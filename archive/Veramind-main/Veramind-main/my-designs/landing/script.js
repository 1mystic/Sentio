document.addEventListener('DOMContentLoaded', function () {
    // Lucide Icons initialization
    lucide.createIcons();

    // Toggle switch functionality
    const toggleButtons = document.querySelectorAll('.toggle-btn');

    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove 'active' class from all buttons
            toggleButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add 'active' class to the clicked button
            button.classList.add('active');

            // You can add logic here to update the stats based on the selected period (Day, Week, Month)
            const selectedPeriod = button.dataset.period;
            console.log(`Selected period: ${selectedPeriod}`);
            // e.g., updateStats(selectedPeriod);
        });
    });
});