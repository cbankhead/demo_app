/*
 * modalLookupHandler.js
 * Shared utility for modal-based lookup handlers (AWS, Azure, GCP, etc.)
 *
 * Responsibilities:
 *   - Initialize modal behavior
 *   - Update visible input fields based on radio selection
 *   - Handle form submission + AJAX lookup
 */

function initializeModalLookup(config) {

    //console.log(config)

    /* ------------------------------------------------------------
     * 1. Modal Setup
     * ------------------------------------------------------------ */

    const modal = document.getElementById(config.modalId);
    const bsModalInstance = modal ? new bootstrap.Modal(modal) : null;

    if (modal) {
        modal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;

            if (!button) return;

            // Optional debug:
            // console.log("Modal triggered by button:", button);

            const closeButton = modal.querySelector('.btn-close');

            if (closeButton) {
                modal.addEventListener('shown.bs.modal', function onShown() {
                    closeButton.focus();
                    modal.removeEventListener('shown.bs.modal', onShown);
                });
            }

            modal.querySelector('.modal-title').textContent =
                button.getAttribute('data-modal-title') || 'Details';

            modal.querySelector('.modal-body').innerHTML =
                button.getAttribute('data-modal-body') || '';
        });
    }


    /* ------------------------------------------------------------
     * 2. Modal Result Display Helper
     * ------------------------------------------------------------ */

    function showResultsInModal(title, data) {
        if (!modal || !bsModalInstance) return;

        modal.querySelector('.modal-title').textContent = title;

        modal.querySelector('.modal-body').innerHTML =
            `<pre>${JSON.stringify(data, null, 2)}</pre>`;

        bsModalInstance.show();

        modal.addEventListener('shown.bs.modal', function onShown() {
            const closeButton = modal.querySelector('.btn-close');
            if (closeButton) closeButton.focus();
            modal.removeEventListener('shown.bs.modal', onShown);
        });
    }


    /* ------------------------------------------------------------
     * 3. Radio Button → Input Visibility Logic
     * ------------------------------------------------------------ */

    function updateSearchInputVisibility() {
        const selectedRadio = document.querySelector(config.radioSelector + ':checked');

        if (!selectedRadio) {
            console.warn("No radio button is selected.");
            return;
        }

        const selectedValue = selectedRadio.value;

        // Optional debug:
        // console.log("Selected lookup option:", selectedValue);

        Object.keys(config.lookups).forEach(key => {
            const lookup = config.lookups[key];
            const container = document.getElementById(lookup.containerId);
            const input = document.getElementById(lookup.inputId);

            const isActive = key === selectedValue;

            if (container) container.style.display = isActive ? 'block' : 'none';
            if (input) input.disabled = !isActive;

            // Optional debug:
            // console.log(`Lookup ${key}: ${isActive ? "ENABLED" : "DISABLED"}`);
        });
    }

    // Attach listeners
    document.querySelectorAll(config.radioSelector).forEach(radio => {
        radio.addEventListener('change', updateSearchInputVisibility);
    });

    // Initial state
    updateSearchInputVisibility();


    /* ------------------------------------------------------------
     * 4. Form Submission Handler
     * ------------------------------------------------------------ */

    const form = document.getElementById(config.formId);

    if (form) {
        form.addEventListener('submit', event => {
            event.preventDefault();

            const selectedRadio = document.querySelector(config.radioSelector + ':checked');

            if (!selectedRadio) {
                alert("Please select a lookup option.");
                return;
            }

            const selectedValue = selectedRadio.value;
            const lookup = config.lookups[selectedValue];

            if (!lookup) {
                alert("Unknown lookup option.");
                return;
            }

            const inputElement = document.getElementById(lookup.inputId);
            const inputValue = inputElement.value.trim();

            if (!inputValue) {
                alert(`Please enter or select a value for ${lookup.resultLabel.toLowerCase()}`);
                return;
            }

            // Optional debug:
            // console.log("Submitting lookup:", lookup);
            // alert("Submitting lookup for: " + inputValue);

            const url = `${lookup.url}?${lookup.paramName}=${encodeURIComponent(inputValue)}`;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    showResultsInModal(`${lookup.resultLabel}: ${inputValue}`, data.data);
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert(`Error: ${error.message}`);
                });
        });
    }
}
