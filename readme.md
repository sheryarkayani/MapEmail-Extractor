MapEmail Extractor - Free Google Maps Email Scraper
MapEmail Extractor is a free email scraper designed to extract business names, website URLs, and emails from Google Maps. Ideal for lead generation, this business email extractor targets industries like dental clinics or restaurants in any location (e.g., "dental clinics in London"). With a modern web interface, visible Chrome browser automation, and user-controlled scraping, it collects up to 150 websites to yield 100+ emails, pausing every 30 websites for user permission. Clone this free Google Maps scraper from GitHub for efficient business email scraping!
Why Choose MapEmail Extractor?
MapEmail Extractor is a powerful Google Maps email extractor with:

Free Email Scraper: Open-source tool for business emails.
Google Maps Integration: Scrapes 150+ business names and URLs.
Smart Email Extraction: AI heuristics prioritize contact pages.
Lead Generation Tool: Targets 100+ emails per search.
Visible Automation: Chrome browser shows live scraping.
User-Controlled: Pauses every 30 websites for permission.
Modern UI: Clean design with progress bar and modals.

Key Features

Free Business Email Finder: Collects 100+ emails with business names.
Google Maps Scraper: Extracts business details in ~300 seconds.
Efficient Scraping: Limits website crawling to 10 pages, ~180 seconds each.
CSV Output: Saves websites.csv (names, URLs) and emails.csv (names, URLs, emails).
Ctrl+C Support: Stops scraping gracefully with progress saved.
Batch Processing: Pauses after every 30 websites for user confirmation.
AI Heuristics: Prioritizes high-yield pages for faster results.

Project Structure
scrappro/
├── scrape_maps_websites.py      # Scrapes business names, URLs (visible Chrome)
├── scrape_website_emails.py     # Extracts emails (batch processing)
├── business_email_scraper.py    # Console-based bridge script
├── app.py                      # Flask API with batch scraping
├── templates/
│   └── index.html             # Modern UI with modals
├── static/
│   ├── css/
│   │   └── styles.css        # Custom styles
│   └── js/
│       └── script.js         # Frontend logic
├── requirements.txt            # Dependencies
├── Dockerfile                 # For cloud deployment
├── .gitignore                 # Excludes temporary files
├── websites.csv               # CSV with names, URLs
├── emails.csv                # CSV with names, URLs, emails
└── README.md                  # Documentation

Requirements

Python: 3.6+
Dependencies:
selenium
webdriver-manager
beautifulsoup4
flask
gunicorn


Browser: Google Chrome
System: Linux (tested on Ubuntu), macOS, or Windows

Local Setup Instructions

Clone Repository:
git clone https://github.com/sheryarkayani/MapEmail-Extractor.git
cd MapEmail-Extractor


Install Dependencies:
pip install --upgrade -r requirements.txt

Verify:
pip list


Install Google Chrome:Check:
google-chrome --version

Install (Ubuntu):
sudo apt update
sudo apt install google-chrome-stable


Set Permissions:
chmod u+w .


Create Directories:
mkdir -p templates static/css static/js


Run Locally:
python3 app.py

Open http://localhost:5000.


How to Use MapEmail Extractor
Web Interface

Open: http://localhost:5000.
Enter Search Term: e.g., dental clinics in London.
Start Scraping: Click "Start Scraping", confirm in modal.
Watch Chrome:
Searches Google Maps, collects ~150 businesses.
Scrapes emails in batches of 30 websites.


Batch Permission:
Modal prompts every 30 websites (5 pauses for 150 websites).
Click "Proceed" to continue or "Cancel" to stop.


Monitor Progress:
Console: “Visiting: {url}”, “Found {n} emails”.
UI: Progress bar, messages like “Scraping batch 2...”.


View Results: Table shows business names, websites, emails.
Download CSVs: Get websites.csv and emails.csv.
Stop Scraping: Press Ctrl+C in console to save progress.

Console Mode
python3 business_email_scraper.py


Input search term.
Watch Chrome and console logs.
Stop with Ctrl+C.
Check CSVs for results.

Example Output

Enter: dental clinics in London
Chrome:
Searches Google Maps, visits ~150 businesses.
Scrapes emails, pausing every 30 websites.


UI:
Modal: “Start Scraping?”, “Continue Batch 2?”
Table: Notting Hill Dental, https://..., info@...


CSVs:
websites.csv: ~150 businesses
emails.csv: 100+ emails



CSV File Formats
websites.csv
Business Name,Website
Notting Hill Dental,https://www.nottinghilldentalclinic.com/
Chelsea Dental,https://www.chelseadentalclinic.co.uk/
...

emails.csv
Business Name,Website,Email
Notting Hill Dental,https://www.nottinghilldentalclinic.com/,info@nottinghilldentalclinic.com
Chelsea Dental,https://www.chelseadentalclinic.co.uk/,contact@chelseadentalclinic.co.uk
...

Troubleshooting
Chrome Not Opening

Verify:google-chrome --version


Install:sudo apt install google-chrome-stable


Check:pip show webdriver-manager



No Businesses Found

Test term on Google Maps.
Try dentists in London.

Fewer Than 100 Emails

Check websites.csv for 150+ entries.
Test websites for plain-text emails.
Increase max_time in scrape_website_emails.py.

Timeouts

Reduce WebDriverWait to 3 seconds.
Check internet.

UI Issues

Ensure Flask running (python3 app.py).
Check browser console.

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
Visible browser automation
AI email scraping
User-controlled scraping

Contributing

Fork: https://github.com/sheryarkayani/MapEmail-Extractor.
Branch:git checkout -b feature/new-feature


Commit:git commit -m 'Add new feature'


Push:git push origin feature/new-feature


Open Pull Request.

License
MIT License. See LICENSE.
Contact
Issues? Open an issue on GitHub or contact @sheryarkayani.

Free Google Maps email scraper for lead generation. Features visible browser automation, AI-driven email scraping, and user-controlled batch processing. Last updated: May 1, 2025
