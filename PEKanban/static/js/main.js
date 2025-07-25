// Main JavaScript file for Taskboard Flask App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add fade-in animation to cards
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });
});

// Utility Functions
function showAlert(type, message, permanent = false) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show ${permanent ? 'alert-permanent' : ''}`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container');
    const firstChild = container.firstElementChild;
    container.insertBefore(alertDiv, firstChild);
    
    // Auto-dismiss after 5 seconds if not permanent
    if (!permanent) {
        setTimeout(() => {
            if (alertDiv.parentNode) {
                const bsAlert = new bootstrap.Alert(alertDiv);
                bsAlert.close();
            }
        }, 5000);
    }
    
    return alertDiv;
}

function showLoading(element, text = 'Caricamento...') {
    const originalContent = element.innerHTML;
    element.innerHTML = `<span class="spinner me-2"></span>${text}`;
    element.disabled = true;
    
    return function() {
        element.innerHTML = originalContent;
        element.disabled = false;
    };
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// AJAX Helper Functions
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            showAlert('danger', 'Errore di connessione. Riprova più tardi.');
            throw error;
        });
}

// Form Validation
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
    });
    
    return isValid;
}

// Real-time form validation
document.addEventListener('input', function(e) {
    if (e.target.hasAttribute('required')) {
        if (e.target.value.trim()) {
            e.target.classList.remove('is-invalid');
            e.target.classList.add('is-valid');
        } else {
            e.target.classList.remove('is-valid');
            e.target.classList.add('is-invalid');
        }
    }
});

// Password strength indicator
function checkPasswordStrength(password) {
    let strength = 0;
    let feedback = [];
    
    if (password.length >= 8) {
        strength += 1;
    } else {
        feedback.push('Almeno 8 caratteri');
    }
    
    if (/[a-z]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('Lettere minuscole');
    }
    
    if (/[A-Z]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('Lettere maiuscole');
    }
    
    if (/[0-9]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('Numeri');
    }
    
    if (/[^A-Za-z0-9]/.test(password)) {
        strength += 1;
    } else {
        feedback.push('Caratteri speciali');
    }
    
    return {
        strength: strength,
        feedback: feedback,
        level: strength < 2 ? 'weak' : strength < 4 ? 'medium' : 'strong'
    };
}

// Add password strength indicator to password fields
document.addEventListener('DOMContentLoaded', function() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    
    passwordInputs.forEach(input => {
        if (input.name === 'password' && input.form && input.form.querySelector('input[name="confirm_password"]')) {
            const strengthDiv = document.createElement('div');
            strengthDiv.className = 'password-strength mt-1';
            input.parentNode.appendChild(strengthDiv);
            
            input.addEventListener('input', function() {
                const result = checkPasswordStrength(this.value);
                let color = result.level === 'weak' ? 'danger' : result.level === 'medium' ? 'warning' : 'success';
                let width = (result.strength / 5) * 100;
                
                strengthDiv.innerHTML = `
                    <div class="progress" style="height: 4px;">
                        <div class="progress-bar bg-${color}" style="width: ${width}%"></div>
                    </div>
                    <small class="text-${color}">
                        Password ${result.level === 'weak' ? 'debole' : result.level === 'medium' ? 'media' : 'forte'}
                        ${result.feedback.length > 0 ? ' - Manca: ' + result.feedback.join(', ') : ''}
                    </small>
                `;
            });
        }
    });
});

// Auto-resize textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Trigger resize on load
        textarea.dispatchEvent(new Event('input'));
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Copy to clipboard functionality
function copyToClipboard(text, successMessage = 'Copiato negli appunti!') {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('success', successMessage);
        }).catch(() => {
            fallbackCopyToClipboard(text, successMessage);
        });
    } else {
        fallbackCopyToClipboard(text, successMessage);
    }
}

function fallbackCopyToClipboard(text, successMessage) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showAlert('success', successMessage);
    } catch (err) {
        showAlert('danger', 'Impossibile copiare negli appunti');
    }
    
    document.body.removeChild(textArea);
}

// Local storage helpers
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('LocalStorage not available:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('LocalStorage not available:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('LocalStorage not available:', e);
        }
    }
};

// Theme management
const Theme = {
    init: function() {
        const savedTheme = Storage.get('theme', 'light');
        this.apply(savedTheme);
    },
    
    toggle: function() {
        const currentTheme = document.body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        this.apply(newTheme);
    },
    
    apply: function(theme) {
        document.body.setAttribute('data-theme', theme);
        Storage.set('theme', theme);
        
        // Update theme toggle button if exists
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            }
        }
    }
};

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    Theme.init();
});

// Export functions for global use
window.TaskboardApp = {
    showAlert,
    showLoading,
    confirmAction,
    makeRequest,
    validateForm,
    copyToClipboard,
    Storage,
    Theme
};

// Service Worker registration (for PWA functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

console.log('Taskboard App initialized successfully!');