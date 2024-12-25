// Example: Form Validation for Login and Signup
document.addEventListener("DOMContentLoaded", function() {
    // Handle form submission for login
    const loginForm = document.querySelector('#loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const username = document.querySelector('#username').value;
            const password = document.querySelector('#password').value;
            
            // Basic form validation
            if (username === '' || password === '') {
                alert('Please fill in both username and password.');
                event.preventDefault();  // Prevent form submission
            }
        });
    }

    // Handle form submission for signup
    const signupForm = document.querySelector('#signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            const email = document.querySelector('#email').value;
            const password = document.querySelector('#password').value;
            const confirmPassword = document.querySelector('#confirmPassword').value;
            
            // Basic form validation
            if (email === '' || password === '' || confirmPassword === '') {
                alert('Please fill in all fields.');
                event.preventDefault();
            } else if (password !== confirmPassword) {
                alert('Passwords do not match.');
                event.preventDefault();
            }
        });
    }

    // Example: Show/Hide Password toggle
    const passwordField = document.querySelector('#password');
    const confirmPasswordField = document.querySelector('#confirmPassword');
    const togglePasswordBtn = document.querySelector('.toggle-password');

    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function() {
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                confirmPasswordField.type = 'text';
                togglePasswordBtn.textContent = 'Hide Password';
            } else {
                passwordField.type = 'password';
                confirmPasswordField.type = 'password';
                togglePasswordBtn.textContent = 'Show Password';
            }
        });
    }

    // Example: Button click event on the Home Page
    const homePageBtn = document.querySelector('#homePageBtn');
    if (homePageBtn) {
        homePageBtn.addEventListener('click', function() {
            alert('You clicked the Home button!');
        });
    }
});
