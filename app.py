from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import scrape_maps_websites
import scrape_website_emails

app = Flask(__name__)
scraping_state = {
    'businesses': [],
    'email_results': [],
    'current_batch': 0,
    'total_businesses': 0,
    'search_term': '',
    'is_scraping': False,
    'start_idx': 0
}

@app.route('/')
def index():
    """Serve the frontend HTML."""
    print("Serving web interface at http://localhost:5000")
    return render_template('index.html')

@app.route('/start_scrape', methods=['POST'])
def start_scrape():
    """Initialize scraping with the provided search term."""
    search_term = request.json.get('search_term')
    if not search_term:
        print("Error: No search term provided.")
        return jsonify({'error': 'Search term is required'}), 400

    print(f"\n=== Starting Web Scrape for: {search_term} ===")
    try:
        # Reset state
        scraping_state['businesses'] = []
        scraping_state['email_results'] = []
        scraping_state['current_batch'] = 0
        scraping_state['total_businesses'] = 0
        scraping_state['search_term'] = search_term
        scraping_state['is_scraping'] = True
        scraping_state['start_idx'] = 0
        
        # Scrape business names and URLs (batch of 20)
        print(f"Step 1: Scraping business names and URLs (Batch starting from {scraping_state['start_idx']})...")
        businesses = scrape_maps_websites.main(search_term, batch_size=20, start_idx=scraping_state['start_idx'])
        if not businesses:
            print("No businesses found.")
            scraping_state['is_scraping'] = False
            return jsonify({'error': 'No businesses found'}), 400
        
        scraping_state['businesses'] = businesses
        scraping_state['total_businesses'] += len(businesses)
        print(f"Collected {len(businesses)} businesses in this batch.")
        
        # Return businesses for UI editing
        results = [{
            'business_name': name,
            'website': website
        } for name, website in businesses]
        
        return jsonify({
            'status': 'businesses_scraped',
            'message': f'Found {len(businesses)} businesses in batch starting from {scraping_state["start_idx"]}. Edit and save to proceed.',
            'results': results,
            'start_idx': scraping_state['start_idx']
        })
    except Exception as e:
        print(f"Error during initial scrape: {e}")
        scraping_state['is_scraping'] = False
        return jsonify({'error': str(e)}), 500

@app.route('/save_businesses', methods=['POST'])
def save_businesses():
    """Save the updated list of businesses to websites.csv."""
    try:
        updated_businesses = request.json.get('businesses', [])
        businesses = [(item['business_name'], item['website']) for item in updated_businesses]
        scrape_maps_websites.save_to_csv(businesses)
        scraping_state['businesses'] = businesses
        return jsonify({'status': 'saved', 'message': 'Businesses saved to websites.csv. Ready to scrape emails.'})
    except Exception as e:
        print(f"Error saving businesses: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/scrape_emails', methods=['POST'])
def scrape_emails():
    """Scrape emails for the current batch of websites."""
    try:
        businesses = scraping_state['businesses']
        if not businesses:
            print("Error: No businesses to scrape.")
            return jsonify({'error': 'No businesses available'}), 400
        
        print(f"Scraping emails for {len(businesses)} websites...")
        email_results = scrape_website_emails.scrape_email_batch(businesses, start_idx=0, batch_size=20)
        scraping_state['email_results'] = email_results
        
        # Save intermediate results
        scrape_website_emails.save_to_csv(email_results)
        
        results = [{
            'business_name': name,
            'website': website,
            'email': email or 'N/A'
        } for name, website, email in email_results]
        
        return jsonify({
            'status': 'emails_scraped',
            'message': f'Emails scraped for batch. Found {len([r for r in results if r["email"] != "N/A"])} emails. Edit and save to continue.',
            'results': results
        })
    except Exception as e:
        print(f"Error during email scrape: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_emails', methods=['POST'])
def save_emails():
    """Save the updated list of emails to emails.csv."""
    try:
        updated_emails = request.json.get('emails', [])
        email_results = [(item['business_name'], item['website'], item['email'] if item['email'] != 'N/A' else None) for item in updated_emails]
        scrape_website_emails.save_to_csv(email_results)
        scraping_state['email_results'] = email_results
        scraping_state['start_idx'] += 20  # Move to next batch
        return jsonify({
            'status': 'saved',
            'message': f'Emails saved to emails.csv. Ready to scrape next batch starting from {scraping_state["start_idx"]}.'
        })
    except Exception as e:
        print(f"Error saving emails: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop_scrape', methods=['POST'])
def stop_scrape():
    """Stop the current scraping process."""
    try:
        scrape_maps_websites.set_stop_flag()
        scrape_website_emails.set_stop_flag()
        scraping_state['is_scraping'] = False
        print("Scraping stopped by user via stop button.")
        return jsonify({'status': 'stopped', 'message': 'Scraping stopped.'})
    except Exception as e:
        print(f"Error stopping scrape: {e}")
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