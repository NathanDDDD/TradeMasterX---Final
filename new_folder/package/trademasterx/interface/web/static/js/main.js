/**
 * TradeMasterX 2.0 - Main JavaScript Module
 * Handles global functionality, utilities, and common operations
 */

// Global variables
window.TradeMasterX = {
    socket: null,
    config: {},
    state: {
        connected: false,
        systemActive: false,
        lastUpdate: null
    },
    charts: {},
    notifications: []
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing TradeMasterX Web Interface...');
    
    // Initialize Socket.IO connection
    initializeSocket();
    
    // Initialize global event listeners
    initializeEventListeners();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Load initial configuration
    loadConfiguration();
    
    console.log('TradeMasterX Web Interface initialized successfully');
}

/**
 * Initialize Socket.IO connection
 */
function initializeSocket() {
    if (!window.io) {
        console.error('Socket.IO not loaded');
        return;
    }
    
    TradeMasterX.socket = io();
    
    // Connection events
    TradeMasterX.socket.on('connect', function() {
        console.log('Connected to TradeMasterX server');
        TradeMasterX.state.connected = true;
        updateConnectionStatus(true);
        showToast('Connected to TradeMasterX server', 'success');
    });
    
    TradeMasterX.socket.on('disconnect', function() {
        console.log('Disconnected from TradeMasterX server');
        TradeMasterX.state.connected = false;
        updateConnectionStatus(false);
        showToast('Disconnected from server', 'warning');
    });
    
    TradeMasterX.socket.on('reconnect', function() {
        console.log('Reconnected to TradeMasterX server');
        TradeMasterX.state.connected = true;
        updateConnectionStatus(true);
        showToast('Reconnected to server', 'success');
    });
    
    // Data events
    TradeMasterX.socket.on('status_update', function(data) {
        handleStatusUpdate(data);
    });
    
    TradeMasterX.socket.on('bot_command_result', function(data) {
        handleBotCommandResult(data);
    });
    
    TradeMasterX.socket.on('error', function(data) {
        console.error('Socket error:', data);
        showToast('Server error: ' + data.message, 'danger');
    });
    
    // Join monitoring room for real-time updates
    TradeMasterX.socket.emit('join_room', {room: 'monitoring'});
}

/**
 * Initialize global event listeners
 */
function initializeEventListeners() {
    // Handle navigation
    document.addEventListener('click', function(e) {
        // Handle external links
        if (e.target.matches('a[href^="http"]')) {
            e.target.setAttribute('target', '_blank');
        }
    });
    
    // Handle form submissions
    document.addEventListener('submit', function(e) {
        // Add loading state to submit buttons
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        }
    });
    
    // Handle keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+R: Refresh data
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            refreshCurrentPage();
        }
        
        // Escape: Close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) modalInstance.hide();
            });
        }
    });
}

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Load configuration from server
 */
function loadConfiguration() {
    fetch('/api/config')
        .then(response => response.json())
        .then(data => {
            TradeMasterX.config = data;
            console.log('Configuration loaded:', data);
        })
        .catch(error => {
            console.error('Error loading configuration:', error);
            showToast('Error loading configuration', 'warning');
        });
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const statusIcon = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-text');
    
    if (statusIcon && statusText) {
        if (connected) {
            statusIcon.className = 'fas fa-circle text-success me-1';
            statusText.textContent = 'Connected';
        } else {
            statusIcon.className = 'fas fa-circle text-danger me-1';
            statusText.textContent = 'Disconnected';
        }
    }
}

/**
 * Handle status updates from server
 */
function handleStatusUpdate(data) {
    TradeMasterX.state.lastUpdate = new Date(data.timestamp);
    TradeMasterX.state.systemActive = data.system?.active || false;
    
    // Trigger custom event for components to listen
    document.dispatchEvent(new CustomEvent('statusUpdate', {
        detail: data
    }));
}

/**
 * Handle bot command results
 */
