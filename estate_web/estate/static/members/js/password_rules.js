// password_rules.js

document.addEventListener("DOMContentLoaded", function () {
    const passwordField = document.querySelector("#id_password1"); // Django's default id
    const requirementsBox = document.createElement("div");

    // Style box
    requirementsBox.className = "alert alert-info mt-2";
    requirementsBox.innerHTML = `
        <strong>Password requirements:</strong>
        <ul class="mb-0">
            <li id="pw-length">At least 8 characters</li>
            <li id="pw-number">At least one number</li>
            <li id="pw-uppercase">At least one uppercase letter</li>
            <li id="pw-lowercase">At least one lowercase letter</li>
            <li id="pw-special">At least one special character (!@#$%^&*)</li>
        </ul>
    `;
    requirementsBox.style.display = "none"; // hidden by default

    // Insert box right under password field
    passwordField.parentNode.appendChild(requirementsBox);

    // Show rules when focusing on password field
    passwordField.addEventListener("focus", () => {
        requirementsBox.style.display = "block";
    });

    // Hide rules if field loses focus
    passwordField.addEventListener("blur", () => {
        if (passwordField.value === "") {
            requirementsBox.style.display = "none";
        }
    });

    // Check rules while typing
    passwordField.addEventListener("input", () => {
        const value = passwordField.value;

        // Validate rules
        document.querySelector("#pw-length").style.color = value.length >= 8 ? "green" : "red";
        document.querySelector("#pw-number").style.color = /\d/.test(value) ? "green" : "red";
        document.querySelector("#pw-uppercase").style.color = /[A-Z]/.test(value) ? "green" : "red";
        document.querySelector("#pw-lowercase").style.color = /[a-z]/.test(value) ? "green" : "red";
        document.querySelector("#pw-special").style.color = /[!@#$%^&*]/.test(value) ? "green" : "red";
    });
});
