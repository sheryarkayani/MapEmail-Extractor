import scrape_maps_websites
import scrape_website_emails

def main():
    """Bridge script to scrape website URLs and emails from Google Maps."""
    print("=== Business Email Scraper ===")
    search_term = input("Enter the search term (e.g., dental clinics in London): ").strip()
    print(f"\nStep 1: Scraping website URLs for '{search_term}' from Google Maps...")
    
    # Run Script 1 to get website URLs
    websites = scrape_maps_websites.main(search_term)
    
    if not websites:
        print("No websites found. Exiting.")
        return
    
    print(f"\nStep 2: Scraping emails from {len(websites)} websites...")
    
    # Run Script 2 to get emails
    email_results = scrape_website_emails.main()
    
    print("\n=== Scraping Complete ===")
    if any(email_results.values()):
        print("Final results:")
        for website, email in email_results.items():
            print(f"{website}: {email or 'N/A'}")
        print("Results saved to emails.csv")
    else:
        print("No emails found.")

if __name__ == "__main__":
    main()