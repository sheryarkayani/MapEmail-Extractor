document.getElementById('scrapeBtn').addEventListener('click', async () => {
    const searchTerm = document.getElementById('searchTerm').value.trim();
    if (!searchTerm) {
        alert('Please enter a search term (e.g., dental clinics in London).');
        return;
    }

    // Show progress
    const progressDiv = document.getElementById('progress');
    const progressText = document.getElementById('progressText');
    const resultsDiv = document.getElementById('results');
    const resultsTable = document.getElementById('resultsTable');
    const scrapeBtn = document.getElementById('scrapeBtn');
    progressDiv.classList.remove('d-none');
    resultsDiv.classList.add('d-none');
    resultsTable.innerHTML = '';
    scrapeBtn.disabled = true;
    progressText.textContent = `Starting scrape for "${searchTerm}"... Opening Chrome browser...`;

    try {
        // Call the scrape API
        const response = await fetch('/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ search_term: searchTerm })
        });
        const data = await response.json();

        if (data.error) {
            progressDiv.classList.remove('alert-info');
            progressDiv.classList.add('alert-danger');
            progressText.textContent = `Error: ${data.error}. Check console for details.`;
            return;
        }

        // Update progress
        progressText.textContent = 'Scraping website URLs from Google Maps (watch Chrome browser)...';
        setTimeout(() => {
            progressText.textContent = 'Extracting emails from websites (watch Chrome browser)...';
        }, 150000);  // Approximate time for website scraping
        setTimeout(() => {
            progressText.textContent = `Scraping complete! Found ${data.results.filter(r => r.email !== 'N/A').length} emails.`;
            progressDiv.classList.remove('alert-info');
            progressDiv.classList.add('alert-success');

            // Display results
            resultsDiv.classList.remove('d-none');
            data.results.forEach((result, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${result.website}</td>
                    <td>${result.email || 'N/A'}</td>
                `;
                resultsTable.appendChild(row);
            });

            // Show download buttons
            const downloadWebsites = document.getElementById('downloadWebsites');
            const downloadEmails = document.getElementById('downloadEmails');
            downloadWebsites.href = data.websites_csv;
            downloadEmails.href = data.emails_csv;
            downloadWebsites.classList.remove('d-none');
            downloadEmails.classList.remove('d-none');
        }, 300000);  // Approximate total scraping time

    } catch (error) {
        progressDiv.classList.remove('alert-info');
        progressDiv.classList.add('alert-danger');
        progressText.textContent = `Error: ${error.message}. Check console or try again.`;
    } finally {
        scrapeBtn.disabled = false;
    }
});