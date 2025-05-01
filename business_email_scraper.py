import scrape_maps_websites
import scrape_website_emails

def main():
    """Bridge script to scrape website URLs and emails from Google Maps."""
    print("=== Business Email Scraper ===")
    print("This script searches Google Maps for businesses and extracts emails from their websites.")
    search_term = input("Enter the search term (e.g., dental clinics in London): ").strip()
    if not search_term:
        print("Error: Search term cannot be empty.")
        return
    
    print(f"\nStep 1: Scraping website URLs for '{search_term}' from Google Maps...")
    print("Chrome browser will open visibly to show the process.")
    
    # Run Script 1 to get website URLs
    websites = scrape_maps_websites.main(search_term)
    
    if not websites:
        print("No websites found. Try a broader search term or check internet connection.")
        return
    
    print(f"\nStep 2: Scraping emails from {len(websites)} websites...")
    print("Chrome will visit each website to find emails, prioritizing contact pages.")
    
    # Run Script 2 to get emails
    email_results = scrape_website_emails.main()
    
    print("\n=== Scraping Complete ===")
    if any(email_results.values()):
        print("Final results:")
        email_count = 0
        for website, email in email_results.items():
            if email:
                email_count += 1
                print(f"{website}: {email}")
            else:
                print(f"{website}: No email found")
        print(f"Total emails found: {email_count}")
        print("Results saved to emails.csv")
    else:
        print("No emails found. Websites may not have public emails.")

if __name__ == "__main__":
    main()