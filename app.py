from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import scrape_maps_websites
import scrape_website_emails

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the frontend HTML."""
    print("Serving web interface at http://localhost:5000")
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Run the scraper with the provided search term."""
    search_term = request.json.get('search_term')
    if not search_term:
        print("Error: No search term provided.")
        return jsonify({'error': 'Search term is required'}), 400

    print(f"\n=== Starting Web Scrape for: {search_term} ===")
    print("Step 1: Scraping website URLs from Google Maps (visible Chrome)...")
    try:
        # Run Google Maps scraper
        websites = scrape_maps_websites.main(search_term)
        if not websites:
            print("No websites found. Check search term or connectivity.")
            return jsonify({'error': 'No websites found'}), 400

        print(f"Step 2: Scraping emails from {len(websites)} websites (visible Chrome)...")
        # Run email scraper
        email_results = scrape_website_emails.main()

        # Read results from emails.csv
        results = []
        if os.path.exists('emails.csv'):
            with open('emails.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    results.append({
                        'website': row['Website'],
                        'email': row['Email']
                    })

        print(f"Scraping complete. Found {len([r for r in results if r['email'] != 'N/A'])} emails.")
        return jsonify({
            'status': 'success',
            'results': results,
            'websites_csv': '/download/websites.csv',
            'emails_csv': '/download/emails.csv'
        })

    except Exception as e:
        print(f"Error during scraping: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve CSV files for download."""
    if filename not in ['websites.csv', 'emails.csv']:
        print(f"Error: Invalid file requested: {filename}")
        return jsonify({'error': 'Invalid file'}), 400
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return jsonify({'error': f'{filename} not found'}), 404
    print(f"Downloading {filename}...")
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    print("Starting Flask server for MapEmail Extractor...")
    app.run(debug=True, host='0.0.0.0', port=5000)