// Main JavaScript file

// Fix scroll issue - Ensure scroll works on all pages
document.addEventListener('DOMContentLoaded', function() {
    // Force enable scroll on html and body
    document.documentElement.style.overflowY = 'auto';
    document.documentElement.style.overflowX = 'hidden';
    document.body.style.overflow = 'visible';
    document.body.style.height = 'auto';
    
    // Remove any event listeners that might block scroll
    document.addEventListener('wheel', function(e) {
        // Allow default scroll behavior
    }, { passive: true });
    
    document.addEventListener('touchmove', function(e) {
        // Allow default scroll behavior
    }, { passive: true });
    
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });
});

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });
    
    return isValid;
}

// Add CSRF token to fetch requests
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

