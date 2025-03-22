document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signupForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');
    const googleButton = document.getElementById('googleSignup');
    const facebookButton = document.getElementById('facebookSignup');

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset error state
        errorMessage.style.display = 'none';
        submitButton.disabled = true;
        submitButton.textContent = 'Creating Account...';

        const fullName = form.fullName.value;
        const email = form.email.value;
        const password = form.password.value;
        const confirmPassword = form.confirmPassword.value;

        // Password validation
        if (password !== confirmPassword) {
            errorMessage.textContent = "Passwords do not match";
            errorMessage.style.display = 'block';
            submitButton.disabled = false;
            submitButton.textContent = 'Create Account';
            return;
        }

        // Password strength validation
        if (password.length < 8) {
            errorMessage.textContent = "Password must be at least 8 characters long";
            errorMessage.style.display = 'block';
            submitButton.disabled = false;
            submitButton.textContent = 'Create Account';
            return;
        }

        try {
            await signUpWithCredentials({
                email,
                password,
                name: fullName,
                callbackUrl: "/app",
                redirect: true
            });
        } catch (err) {
            errorMessage.textContent = "Error creating account. Please try again.";
            errorMessage.style.display = 'block';
            submitButton.disabled = false;
            submitButton.textContent = 'Create Account';
        }
    });

    // Social signup handlers
    googleButton.addEventListener('click', () => {
        signInWithGoogle({
            callbackUrl: "/app",
            redirect: true
        });
    });

    facebookButton.addEventListener('click', () => {
        signInWithFacebook({
            callbackUrl: "/app",
            redirect: true
        });
    });
});