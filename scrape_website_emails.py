import re
import time
import csv
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# Global stop flag (shared with scrape_maps_websites)
stop_scraping = False

def set_stop_flag():
    """Set the global stop flag to True."""
    global stop_scraping
    stop_scraping = True

def normalize_url(url):
    """Ensure URL has a protocol; default to https if none provided."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.strip()

def is_valid_url(url):
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def clean_url(url):
    """Remove fragments and query strings to avoid duplicate URLs."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def is_valid_email(email):
    """Validate email format to ensure it's realistic."""
    pattern = r'^[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def score_page(url, page_source):
    """AI-inspired heuristic to score page likelihood of containing emails."""
    score = 0
    priority_keywords = {
        'contact': 50, 'about': 30, 'team': 20, 'support': 20, 'get-in-touch': 40,
        'reach-us': 40, 'services': 15, 'our-practice': 15, 'staff': 20, 'location': 10, 'info': 10
    }
    irrelevant_keywords = ['news', 'blog', 'post', 'privacy', 'policy', 'terms', 'conditions', 'cookie', 'archive', 'category', 'tag', '.pdf']
    
    url_lower = url.lower()
    for keyword, weight in priority_keywords.items():
        if keyword in url_lower:
            score += weight
    
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        title = soup.title.string.lower() if soup.title else ''
        for keyword, weight in priority_keywords.items():
            if keyword in title:
                score += weight // 2
    except:
        pass
    
    for keyword in irrelevant_keywords:
        if keyword in url_lower:
            score -= 100
    
    return score

def is_irrelevant_page(url):
    """Check if the page is likely irrelevant."""
    irrelevant_keywords = ['news', 'blog', 'post', 'privacy', 'policy', 'terms', 'conditions', 'cookie', 'archive', 'category', 'tag', '.pdf']
    url_lower = url.lower()
    return any(keyword in url_lower for keyword in irrelevant_keywords)

def extract_emails(text):
    """Extract and validate email addresses from text."""
    email_pattern = r'[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_pattern, text))
    return {email for email in emails if is_valid_email(email)}

def get_footer_emails(soup):
    """Extract emails from footer sections."""
    emails = set()
    footer_selectors = ['footer', '[class*="footer"]', '[id*="footer"]', '.site-footer', '.footer-content', '.footer-section']
    
    for selector in footer_selectors:
        try:
            footers = soup.select(selector)
            for footer in footers:
                footer_text = re.sub(r'\s+', ' ', footer.get_text())
                emails.update(extract_emails(footer_text))
        except:
            continue
    return emails

def get_page_links(driver, url, visited, domain, max_links=10):
    """Extract up to max_links from a webpage in the same domain."""
    if stop_scraping:
        print("Stopping link extraction due to user request.")
        return set()
    
    links = set()
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            if stop_scraping:
                break
            href = a_tag['href']
            absolute_url = urljoin(url, href)
            parsed_url = urlparse(absolute_url)
            
            if parsed_url.netloc == domain and clean_url(absolute_url) not in visited:
                links.add(clean_url(absolute_url))
            if len(links) >= max_links:
                break
    except TimeoutException:
        print(f"Timeout loading {url}")
    except Exception as e:
        print(f"Error accessing {url}: {e}")
    return links

