document.addEventListener('DOMContentLoaded', () => {
    // If already logged in, redirect to index
    if (localStorage.getItem('userId')) {
        window.location.href = 'index.html';
        return;
    }

    const authForm = document.getElementById('authForm');
    const authTitle = document.getElementById('authTitle');
    const submitBtn = document.getElementById('submitBtn');
    const switchAction = document.getElementById('switchAction');
    const switchText = document.getElementById('switchText');
    const errorMsg = document.getElementById('errorMsg');

    let isLogin = true;

    // Toggle between Login and Register
    switchAction.addEventListener('click', () => {
        isLogin = !isLogin;
        errorMsg.style.display = 'none';
        
        if (isLogin) {
            authTitle.textContent = 'Login to Your Account';
            submitBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> Login';
            switchText.textContent = "Don't have an account? ";
            switchAction.textContent = "Register here";
        } else {
            authTitle.textContent = 'Create an Account';
            submitBtn.innerHTML = '<i class="fa-solid fa-user-plus"></i> Register';
            switchText.textContent = "Already have an account? ";
            switchAction.textContent = "Login here";
        }
    });

    // Handle form submission
    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        
        if (!username || !password) {
            showError("Please enter both username and password");
            return;
        }

        const endpoint = isLogin ? '/api/login' : '/api/register';
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
            
            const response = await fetch(`http://localhost:5000${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Save user session
                localStorage.setItem('userId', data.user_id);
                localStorage.setItem('username', data.username);
                
                // Redirect to main app
                window.location.href = 'index.html';
            } else {
                showError(data.error || 'Authentication failed');
            }
        } catch (error) {
            console.error('Auth error:', error);
            showError('Could not connect to the server');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = isLogin ? '<i class="fa-solid fa-right-to-bracket"></i> Login' : '<i class="fa-solid fa-user-plus"></i> Register';
        }
    });

    function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.style.display = 'block';
    }
});
