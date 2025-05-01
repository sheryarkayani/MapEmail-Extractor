import scrape_maps_websites
import scrape_website_emails

def main():
    """Bridge script to scrape business names, URLs, and emails from Google Maps."""
    print("=== Business Email Scraper ===")
    print("This script searches Google Maps for businesses and extracts emails in batches of 20.")
    print("Press Ctrl+C to stop scraping at any time.")
    search_term = input("Enter the search term (e.g., dental clinics in London): ").strip()
    if not search_term:
        print("Error: Search term cannot be empty.")
        return
    
    batch_size = 20
    start_idx = 0
    while True:
        print(f"\nStep 1: Scraping business names and URLs for '{search_term}' (Batch starting from {start_idx})...")
        try:
            businesses = scrape_maps_websites.main(search_term, batch_size=batch_size, start_idx=start_idx)
        except KeyboardInterrupt:
            print("\nScraping stopped by user.")
            return
        
        if not businesses:
            print("No businesses found.")
            return
        
        print(f"\nStep 2: Scraping emails from {len(businesses)} websites...")
        try:
            email_results = scrape_website_emails.main()
        except KeyboardInterrupt:
            print("\nScraping stopped by user.")
            return
        
        print("\n=== Batch Complete ===")
        if any(email for _, _, email in email_results):
            print("Batch results:")
            email_count = 0
            for name, website, email in email_results:
                if email:
                    email_count += 1
                    print(f"{name} ({website}): {email}")
                else:
                    print(f"{name} ({website}): No email found")
            print(f"Total emails found in batch: {email_count}")
            print("Results saved to emails.csv")
        else:
            print("No emails found in this batch.")
        
        # Ask user if they want to continue
        continue_scraping = input("\nDo you want to scrape the next batch? (y/n): ").strip().lower()
        if continue_scraping != 'y':
            print("Scraping stopped by user.")
            break
        start_idx += batch_size

if __name__ == "__main__":
    main()