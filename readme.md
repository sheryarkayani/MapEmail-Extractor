MapEmail Extractor - Free Google Maps Email Scraper
MapEmail Extractor is a free email scraper designed to extract business website URLs and emails from Google Maps. Perfect for lead generation, this business email extractor targets industries like dental clinics, restaurants, or any business type in any location (e.g., "dental clinics in London"). With a user-friendly web interface, it scrapes website URLs, extracts one email per website from pages like "Contact Us" or footers, and saves results to CSV files. Clone this free Google Maps scraper from GitHub for fast, automated business email scraping!
Why Choose MapEmail Extractor?
MapEmail Extractor is a powerful Google Maps email extractor that simplifies business email finding. Here’s why it stands out:

Free Email Scraper: Open-source, no-cost tool for extracting business emails.
Google Maps Integration: Scrapes website URLs directly from Google Maps search results.
Smart Email Extraction: Prioritizes "Contact Us," "About," and footer sections for accurate email scraping.
Lead Generation Tool: Ideal for marketers targeting dental clinics, restaurants, or local businesses.
SEO-Optimized Crawling: Skips irrelevant pages (e.g., news, privacy policies) for faster results.
Web Interface: Responsive frontend for easy input and result viewing.

Key Features

Free Business Email Finder: Extracts one valid email per website for high-quality leads.
Google Maps Scraper: Pulls website URLs for businesses in any city or region.
Efficient Scraping: Limits each website scrape to 120 seconds, avoiding irrelevant pages.
CSV Output: Generates websites.csv (URLs) and emails.csv (website-email pairs).
Headless Chrome: Uses Selenium for fast, automated browsing.
Flask API: Powers the web interface with a lightweight backend.

Project Structure
scrappro/
├── scrape_maps_websites.py      # Free Google Maps scraper for website URLs
├── scrape_website_emails.py     # Business email extractor for websites
├── business_email_scraper.py    # Bridges scripts for email scraping
├── app.py                      # Flask API for web interface
├── templates/
│   └── index.html             # Frontend HTML
├── static/
│   ├── css/
│   │   └── styles.css        # Custom CSS
│   └── js/
│       └── script.js         # JavaScript for frontend
├── websites.csv               # Intermediate CSV with website URLs
├── emails.csv                # Final CSV with website URLs and emails
└── README.md                  # Documentation for the free email scraper

Requirements
To run this free Google Maps email scraper, ensure the following:

Python: Version 3.6 or higher
Dependencies:
selenium
webdriver-manager
beautifulsoup4
flask


Browser: Google Chrome
System: Linux (tested on Ubuntu), macOS, or Windows

Setup Instructions
Follow these steps to set up MapEmail Extractor for business email scraping:
1. Clone the Repository
Clone the project from GitHub:
git clone https://github.com/sheryarkayani/MapEmail-Extractor.git
cd MapEmail-Extractor

2. Install Dependencies
Install required Python packages:
pip install --upgrade selenium webdriver-manager beautifulsoup4 flask

Verify installation:
pip list

Ensure selenium, webdriver-manager, beautifulsoup4, and flask are listed.
3. Install Google Chrome
Check Chrome version:
google-chrome --version

Install or update (Ubuntu example):
sudo apt update
sudo apt install google-chrome-stable

4. Verify Directory Permissions
Ensure write access for CSV output:
chmod u+w .

5. Create Directory Structure
Create the following directories:
mkdir -p templates static/css static/js

Verify all files are present:

scrape_maps_websites.py
scrape_website_emails.py
business_email_scraper.py
app.py
templates/index.html
static/css/styles.css
static/js/script.js

How to Use MapEmail Extractor
1. Start the Web Application
Run the Flask app:
python3 app.py

Open your browser and navigate to:
http://localhost:5000

2. Use the Web Interface

Enter Search Term: Input a term like dental clinics in London.
Start Scraping: Click the "Start Scraping" button.
View Results: See website URLs and emails in a table.
Download CSVs: Download websites.csv and emails.csv using the provided buttons.

3. Check Output Files

websites.csv: Contains website URLs (e.g., https://www.chelseadentalclinic.co.uk/).
emails.csv: Lists website-email pairs (e.g., https://www.chelseadentalclinic.co.uk/,contact@chelseadentalclinic.co.uk).

Example Output
Below is a sample interaction with the Google Maps email extractor web interface:

Enter: dental clinics in London
Progress: "Scraping website URLs from Google Maps..." then "Extracting emails from websites..."
Results (displayed in table):Website: https://www.nottinghilldentalclinic.com/, Email: info@nottinghilldentalclinic.com
Website: https://www.chelseadentalclinic.co.uk/, Email: contact@chelseadentalclinic.co.uk
...


Download: Click buttons to download websites.csv and emails.csv.

CSV File Formats
websites.csv
Website
https://www.nottinghilldentalclinic.com/
https://www.chelseadentalclinic.co.uk/
...

emails.csv
Website,Email
https://www.nottinghilldentalclinic.com/,info@nottinghilldentalclinic.com
https://www.chelseadentalclinic.co.uk/,contact@chelseadentalclinic.co.uk
...

Troubleshooting
No Websites Found

Verify internet connectivity.
Test the search term on Google Maps (e.g., try "dentists in London").
Ensure Google Maps loads correctly in a browser.

No Emails Found

Some websites may hide emails in images or JavaScript. Test with a known site like https://www.talbotplacedental.co.uk/.
Check websites.csv for valid URLs.

Timeouts

Reduce WebDriverWait from 10 to 5 seconds in scrape_maps_websites.py or scrape_website_emails.py.
Share console output for debugging.

CSV Issues

Ensure write permissions:ls -l
chmod u+w .


Verify websites.csv exists before email scraping.

Web Interface Issues

Ensure Flask is running (python3 app.py).
Check browser console for JavaScript errors.
Verify templates/ and static/ directories exist.

SEO-Optimized Keywords

Free email scraper
Google Maps email extractor
Business email finder
Dental clinics email scraper
Free Google Maps scraper
Lead generation tool
Business email extractor
Website email scraper
Email finder for marketing
Local business email scraper

Contributing to MapEmail Extractor
We welcome contributions to enhance this free email scraper! To contribute:

Fork the repository: https://github.com/sheryarkayani/MapEmail-Extractor.
Create a feature branch:git checkout -b feature/new-feature


Commit changes:git commit -m 'Add new feature'


Push to the branch:git push origin feature/new-feature


Open a Pull Request on GitHub.

License
This project is licensed under the MIT License. See the LICENSE file for details.
Contact
For issues, feature requests, or questions, open an issue on GitHub or contact the maintainer (@sheryarkayani).

Free Google Maps email scraper for lead generation. Built to empower marketers and developers with efficient business email scraping. Last updated: May 1, 2025
