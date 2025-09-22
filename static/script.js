document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    const fileInput = document.getElementById('file-input');
    const languageSelect = document.getElementById('language-select');
    const resultsContainer = document.getElementById('results-container');
    const loader = document.getElementById('loader');

    // Show the loader and clear previous results
    loader.style.display = 'block';
    resultsContainer.textContent = '';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('language', languageSelect.value);

    try {
        const response = await fetch('/simplify', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            resultsContainer.textContent = result.simplified_text;
        } else {
            resultsContainer.textContent = 'Error: ' + result.error;
        }

    } catch (error) {
        resultsContainer.textContent = 'An unexpected error occurred. Please check the console.';
        console.error('Error:', error);
    } finally {
        // Hide the loader
        loader.style.display = 'none';
    }
});