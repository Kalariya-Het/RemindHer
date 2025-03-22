document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('signinForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');
    const googleButton = document.getElementById('googleLogin');
    const facebookButton = document.getElementById('facebookLogin');

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset error state
        errorMessage.style.display = 'none';
        submitButton.disabled = true;
        submitButton.textContent = 'Signing in...';

        const email = form.email.value;
        const password = form.password.value;

        try {
            await signInWithCredentials({
                email,
                password,
                callbackUrl: "/app",
                redirect: true
            });
        } catch (err) {
            errorMessage.textContent = "Invalid email or password";
            errorMessage.style.display = 'block';
            submitButton.disabled = false;
            submitButton.textContent = 'Sign In';
        }
    });

    // Social login handlers
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