from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import os
import csv
import scrape_maps_websites
import scrape_website_emails

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the frontend HTML."""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Run the scraper with the provided search term."""
    search_term = request.json.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400

    try:
        # Run Google Maps scraper
        print(f"Scraping websites for: {search_term}")
        scrape_maps_websites.main(search_term)

        # Run email scraper
        print(f"Scraping emails from websites")
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

        return jsonify({
            'status': 'success',
            'results': results,
            'websites_csv': '/download/websites.csv',
            'emails_csv': '/download/emails.csv'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve CSV files for download."""
    if filename not in ['websites.csv', 'emails.csv']:
        return jsonify({'error': 'Invalid file'}), 400
    if not os.path.exists(filename):
        return jsonify({'error': f'{filename} not found'}), 404
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)