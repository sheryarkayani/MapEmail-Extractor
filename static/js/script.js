let currentBusinesses = [];
let currentEmails = [];
let isScraping = false;

function showModal(title, message, onProceed, onCancel) {
    const modal = document.getElementById('permissionModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');
    const proceedBtn = document.getElementById('proceedBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    
    modalTitle.textContent = title;
    modalMessage.textContent = message;
    modal.classList.remove('hidden');
    
    proceedBtn.onclick = () => {
        modal.classList.add('hidden');
        onProceed();
    };
    cancelBtn.onclick = () => {
        modal.classList.add('hidden');
        onCancel();
    };
}

function updateProgress(message, percentage) {
    const progressDiv = document.getElementById('progress');
    const progressText = document.getElementById('progressText');
    const progressBar = document.getElementById('progressBar');
    progressDiv.classList.remove('d-none');
    progressText.textContent = message;
    progressBar.style.width = `${percentage}%`;
}

function resetUI() {
    document.getElementById('businessResults').classList.add('d-none');
    document.getElementById('emailResults').classList.add('d-none');
    document.getElementById('businessTable').innerHTML = '';
    document.getElementById('emailTable').innerHTML = '';
    document.getElementById('progress').classList.add('d-none');
    document.getElementById('scrapeBtn').disabled = false;
    document.getElementById('stopBtn').classList.add('d-none');
}

document.getElementById('scrapeBtn').addEventListener('click', async () => {
    const searchTerm = document.getElementById('searchTerm').value.trim();
    if (!searchTerm) {
        alert('Please enter a search term (e.g., dental clinics in London).');
        return;
    }

    showModal('Start Scraping?', `Do you want to start scraping businesses for "${searchTerm}"?`, async () => {
        resetUI();
        isScraping = true;
        document.getElementById('scrapeBtn').disabled = true;
        document.getElementById('stopBtn').classList.remove('d-none');
        updateProgress(`Scraping businesses for "${searchTerm}"...`, 10);

        try {
            const response = await fetch('/start_scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ search_term: searchTerm })
            });
            const data = await response.json();

            if (data.error) {
                updateProgress(`Error: ${data.error}. Check console.`, 0);
                document.getElementById('progress').classList.remove('bg-blue-100');
                document.getElementById('progress').classList.add('bg-red-100');
                isScraping = false;
                document.getElementById('scrapeBtn').disabled = false;
                document.getElementById('stopBtn').classList.add('d-none');
                return;
            }

            updateProgress(data.message, 50);
            currentBusinesses = data.results;
            
            // Display businesses for editing
            const businessTable = document.getElementById('businessTable');
            businessTable.innerHTML = '';
            currentBusinesses.forEach((business, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-4 py-2"><input type="text" value="${business.business_name}" data-index="${index}" class="business-name"></td>
                    <td class="px-4 py-2"><input type="text" value="${business.website}" data-index="${index}" class="business-website"></td>
                    <td class="px-4 py-2"><button class="delete-business bg-red-600 text-white p-1 rounded hover:bg-red-700" data-index="${index}">Delete</button></td>
                `;
                businessTable.appendChild(row);
            });

            document.getElementById('businessResults').classList.remove('d-none');
            updateProgress('Edit the businesses and save to proceed.', 100);
        } catch (error) {
            updateProgress(`Error: ${error.message}. Check console.`, 0);
            document.getElementById('progress').classList.remove('bg-blue-100');
            document.getElementById('progress').classList.add('bg-red-100');
        } finally {
            if (isScraping) {
                document.getElementById('stopBtn').classList.remove('d-none');
            } else {
                document.getElementById('stopBtn').classList.add('d-none');
            }
        }
    }, () => {});
});

document.getElementById('businessTable').addEventListener('click', (e) => {
    if (e.target.classList.contains('delete-business')) {
        const index = parseInt(e.target.dataset.index);
        currentBusinesses.splice(index, 1);
        
        // Refresh table
        const businessTable = document.getElementById('businessTable');
        businessTable.innerHTML = '';
        currentBusinesses.forEach((business, idx) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-4 py-2"><input type="text" value="${business.business_name}" data-index="${idx}" class="business-name"></td>
                <td class="px-4 py-2"><input type="text" value="${business.website}" data-index="${idx}" class="business-website"></td>
                <td class="px-4 py-2"><button class="delete-business bg-red-600 text-white p-1 rounded hover:bg-red-700" data-index="${idx}">Delete</button></td>
            `;
            businessTable.appendChild(row);
        });
    }
});

document.getElementById('saveBusinessesBtn').addEventListener('click', async () => {
    // Update currentBusinesses with edited values
    const nameInputs = document.querySelectorAll('.business-name');
    const websiteInputs = document.querySelectorAll('.business-website');
    nameInputs.forEach((input, idx) => {
        currentBusinesses[idx].business_name = input.value;
    });
    websiteInputs.forEach((input, idx) => {
        currentBusinesses[idx].website = input.value;
    });

    updateProgress('Saving businesses...', 50);
    const response = await fetch('/save_businesses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ businesses: currentBusinesses })
    });
    const data = await response.json();

    if (data.error) {
        updateProgress(`Error: ${data.error}. Check console.`, 0);
        document.getElementById('progress').classList.remove('bg-blue-100');
        document.getElementById('progress').classList.add('bg-red-100');
        return;
    }

    updateProgress('Scraping emails for saved businesses...', 75);
    const emailResponse = await fetch('/scrape_emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });
    const emailData = await emailResponse.json();

    if (emailData.error) {
        updateProgress(`Error: ${emailData.error}. Check console.`, 0);
        document.getElementById('progress').classList.remove('bg-blue-100');
        document.getElementById('progress').classList.add('bg-red-100');
        return;
    }

    currentEmails = emailData.results;
    const emailTable = document.getElementById('emailTable');
    emailTable.innerHTML = '';
    currentEmails.forEach((result, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="px-4 py-2">${result.business_name}</td>
            <td class="px-4 py-2">${result.website}</td>
            <td class="px-4 py-2"><input type="text" value="${result.email}" data-index="${index}" class="email-value"></td>
            <td class="px-4 py-2"><button class="edit-email bg-blue-600 text-white p-1 rounded hover:bg-blue-700" data-index="${index}">Edit</button></td>
        `;
        emailTable.appendChild(row);
    });

    document.getElementById('businessResults').classList.add('d-none');
    document.getElementById('emailResults').classList.remove('d-none');
    updateProgress(emailData.message, 100);
});

document.getElementById('emailTable').addEventListener('click', (e) => {
    if (e.target.classList.contains('edit-email')) {
        const index = parseInt(e.target.dataset.index);
        const input = document.querySelector(`.email-value[data-index="${index}"]`);
        input.disabled = false;
        input.focus();
    }
});

document.getElementById('saveEmailsBtn').addEventListener('click', async () => {
    // Update currentEmails with edited values
    const emailInputs = document.querySelectorAll('.email-value');
    emailInputs.forEach((input, idx) => {
        currentEmails[idx].email = input.value;
    });

    updateProgress('Saving emails...', 50);
    const response = await fetch('/save_emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emails: currentEmails })
    });
    const data = await response.json();

    if (data.error) {
        updateProgress(`Error: ${data.error}. Check console.`, 0);
        document.getElementById('progress').classList.remove('bg-blue-100');
        document.getElementById('progress').classList.add('bg-red-100');
        return;
    }

    document.getElementById('downloadEmails').classList.remove('d-none');
    updateProgress(data.message, 100);

    showModal('Continue Scraping?', `Proceed to scrape the next batch starting from ${data.message.match(/\d+/)[0]}?`, async () => {
        // Start next batch
        resetUI();
        isScraping = true;
        document.getElementById('scrapeBtn').disabled = true;
        document.getElementById('stopBtn').classList.remove('d-none');
        updateProgress(`Scraping next batch of businesses...`, 10);

        const response = await fetch('/start_scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ search_term: document.getElementById('searchTerm').value.trim() })
        });
        const data = await response.json();

        if (data.error) {
            updateProgress(`Error: ${data.error}. Check console.`, 0);
            document.getElementById('progress').classList.remove('bg-blue-100');
            document.getElementById('progress').classList.add('bg-red-100');
            isScraping = false;
            document.getElementById('scrapeBtn').disabled = false;
            document.getElementById('stopBtn').classList.add('d-none');
            return;
        }

        updateProgress(data.message, 50);
        currentBusinesses = data.results;
        
        const businessTable = document.getElementById('businessTable');
        businessTable.innerHTML = '';
        currentBusinesses.forEach((business, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-4 py-2"><input type="text" value="${business.business_name}" data-index="${index}" class="business-name"></td>
                <td class="px-4 py-2"><input type="text" value="${business.website}" data-index="${index}" class="business-website"></td>
                <td class="px-4 py-2"><button class="delete-business bg-red-600 text-white p-1 rounded hover:bg-red-700" data-index="${index}">Delete</button></td>
            `;
            businessTable.appendChild(row);
        });

        document.getElementById('emailResults').classList.add('d-none');
        document.getElementById('businessResults').classList.remove('d-none');
        updateProgress('Edit the businesses and save to proceed.', 100);
    }, () => {
        resetUI();
        isScraping = false;
    });
});

document.getElementById('stopBtn').addEventListener('click', async () => {
    if (!isScraping) return;
    
    updateProgress('Stopping scraping...', 0);
    const response = await fetch('/stop_scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    });
    const data = await response.json();

    updateProgress(data.message, 0);
    document.getElementById('progress').classList.remove('bg-blue-100');
    document.getElementById('progress').classList.add('bg-yellow-100');
    isScraping = false;
    document.getElementById('scrapeBtn').disabled = false;
    document.getElementById('stopBtn').classList.add('d-none');
});