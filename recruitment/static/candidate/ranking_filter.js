document.addEventListener('DOMContentLoaded', function() {
    // Function to submit form
    function submitForm(form) {
        // Get all form values
        const formData = new FormData(form);

        // Convert to URL parameters
        const searchParams = new URLSearchParams(formData);

        // Update URL and reload
        window.location.href = window.location.pathname + '?' + searchParams.toString();
    }

    // Add event listeners to all auto-submit inputs
    const filterInputs = document.querySelectorAll('.auto-submit');

    filterInputs.forEach(input => {
        // For select elements
        if (input.tagName === 'SELECT') {
            input.addEventListener('change', function() {
                submitForm(this.closest('form'));
            });
        }

        // For number inputs - add debounce
        if (input.type === 'number') {
            let timeout = null;
            input.addEventListener('input', function() {
                clearTimeout(timeout);
                const form = this.closest('form');
                timeout = setTimeout(() => {
                    submitForm(form);
                }, 500); // 500ms delay before submitting
            });

            // Also trigger on change (for when users use up/down arrows)
            input.addEventListener('change', function() {
                submitForm(this.closest('form'));
            });
        }
    });
});