def scrape_emails(website_url, max_time=180):
    """Scrape one email from a website using AI-inspired prioritization."""
    global stop_scraping
    start_time = time.time()
    website_url = normalize_url(website_url)
    if not is_valid_url(website_url):
        print(f"Invalid URL: {website_url}")
        return None

    print(f"Initializing Chrome for {website_url}...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Uncomment for Render deployment
    # chrome_options.add_argument("--headless")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        print("Chrome browser opened.")
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        return None

    visited = set()
    to_visit = [(clean_url(website_url), 0)]
    emails = set()
    domain = urlparse(website_url).netloc
    max_pages = 10
    
    try:
        print("Phase 1: Checking high-priority pages...")
        while to_visit and (time.time() - start_time) < max_time and len(visited) < max_pages:
            if stop_scraping:
                print("Scraping stopped by user.")
                break
            to_visit.sort(key=lambda x: x[1], reverse=True)
            url, _ = to_visit.pop(0)
            if url in visited or is_irrelevant_page(url):
                continue
                
            print(f"Visiting: {url}")
            visited.add(url)
            
            try:
                driver.get(url)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                page_score = score_page(url, page_source)
                print(f"Page score: {page_score}")
                
                page_emails = extract_emails(page_source)
                if page_emails:
                    print(f"Found {len(page_emails)} emails on {url}")
                    emails.update(page_emails)
                
                footer_emails = get_footer_emails(soup)
                if footer_emails:
                    print(f"Found {len(footer_emails)} emails in footer of {url}")
                    emails.update(footer_emails)
                
                if emails:
                    print("Emails found, stopping search.")
                    break
                
                new_links = get_page_links(driver, url, visited, domain)
                for link in new_links:
                    link_score = score_page(link, "")
                    to_visit.append((link, link_score))
                
            except TimeoutException:
                print(f"Timeout loading {url}.")
            except Exception as e:
                print(f"Error processing {url}: {e}")
        
        if not emails:
            print("Phase 2: Scanning additional pages...")
            to_visit = [(url, score_page(url, "")) for url in to_visit if not is_irrelevant_page(url)]
            visited.clear()
            while to_visit and (time.time() - start_time) < max_time and len(visited) < max_pages:
                if stop_scraping:
                    print("Scraping stopped by user.")
                    break
                to_visit.sort(key=lambda x: x[1], reverse=True)
                url, _ = to_visit.pop(0)
                if url in visited or is_irrelevant_page(url):
                    continue
                    
                print(f"Visiting: {url}")
                visited.add(url)
                
                try:
                    driver.get(url)
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    page_emails = extract_emails(page_source)
                    if page_emails:
                        print(f"Found {len(page_emails)} emails on {url}")
                        emails.update(page_emails)
                    
                    footer_emails = get_footer_emails(soup)
                    if footer_emails:
                        print(f"Found {len(footer_emails)} emails in footer of {url}")
                        emails.update(footer_emails)
                    
                    if emails:
                        print("Emails found, stopping search.")
                        break
                    
                    new_links = get_page_links(driver, url, visited, domain)
                    for link in new_links:
                        link_score = score_page(link, "")
                        to_visit.append((link, link_score))
                    
                except TimeoutException:
                    print(f"Timeout loading {url}")
                except Exception as e:
                    print(f"Error processing {url}: {e}")
                
    except KeyboardInterrupt:
        print("\nUser interrupted email scraping (Ctrl+C).")
        raise
    finally:
        print("Closing Chrome browser...")
        try:
            driver.quit()
        except:
            pass
    
    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds. Found {len(emails)} emails.")
    return next(iter(emails)) if emails else None

def read_websites_csv(filename="websites.csv"):
    """Read business names and website URLs from CSV."""
    print(f"Reading businesses from {filename}...")
    businesses = []
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                if row and len(row) >= 2 and row[1]:
                    businesses.append((row[0], row[1]))
        print(f"Read {len(businesses)} businesses.")
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return businesses

def save_to_csv(email_results, filename="emails.csv"):
    """Save business names, websites, and emails to a CSV file."""
    print(f"Saving emails to {filename}...")
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Business Name', 'Website', 'Email'])
            for name, website, email in email_results:
                writer.writerow([name, website, email or 'N/A'])
        print(f"Emails successfully saved to {filename}.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main(websites_csv="websites.csv"):
    """Main function to scrape emails from websites in CSV."""
    businesses = read_websites_csv(websites_csv)
    if not businesses:
        print("No businesses to process.")
        return []
    
    email_results = []
    target_emails = 100
    for i, (name, website) in enumerate(businesses, 1):
        if stop_scraping:
            print("Scraping stopped by user.")
            break
        if sum(1 for _, _, email in email_results if email) >= target_emails:
            print(f"Reached target of {target_emails} emails, stopping.")
            break
        print(f"\nProcessing website {i}/{len(businesses)}: {website} ({name})")
        try:
            email = scrape_emails(website)
            email_results.append((name, website, email))
        except KeyboardInterrupt:
            print("\nSaving partial email results...")
            save_to_csv(email_results)
            raise
    
    if any(email for _, _, email in email_results):
        print("\nFound emails:")
        email_count = 0
        for name, website, email in email_results:
            if email:
                email_count += 1
                print(f"{name} ({website}): {email}")
        print(f"Total emails found: {email_count}")
        save_to_csv(email_results)
    else:
        print("No emails found.")
    return email_results

def scrape_email_batch(businesses, start_idx, batch_size=20):
    """Scrape emails for a batch of websites."""
    global stop_scraping
    email_results = []
    end_idx = min(start_idx + batch_size, len(businesses))
    target_emails = 100
    
    for i in range(start_idx, end_idx):
        if stop_scraping:
            print("Scraping stopped by user.")
            break
        if sum(1 for _, _, email in email_results if email) >= target_emails:
            print(f"Reached target of {target_emails} emails, stopping batch.")
            break
        name, website = businesses[i]
        print(f"\nProcessing website {i+1}/{len(businesses)}: {website} ({name})")
        try:
            email = scrape_emails(website)
            email_results.append((name, website, email))
        except KeyboardInterrupt:
            print("\nSaving partial batch results...")
            save_to_csv(email_results)
            raise
    return email_results

if __name__ == "__main__":
    main()