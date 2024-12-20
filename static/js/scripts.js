// Event listener to show loading spinner after form submission
document.querySelector('form').addEventListener('submit', function (event) {
    // Show loading spinner
    document.getElementById('loading-spinner').style.display = 'block';

    // Optionally, you can add a delay before submitting the form to simulate processing
    setTimeout(function () {
        // Form submission proceeds
    }, 100); // Simulate a delay
});
