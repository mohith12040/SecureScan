// SecureScan Client-Side Core Framework
document.addEventListener('DOMContentLoaded', () => {
    // 1. Automatic Auto-Dismiss for Flash Alert boxes
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
    
    // 2. Active Sidebar State Syncing
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-item a');
    sidebarLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
            link.closest('.sidebar-item').classList.add('active');
        } else {
            link.closest('.sidebar-item').classList.remove('active');
        }
    });
});

/**
 * Standard security Fetch wrapper that injects CSRF tokens
 * automatically for all database modifying actions.
 */
async function secureFetch(url, options = {}) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    if (!options.headers) {
        options.headers = {};
    }
    
    if (csrfToken) {
        options.headers['X-CSRFToken'] = csrfToken;
    }
    
    if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.message || `HTTP Exception: ${response.status}`);
    }
    
    return response.json();
}
