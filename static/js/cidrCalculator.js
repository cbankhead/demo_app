const cidrForm = document.getElementById("ipv4_cidr_form");
const cidrModal = document.getElementById("cidr_modal");
const cidrModalOutput = document.getElementById("cidr_modal_output");
const cidrSubmitButton = document.getElementById("cidr_submit_button");

cidrForm.addEventListener("submit", async event => {
    event.preventDefault();
    cidrSubmitButton.disabled = true;
    cidrModalOutput.textContent = "Calculating...";

    const modal = bootstrap.Modal.getOrCreateInstance(cidrModal);
    modal.show();

    try {
        const formData = new FormData(cidrForm);
        const response = await fetch(cidrForm.action || window.location.href, {
            method: "POST",
            body: formData,
        });
        const responseData = await response.json();

        cidrModalOutput.textContent = JSON.stringify(responseData, null, 2);
    } catch (error) {
        cidrModalOutput.textContent = "The calculation could not be completed.";
    } finally {
        cidrSubmitButton.disabled = false;
    }
});