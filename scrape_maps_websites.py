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
    """Set up headless Chrome driver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
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

def scroll_results(driver, scroll_pane_selector, max_time=30):
    """Scroll the results pane to load all businesses."""
    try:
        scroll_pane = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, scroll_pane_selector))
        )
        start_time = time.time()
        last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_pane)
        
        while time.time() - start_time < max_time:
            driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scroll_pane)
            time.sleep(2)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_pane)
            if new_height == last_height:
                break
            last_height = new_height
    except TimeoutException:
        print("Timeout while scrolling results pane")
    except Exception as e:
        print(f"Error scrolling results: {e}")

def get_business_links(driver, results_selector):
    """Extract links to business details pages."""
    try:
        results = WebDriverWait(driver, 10).until(
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
        return links
    except TimeoutException:
        print("Timeout while loading business results")
        return []
    except Exception as e:
        print(f"Error extracting business links: {e}")
        return []

def extract_website_url(driver, url):
    """Extract website URL from a business details page."""
    try:
        driver.get(url)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        website = ""
        try:
            website_element = driver.find_element(By.CSS_SELECTOR, "a[data-item-id*='authority']")
            website = clean_url(website_element.get_attribute("href"))
        except NoSuchElementException:
            print(f"No website found for {url}")
        
        return website
    except TimeoutException:
        print(f"Timeout loading business page: {url}")
        return ""
    except Exception as e:
        print(f"Error processing business page {url}: {e}")
        return ""

def save_to_csv(websites, filename="websites.csv"):
    """Save website URLs to a CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Website'])
            for website in websites:
                if website:  # Only save non-empty URLs
                    writer.writerow([website])
        print(f"Websites saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def scrape_google_maps(search_term, max_time=120):
    """Scrape website URLs from Google Maps."""
    driver = setup_driver()
    if not driver:
        return []

    start_time = time.time()
    websites = []
    try:
        driver.get("https://www.google.com/maps")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        
        search_box = driver.find_element(By.ID, "searchboxinput")
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)
        
        scroll_pane_selector = "div[role='feed']"
        results_selector = "a[href*='/maps/place/']"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, scroll_pane_selector))
        )
        
        print("Scrolling through search results...")
        scroll_results(driver, scroll_pane_selector, max_time=30)
        
        print("Extracting business links...")
        business_links = get_business_links(driver, results_selector)
        print(f"Found {len(business_links)} businesses")
        
        for i, link in enumerate(business_links, 1):
            if time.time() - start_time > max_time:
                print("Time limit reached, stopping scrape")
                break
            print(f"Processing business {i}/{len(business_links)}: {link}")
            website = extract_website_url(driver, link)
            if website:
                websites.append(website)
        
    except TimeoutException:
        print("Timeout during Google Maps search")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()
    
    elapsed_time = time.time() - start_time
    print(f"Scraping completed in {elapsed_time:.2f} seconds")
    return websites

def main(search_term):
    """Main function to run the Google Maps scraper."""
    print(f"Starting Google Maps scrape for: {search_term}")
    websites = scrape_google_maps(search_term)
    if websites:
        print(f"Found {len(websites)} websites:")
        for website in websites:
            print(website)
        save_to_csv(websites)
    else:
        print("No websites found.")
    return websites

if __name__ == "__main__":
    search_term = input("Enter the search term (e.g., dental clinics in London): ").strip()
    main(search_term)