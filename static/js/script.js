document.getElementById('scrapeBtn').addEventListener('click', async () => {
    const searchTerm = document.getElementById('searchTerm').value.trim();
    if (!searchTerm) {
        alert('Please enter a search term.');
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
    progressText.textContent = 'Scraping website URLs from Google Maps...';

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
            progressText.textContent = `Error: ${data.error}`;
            return;
        }

        // Update progress
        progressText.textContent = 'Extracting emails from websites...';
        setTimeout(() => {
            progressText.textContent = 'Scraping complete!';
            progressDiv.classList.remove('alert-info');
            progressDiv.classList.add('alert-success');

            // Display results
            resultsDiv.classList.remove('d-none');
            data.results.forEach(result => {
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
        }, 1000);

    } catch (error) {
        progressDiv.classList.remove('alert-info');
        progressDiv.classList.add('alert-danger');
        progressText.textContent = `Error: ${error.message}`;
    } finally {
        scrapeBtn.disabled = false;
    }
});