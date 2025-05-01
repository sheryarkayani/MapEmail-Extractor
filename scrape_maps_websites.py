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

# Global flag to stop scraping
stop_scraping = False

def set_stop_flag():
    """Set the global stop flag to True."""
    global stop_scraping
    stop_scraping = True

def setup_driver():
    """Set up Chrome driver (headless for Render, visible locally)."""
    print("Initializing Chrome browser...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Uncomment for Render deployment
    # chrome_options.add_argument("--headless")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.maximize_window()
        print("Chrome browser opened successfully.")
        return driver
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        return None

def clean_url(url):
    """Clean URL to remove query strings and fragments."""
    if not url:
        return ""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

def is_facebook_url(url):
    """Check if the URL is a Facebook link."""
    return "facebook.com" in url.lower()

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
            if stop_scraping:
                print("Stopping scroll due to user request.")
                break
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_pane)
            time.sleep(1)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_pane)
            if new_height == last_height:
                print("Reached end of results or no new businesses loaded.")
                break
            last_height = new_height
    except TimeoutException:
        print("Timeout while scrolling results pane.")
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
            if stop_scraping:
                print("Stopping link extraction due to user request.")
                break
            try:
                link = result.get_attribute("href")
                if link and "https://www.google.com/maps/place/" in link:
                    links.append(link)
            except:
                continue
        print(f"Found {len(links)} business links.")
        return links
    except TimeoutException:
        print("Timeout while loading business results.")
        return []
    except Exception as e:
        print(f"Error extracting business links: {e}")
        return []

def extract_business_info(driver, url):
    """Extract business name and website URL from a business details page."""
    if stop_scraping:
        print("Stopping business info extraction due to user request.")
        return "", ""
    
    print(f"Visiting business page: {url}")
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Extract business name
        business_name = ""
        try:
            name_element = driver.find_element(By.TAG_NAME, "h1")
            business_name = name_element.text.strip()
            print(f"Business name: {business_name}")
        except NoSuchElementException:
            print("No business name found.")
        
        # Extract website
        website = ""
        try:
            website_element = driver.find_element(By.CSS_SELECTOR, "a[data-item-id*='authority']")
            website = clean_url(website_element.get_attribute("href"))
            if is_facebook_url(website):
                print("Skipping Facebook URL.")
                website = ""
            else:
                print(f"Found website: {website}")
        except NoSuchElementException:
            print("No website link found.")
        
        return business_name, website
    except TimeoutException:
        print(f"Timeout loading business page: {url}.")
        return "", ""
    except Exception as e:
        print(f"Error processing business page {url}: {e}")
        return "", ""

def save_to_csv(businesses, filename="websites.csv"):
    """Save business names and website URLs to a CSV file."""
    print(f"Saving {len(businesses)} businesses to {filename}...")
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Business Name', 'Website'])
            for name, website in businesses:
                if website:
                    writer.writerow([name, website])
        print(f"Businesses successfully saved to {filename}.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def scrape_google_maps(search_term, max_time=300, batch_size=20, start_idx=0):
    """Scrape business names and website URLs from Google Maps in batches."""
    global stop_scraping
    stop_scraping = False
    driver = setup_driver()
    if not driver:
        return []

    start_time = time.time()
    businesses = set()  # (name, website)
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
        
        target_websites = batch_size
        current_idx = 0
        for i, link in enumerate(business_links, 1):
            if current_idx < start_idx:
                current_idx += 1
                continue
            if stop_scraping:
                print("Scraping stopped by user.")
                break
            if time.time() - start_time > max_time or len(businesses) >= target_websites:
                print(f"Stopping scrape: {len(businesses)} websites collected or time limit reached.")
                break
            print(f"Processing business {i}/{len(business_links)}...")
            name, website = extract_business_info(driver, link)
            if website:
                businesses.add((name, website))
        
    except KeyboardInterrupt:
        print("\nUser interrupted scraping (Ctrl+C). Saving progress...")
        save_to_csv(businesses)
        raise
    except TimeoutException:
        print("Timeout during Google Maps search.")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        print("Closing Chrome browser...")
        try:
            driver.quit()
        except:
            pass
    
    businesses = list(businesses)
    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds. Collected {len(businesses)} businesses.")
    return businesses

def main(search_term, batch_size=20, start_idx=0):
    """Main function to run the Google Maps scraper."""
    print(f"\n=== Starting Google Maps Scrape for: {search_term} (Batch starting from {start_idx}) ===")
    try:
        businesses = scrape_google_maps(search_term, batch_size=batch_size, start_idx=start_idx)
        if businesses:
            print(f"\nFound {len(businesses)} unique businesses:")
            for i, (name, website) in enumerate(businesses, 1):
                print(f"{i}. {name}: {website}")
            save_to_csv(businesses)
        else:
            print("No businesses found.")
        return businesses
    except KeyboardInterrupt:
        print("\nScraping stopped by user.")
        return []

if __name__ == "__main__":
    search_term = input("Enter the search term (e.g., dental clinics in London): ").strip()
    main(search_term)