function handleBotCommandResult(data) {
    if (data.success) {
        showToast(data.message, 'success');
    } else {
        showToast('Command failed: ' + data.error, 'danger');
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const toastId = 'toast-' + Date.now();
    const typeColors = {
        'success': 'text-bg-success',
        'danger': 'text-bg-danger',
        'warning': 'text-bg-warning',
        'info': 'text-bg-info'
    };
    
    const toastHtml = `
        <div class="toast ${typeColors[type] || 'text-bg-info'}" id="${toastId}" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${escapeHtml(message)}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: duration > 0,
        delay: duration
    });
    
    toast.show();
    
    // Store notification
    TradeMasterX.notifications.push({
        id: toastId,
        message: message,
        type: type,
        timestamp: new Date()
    });
    
    // Clean up old notifications
    if (TradeMasterX.notifications.length > 50) {
        TradeMasterX.notifications = TradeMasterX.notifications.slice(-25);
    }
    
    // Remove element after hide
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

/**
 * Format number with thousands separator
 */
function formatNumber(num, decimals = 2) {
    if (typeof num !== 'number') return num;
    
    return num.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

/**
 * Format bytes to human readable format
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format duration in milliseconds to human readable format
 */
function formatDuration(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
}

/**
 * Deep clone object
 */
function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map(item => deepClone(item));
    if (typeof obj === 'object') {
        const clonedObj = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                clonedObj[key] = deepClone(obj[key]);
            }
        }
        return clonedObj;
    }
}

/**
 * Debounce function execution
 */
function debounce(func, wait, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

/**
 * Throttle function execution
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Refresh current page data
 */
function refreshCurrentPage() {
    const event = new CustomEvent('refreshData');
    document.dispatchEvent(event);
    showToast('Refreshing data...', 'info', 2000);
}

/**
 * Download data as JSON file
 */
function downloadJSON(data, filename) {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

/**
 * Download data as CSV file
 */
function downloadCSV(data, filename) {
    if (!Array.isArray(data) || data.length === 0) {
        showToast('No data to export', 'warning');
        return;
    }
    
    const headers = Object.keys(data[0]);
    let csvContent = headers.join(',') + '\n';
    
    data.forEach(row => {
        const values = headers.map(header => {
            let value = row[header];
            if (typeof value === 'string' && value.includes(',')) {
                value = `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        });
        csvContent += values.join(',') + '\n';
    });
    
    const blob = new Blob([csvContent], {type: 'text/csv'});
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard', 'success', 2000);
    } catch (err) {
        console.error('Failed to copy to clipboard:', err);
        showToast('Failed to copy to clipboard', 'danger');
    }
}

/**
 * Get query parameter from URL
 */
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

/**
 * Update URL query parameter without refresh
 */
function updateQueryParam(param, value) {
    const url = new URL(window.location);
    if (value) {
        url.searchParams.set(param, value);
    } else {
        url.searchParams.delete(param);
    }
    window.history.replaceState({}, '', url);
}

/**
 * Create chart color palette
 */
function getChartColors(count = 1) {
    const colors = [
        '#007bff', '#28a745', '#ffc107', '#dc3545', '#17a2b8',
        '#6610f2', '#fd7e14', '#e83e8c', '#20c997', '#6f42c1'
    ];
    
    if (count === 1) return colors[0];
    return colors.slice(0, count);
}

/**
 * Validate email address
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Generate random ID
 */
function generateId(prefix = 'id') {
    return `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Smooth scroll to element
 */
function scrollToElement(element, offset = 0) {
    const targetPosition = element.offsetTop - offset;
    window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
    });
}

/**
 * Local storage helper
 */
const storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing from localStorage:', e);
        }
    },
    
    clear: function() {
        try {
            localStorage.clear();
        } catch (e) {
            console.error('Error clearing localStorage:', e);
        }
    }
};

// Export functions for use in other modules
window.TradeMasterX.utils = {
    showToast,
    escapeHtml,
    formatNumber,
    formatBytes,
    formatDuration,
    deepClone,
    debounce,
    throttle,
    downloadJSON,
    downloadCSV,
    copyToClipboard,
    getQueryParam,
    updateQueryParam,
    getChartColors,
    isValidEmail,
    generateId,
    isInViewport,
    scrollToElement,
    storage
};
