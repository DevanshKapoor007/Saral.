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

// Get the HTML element where we will display the challenge
const challengeBox = document.getElementById('challenge-box');

// This array holds all your possible challenges
const challenges = [
    "Challenge: Try simplifying a handwritten note!",
    "Challenge: Can you upload a two-page PDF?",
    "Challenge: Find a document with tables and see how it works.",
    "Challenge: Try a document in a different language!",
    "Challenge: Upload a low-quality photo of a receipt."
];

// This is the main function that runs a random challenge
function triggerRandomChallenge() {
    // 1. Pick a random challenge from the array
    const randomIndex = Math.floor(Math.random() * challenges.length);
    const randomChallenge = challenges[randomIndex];

    // 2. Display the challenge on the screen
    console.log("Challenge Activated:", randomChallenge);
    challengeBox.textContent = randomChallenge;
    
    // 3. Make the challenge box visible, then fade it out after a few seconds
    challengeBox.style.opacity = 1;
    setTimeout(() => {
        challengeBox.style.opacity = 0;
    }, 4000); // The message will be visible for 4 seconds

    // 4. Schedule the next random challenge
    scheduleNextChallenge();
}

// This function schedules the next trigger at a random time
function scheduleNextChallenge() {
    // Define your time range in milliseconds (1s = 1000ms)
    const minInterval = 5000;  // 5 seconds
    const maxInterval = 15000; // 15 seconds

    // Calculate a random delay
    const randomTime = Math.random() * (maxInterval - minInterval) + minInterval;

    console.log(`Next challenge in ${(randomTime / 1000).toFixed(2)} seconds.`);

    // Set a timeout to run the challenge function after the random delay
    setTimeout(triggerRandomChallenge, randomTime);
}

// --- Start the Challenge Mode ---
// This initial call kicks everything off.
scheduleNextChallenge();