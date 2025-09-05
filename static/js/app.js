// Main JavaScript file for KDP Keyword Research Tool
// Handles theme switching, global utilities, and common functionality

class KDPApp {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        this.initTheme();
        this.bindGlobalEvents();
        this.initTooltips();
        this.initClipboard();
    }

    // Enhanced Theme Management
    initTheme() {
        // Set initial theme
        document.documentElement.setAttribute('data-bs-theme', this.currentTheme);
        document.body.setAttribute('data-bs-theme', this.currentTheme);
        this.updateThemeIcon();
        this.updateChartTheme();

        // Bind theme toggle with animation
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        }
    }

    toggleTheme() {
        // Add smooth transition
        document.body.style.transition = 'all 0.3s ease';
        
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', this.currentTheme);
        document.body.setAttribute('data-bs-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        
        this.updateThemeIcon();
        this.updateChartTheme();
        
        // Remove transition after animation
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    updateThemeIcon() {
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            // Add rotation animation
            themeIcon.style.transform = 'rotate(360deg)';
            setTimeout(() => {
                themeIcon.className = this.currentTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
                themeIcon.style.transform = 'rotate(0deg)';
            }, 150);
        }
    }

    updateChartTheme() {
        // Update Chart.js theme
        const isDark = this.currentTheme === 'dark';
        if (typeof Chart !== 'undefined') {
            Chart.defaults.color = isDark ? '#ffffff' : '#333333';
            Chart.defaults.borderColor = isDark ? '#374151' : '#e5e7eb';
            Chart.defaults.backgroundColor = isDark ? '#1f2937' : '#f9fafb';
        }
    }

    // Global Event Bindings
    bindGlobalEvents() {
        // Handle escape key for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                // Close any open modals
                const openModals = document.querySelectorAll('.modal.show');
                openModals.forEach(modal => {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) bsModal.hide();
                });
            }
        });

        // Handle form submissions with loading states
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM') {
                this.showFormLoading(form);
            }
        });

        // Auto-save form data
        this.initAutoSave();
    }

    // Initialize tooltips
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize clipboard functionality
    initClipboard() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-clipboard]') || e.target.closest('[data-clipboard]')) {
                const button = e.target.matches('[data-clipboard]') ? e.target : e.target.closest('[data-clipboard]');
                const text = button.getAttribute('data-clipboard') || button.dataset.keyword || button.textContent.trim();
                this.copyToClipboard(text, button);
            }
        });
    }

    // Clipboard utility
    async copyToClipboard(text, button = null) {
        try {
            await navigator.clipboard.writeText(text);
            
            if (button) {
                const originalContent = button.innerHTML;
                const originalClasses = button.className;
                
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                button.classList.add('btn-success');
                
                setTimeout(() => {
                    button.innerHTML = originalContent;
                    button.className = originalClasses;
                }, 1500);
            }
            
            this.showToast('Text copied to clipboard!', 'success');
        } catch (err) {
            console.error('Failed to copy: ', err);
            this.showToast('Failed to copy to clipboard', 'error');
        }
    }

    // Form loading states
    showFormLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            submitButton.disabled = true;
            
            // Store original state for restoration
            submitButton.dataset.originalText = originalText;
        }
    }

    hideFormLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton && submitButton.dataset.originalText) {
            submitButton.innerHTML = submitButton.dataset.originalText;
            submitButton.disabled = false;
            delete submitButton.dataset.originalText;
        }
    }

    // Auto-save functionality
    initAutoSave() {
        const autoSaveElements = document.querySelectorAll('[data-autosave]');
        
        autoSaveElements.forEach(element => {
            const key = element.dataset.autosave;
            
            // Load saved value
            const savedValue = localStorage.getItem(`autosave_${key}`);
            if (savedValue) {
                element.value = savedValue;
            }
            
            // Save on change
            element.addEventListener('input', () => {
                localStorage.setItem(`autosave_${key}`, element.value);
            });
        });
    }

    // Toast notifications
    showToast(message, type = 'info', duration = 3000) {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '1060';
            document.body.appendChild(toastContainer);
        }

        // Create toast element
        const toastId = 'toast_' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas fa-${this.getToastIcon(type)} me-2 text-${type}"></i>
                    <strong class="me-auto">KDP Tool</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        
        toast.show();

        // Clean up after toast is hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Utility functions
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }

    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    }

    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(new Date(date));
    }

    formatRelativeTime(date) {
        const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
        const now = new Date();
        const targetDate = new Date(date);
        const diffTime = targetDate - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (Math.abs(diffDays) < 1) {
            const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
            if (Math.abs(diffHours) < 1) {
                const diffMinutes = Math.ceil(diffTime / (1000 * 60));
                return rtf.format(diffMinutes, 'minute');
            }
            return rtf.format(diffHours, 'hour');
        }
        
        return rtf.format(diffDays, 'day');
    }

    // API helpers
    async makeRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            this.showToast(`Request failed: ${error.message}`, 'error');
            throw error;
        }
    }

    // Data export helpers
    async exportData(format, filename = 'kdp_data') {
        try {
            const response = await fetch(`/export/${format}`);
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            this.downloadBlob(blob, `${filename}.${format}`);
            this.showToast(`Successfully exported as ${format.toUpperCase()}`, 'success');
        } catch (error) {
            console.error('Export error:', error);
            this.showToast(`Export failed: ${error.message}`, 'error');
        }
    }

    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    // Local storage helpers
    saveToStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    }

    loadFromStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Failed to load from localStorage:', error);
            return defaultValue;
        }
    }

    removeFromStorage(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
        }
    }

    // Debounce utility
    debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    // Throttle utility
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Chart.js default configuration
if (typeof Chart !== 'undefined') {
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;
    Chart.defaults.plugins.legend.display = true;
    Chart.defaults.plugins.tooltip.mode = 'index';
    Chart.defaults.plugins.tooltip.intersect = false;

    // Dark theme configuration
    const updateChartTheme = () => {
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        
        Chart.defaults.color = isDark ? '#ffffff' : '#333333';
        Chart.defaults.borderColor = isDark ? '#374151' : '#e5e7eb';
        Chart.defaults.backgroundColor = isDark ? '#1f2937' : '#f9fafb';
        
        // Update existing charts
        Object.values(Chart.instances || {}).forEach(chart => {
            if (chart && chart.options) {
                chart.options.plugins.legend.labels.color = Chart.defaults.color;
                chart.options.scales?.x && (chart.options.scales.x.ticks.color = Chart.defaults.color);
                chart.options.scales?.y && (chart.options.scales.y.ticks.color = Chart.defaults.color);
                chart.options.scales?.x && (chart.options.scales.x.grid.color = Chart.defaults.borderColor);
                chart.options.scales?.y && (chart.options.scales.y.grid.color = Chart.defaults.borderColor);
                chart.update();
            }
        });
    };

    // Update chart theme when theme changes
    document.addEventListener('DOMContentLoaded', updateChartTheme);
    window.addEventListener('themeChanged', updateChartTheme);
}

// Initialize the app
const kdpApp = new KDPApp();

// Global utility functions for backward compatibility
window.copyToClipboard = (text, button) => kdpApp.copyToClipboard(text, button);
window.showToast = (message, type, duration) => kdpApp.showToast(message, type, duration);
window.formatNumber = (num) => kdpApp.formatNumber(num);
window.formatCurrency = (amount, currency) => kdpApp.formatCurrency(amount, currency);
window.exportData = (format, filename) => kdpApp.exportData(format, filename);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KDPApp;
}
