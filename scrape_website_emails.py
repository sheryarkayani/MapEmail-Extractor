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

def is_priority_page(url, page_source):
    """Check if the page is likely to contain contact information."""
    priority_keywords = [
        'contact', 'about', 'team', 'support', 'get-in-touch', 'reach-us',
        'services', 'our-practice', 'staff', 'location', 'info'
    ]
    url_lower = url.lower()
    if any(keyword in url_lower for keyword in priority_keywords):
        return True
    
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        title = soup.title.string.lower() if soup.title else ''
        return any(keyword in title for keyword in priority_keywords)
    except:
        return False

def is_irrelevant_page(url):
    """Check if the page is likely irrelevant (e.g., news, blog, privacy)."""
    irrelevant_keywords = [
        'news', 'blog', 'post', 'privacy', 'policy', 'terms', 'conditions',
        'cookie', 'archive', 'category', 'tag', '.pdf'
    ]
    url_lower = url.lower()
    return any(keyword in url_lower for keyword in irrelevant_keywords)

def extract_emails(text):
    """Extract and validate email addresses from text."""
    email_pattern = r'[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set(re.findall(email_pattern, text))
    return {email for email in emails if is_valid_email(email)}

def get_footer_emails(soup):
    """Extract emails specifically from footer sections."""
    emails = set()
    footer_selectors = [
        'footer',
        '[class*="footer"]',
        '[id*="footer"]',
        '.site-footer',
        '.footer-content',
        '.footer-section'
    ]
    
    for selector in footer_selectors:
        try:
            footers = soup.select(selector)
            for footer in footers:
                footer_text = re.sub(r'\s+', ' ', footer.get_text())
                emails.update(extract_emails(footer_text))
        except:
            continue
    return emails

def get_page_links(driver, url, visited, domain):
    """Extract links from a webpage that belong to the same domain."""
    links = set()
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(url, href)
            parsed_url = urlparse(absolute_url)
            
            if parsed_url.netloc == domain and clean_url(absolute_url) not in visited:
                links.add(clean_url(absolute_url))
    except TimeoutException:
        print(f"Timeout loading {url}")
    except Exception as e:
        print(f"Error accessing {url}: {e}")
    return links

def scrape_emails(website_url, max_time=120):
    """Scrape one email from a website, prioritizing contact pages and footers."""
    start_time = time.time()
    website_url = normalize_url(website_url)
    if not is_valid_url(website_url):
        print(f"Invalid URL after normalization: {website_url}")
        return None

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        return None

    visited = set()
    to_visit = {clean_url(website_url)}
    priority_urls = set()
    emails = set()
    domain = urlparse(website_url).netloc
    
    try:
        print("Phase 1: Checking priority pages (e.g., Contact Us) and footers")
        while to_visit and (time.time() - start_time) < max_time:
            url = to_visit.pop()
            if url in visited or is_irrelevant_page(url):
                continue
                
            print(f"Checking: {url}")
            visited.add(url)
            
            try:
                driver.get(url)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                if is_priority_page(url, page_source):
                    print(f"Scraping priority page: {url}")
                    priority_urls.add(url)
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
                
                if url == clean_url(website_url):
                    footer_emails = get_footer_emails(soup)
                    if footer_emails:
                        print(f"Found {len(footer_emails)} emails in homepage footer")
                        emails.update(footer_emails)
                    
                    if emails:
                        print("Emails found, stopping search.")
                        break
                
                new_links = get_page_links(driver, url, visited, domain)
                to_visit.update(new_links - visited)
                
            except TimeoutException:
                print(f"Timeout loading {url}")
            except Exception as e:
                print(f"Error processing {url}: {e}")
        
        if not emails:
            print("Phase 2: No emails found in priority pages, scanning other pages")
            to_visit = {url for url in to_visit if not is_irrelevant_page(url)}
            visited.clear()
            while to_visit and (time.time() - start_time) < max_time:
                url = to_visit.pop()
                if url in visited or is_irrelevant_page(url):
                    continue
                    
                print(f"Scraping: {url}")
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
                    to_visit.update(new_links - visited)
                    
                except TimeoutException:
                    print(f"Timeout loading {url}")
                except Exception as e:
                    print(f"Error processing {url}: {e}")
                
    finally:
        driver.quit()
    
    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds")
    # Return the first email found (or None if none)
    return next(iter(emails)) if emails else None

def read_websites_csv(filename="websites.csv"):
    """Read website URLs from CSV."""
    websites = []
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header
            for row in reader:
                if row and row[0]:
                    websites.append(row[0])
        print(f"Read {len(websites)} websites from {filename}")
    except FileNotFoundError:
        print(f"Error: {filename} not found")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return websites

def save_to_csv(emails, filename="emails.csv"):
    """Save emails to a CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Website', 'Email'])
            for website, email in emails.items():
                writer.writerow([website, email or 'N/A'])
        print(f"Emails saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main(websites_csv="websites.csv"):
    """Main function to scrape emails from websites in CSV."""
    websites = read_websites_csv(websites_csv)
    if not websites:
        print("No websites to process.")
        return {}
    
    email_results = {}
    for i, website in enumerate(websites, 1):
        print(f"\nProcessing website {i}/{len(websites)}: {website}")
        email = scrape_emails(website)
        email_results[website] = email
    
    if any(email_results.values()):
        print("\nFound emails:")
        for website, email in email_results.items():
            if email:
                print(f"{website}: {email}")
        save_to_csv(email_results)
    else:
        print("No emails found.")
    return email_results

if __name__ == "__main__":
    main()