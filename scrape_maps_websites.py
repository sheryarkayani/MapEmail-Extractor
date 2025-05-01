import time
import csv
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up visible Chrome driver."""
    print("Initializing Chrome browser (visible mode)...")
    chrome_options = Options()
    # Removed --headless for visible browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        print("Chrome browser opened successfully.")
        return driver
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("Ensure Google Chrome is installed and webdriver-manager is up-to-date.")
        return None

def clean_url(url):
    """Clean URL to remove query strings and fragments."""
    if not url:
        return ""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def scroll_results(driver, scroll_pane_selector, max_time=60):
    """Scroll the results pane to load more businesses."""
    print("Scrolling Google Maps results to load businesses...")
    try:
        scroll_pane = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, scroll_pane_selector))
        )
        start_time = time.time()
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_pane)
        
        while time.time() - start_time < max_time:
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_pane)
            time.sleep(1)  # Reduced for efficiency
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_pane)
            if new_height == last_height:
                print("Reached end of results or no new businesses loaded.")
                break
            last_height = new_height
    except TimeoutException:
        print("Timeout while scrolling results pane. Check internet connection or Google Maps loading.")
    except Exception as e:
        print(f"Error scrolling results: {e}")

def get_business_links(driver, results_selector):
    """Extract links to business details pages."""
    print("Extracting business detail page links...")
    try:
        results = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, results_selector))
        )
        links = []
        for result in results:
            try:
                link = result.get_attribute("href")
                if link and "https://www.google.com/maps/place/" in link:
                    links.append(link)
            except:
                continue
        print(f"Found {len(links)} business links.")
        return links
    except TimeoutException:
        print("Timeout while loading business results. Google Maps may be slow.")
        return []
    except Exception as e:
        print(f"Error extracting business links: {e}")
        return []

def extract_website_url(driver, url):
    """Extract website URL from a business details page."""
    print(f"Visiting business page: {url}")
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        website = ""
        try:
            website_element = driver.find_element(By.CSS_SELECTOR, "a[data-item-id*='authority']")
            website = clean_url(website_element.get_attribute("href"))
            print(f"Found website: {website}")
        except NoSuchElementException:
            print("No website link found on this business page.")
        
        return website
    except TimeoutException:
        print(f"Timeout loading business page: {url}. Page may be slow or unresponsive.")
        return ""
    except Exception as e:
        print(f"Error processing business page {url}: {e}")
        return ""

def save_to_csv(websites, filename="websites.csv"):
    """Save website URLs to a CSV file."""
    print(f"Saving {len(websites)} websites to {filename}...")
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Website'])
            for website in websites:
                if website:
                    writer.writerow([website])
        print(f"Websites successfully saved to {filename}.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        print("Check directory permissions or disk space.")

def scrape_google_maps(search_term, max_time=300):
    """Scrape website URLs from Google Maps, targeting 150 websites."""
    driver = setup_driver()
    if not driver:
        return []

    start_time = time.time()
    websites = set()  # Use set to avoid duplicates
    try:
        print("Navigating to Google Maps...")
        driver.get("https://www.google.com/maps")
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        
        print(f"Searching for: {search_term}")
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)
        
        scroll_pane_selector = "div[role='feed']"
        results_selector = "a[href*='/maps/place/']"
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, scroll_pane_selector))
        )
        
        scroll_results(driver, scroll_pane_selector)
        
        business_links = get_business_links(driver, results_selector)
        
        target_websites = 150
        for i, link in enumerate(business_links, 1):
            if time.time() - start_time > max_time or len(websites) >= target_websites:
                print(f"Stopping scrape: {len(websites)} websites collected or time limit reached.")
                break
            print(f"Processing business {i}/{len(business_links)}...")
            website = extract_website_url(driver, link)
            if website:
                websites.add(website)
        
    except TimeoutException:
        print("Timeout during Google Maps search. Check internet or increase timeout.")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        print("Closing Chrome browser...")
        driver.quit()
    
    websites = list(websites)
    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds. Collected {len(websites)} websites.")
    return websites

def main(search_term):
    """Main function to run the Google Maps scraper."""
    print(f"\n=== Starting Google Maps Scrape for: {search_term} ===")
    websites = scrape_google_maps(search_term)
    if websites:
        print(f"\nFound {len(websites)} unique websites:")
        for i, website in enumerate(websites, 1):
            print(f"{i}. {website}")
        save_to_csv(websites)
    else:
        print("No websites found. Try a different search term or check connectivity.")
    return websites

if __name__ == "__main__":
    search_term = input("Enter the search term (e.g., dental clinics in London): ").strip()
    main(search_term)