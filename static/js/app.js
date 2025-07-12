// WordPress AI Editor - Main JavaScript

// Global variables
let isProcessing = false;
let selectedImages = new Map();

// Utility functions
function showLoadingState(element, text = 'Loading...') {
    if (element) {
        element.disabled = true;
        element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
    }
}

function hideLoadingState(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
}

// Toast notification system
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = getOrCreateToastContainer();
    const toastId = 'toast-' + Date.now();
    
    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';
    
    const iconClass = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-triangle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white ${bgClass} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="${iconClass} me-2"></i>${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: duration
    });
    
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
    
    return bsToast;
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

// Image handling functions
function selectImageFromGrid(imageElement, imageData) {
    // Remove previous selections
    document.querySelectorAll('.image-selected').forEach(el => {
        el.classList.remove('image-selected');
    });
    
    // Mark as selected
    imageElement.classList.add('image-selected');
    
    // Store selection
    selectedImages.set('current', imageData);
    
    // Add visual feedback
    const checkmark = document.createElement('div');
    checkmark.className = 'position-absolute top-0 end-0 m-2';
    checkmark.innerHTML = '<i class="fas fa-check-circle text-success fa-2x"></i>';
    checkmark.style.zIndex = '10';
    
    // Remove existing checkmarks
    imageElement.querySelectorAll('.position-absolute').forEach(el => el.remove());
    
    // Add checkmark
    imageElement.style.position = 'relative';
    imageElement.appendChild(checkmark);
}

// WordPress connection validation
function validateWordPressUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
        return false;
    }
}

// Form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Image lazy loading
function setupLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + S to save post
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveBtn = document.getElementById('savePostBtn');
            if (saveBtn && !saveBtn.disabled) {
                saveBtn.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

// Auto-save functionality
function setupAutoSave() {
    let autoSaveTimeout;
    const contentElement = document.getElementById('postContent');
    
    if (contentElement) {
        const observer = new MutationObserver(() => {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                // Auto-save logic here if needed
                console.log('Content changed - auto-save could be triggered');
            }, 30000); // 30 seconds delay
        });
        
        observer.observe(contentElement, {
            childList: true,
            subtree: true,
            characterData: true
        });
    }
}

// Error handling
function handleApiError(error, fallbackMessage = 'An error occurred') {
    console.error('API Error:', error);
    
    let message = fallbackMessage;
    if (error.response) {
        // Server responded with error status
        message = error.response.data?.error || `Server error: ${error.response.status}`;
    } else if (error.request) {
        // Network error
        message = 'Network error. Please check your connection.';
    } else if (error.message) {
        message = error.message;
    }
    
    showToast(message, 'error');
}

// Loading overlay
function showLoadingOverlay(message = 'Processing...') {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    overlay.style.cssText = 'background: rgba(0,0,0,0.7); z-index: 9998;';
    
    overlay.innerHTML = `
        <div class="text-center text-white">
            <div class="spinner-border spinner-border-lg mb-3"></div>
            <h5>${message}</h5>
        </div>
    `;
    
    document.body.appendChild(overlay);
    return overlay;
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Progress tracking
function updateProgress(current, total, element) {
    if (element) {
        const percentage = Math.round((current / total) * 100);
        element.style.width = `${percentage}%`;
        element.setAttribute('aria-valuenow', percentage);
        element.textContent = `${percentage}%`;
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Setup form validation
    setupFormValidation();
    
    // Setup lazy loading for images
    setupLazyLoading();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup auto-save if on edit page
    if (document.getElementById('postContent')) {
        setupAutoSave();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    console.log('WordPress AI Editor initialized successfully');
});

// Export functions for use in other scripts
window.WordPressAIEditor = {
    showToast,
    showLoadingOverlay,
    hideLoadingOverlay,
    handleApiError,
    selectImageFromGrid,
    validateWordPressUrl
};
