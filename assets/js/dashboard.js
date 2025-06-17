/**
 * CYBERSECURITY DASHBOARD - ENHANCED JAVASCRIPT
 * Modern UI interactions and optimizations
 */

// ============================================
// GLOBAL CONFIGURATION
// ============================================

const DashboardConfig = {
    animations: {
        duration: 300,
        easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
    },
    api: {
        baseUrl: 'http://127.0.0.1:8000',
        timeout: 5000
    },
    ui: {
        enableAnimations: true,
        autoRefresh: true,
        refreshInterval: 30000 // 30 seconds
    }
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

class DashboardUtils {
    static formatNumber(num, decimals = 0) {
        if (num === null || num === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    }

    static formatPercentage(num, decimals = 1) {
        if (num === null || num === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num / 100);
    }

    static formatCurrency(num, currency = 'USD') {
        if (num === null || num === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(num);
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    static throttle(func, limit) {
        let lastFunc;
        let lastRan;
        return function(...args) {
            if (!lastRan) {
                func.apply(this, args);
                lastRan = Date.now();
            } else {
                clearTimeout(lastFunc);
                lastFunc = setTimeout(() => {
                    if ((Date.now() - lastRan) >= limit) {
                        func.apply(this, args);
                        lastRan = Date.now();
                    }
                }, limit - (Date.now() - lastRan));
            }
        };
    }

    static generateId() {
        return Math.random().toString(36).substr(2, 9);
    }

    static copyToClipboard(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return Promise.resolve();
            } catch (err) {
                document.body.removeChild(textArea);
                return Promise.reject(err);
            }
        }
    }
}

// ============================================
// ANIMATION ENGINE
// ============================================

class AnimationEngine {
    static fadeIn(element, duration = 300) {
        if (!DashboardConfig.ui.enableAnimations) return;
        
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = `all ${duration}ms ${DashboardConfig.animations.easing}`;
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    }

    static slideIn(element, direction = 'left', duration = 300) {
        if (!DashboardConfig.ui.enableAnimations) return;
        
        const transforms = {
            left: 'translateX(-30px)',
            right: 'translateX(30px)',
            up: 'translateY(-30px)',
            down: 'translateY(30px)'
        };

        element.style.opacity = '0';
        element.style.transform = transforms[direction];
        element.style.transition = `all ${duration}ms ${DashboardConfig.animations.easing}`;
        
        requestAnimationFrame(() => {
            element.style.opacity = '1';
            element.style.transform = 'translate(0)';
        });
    }

    static pulse(element, duration = 1000) {
        if (!DashboardConfig.ui.enableAnimations) return;
        
        element.style.animation = `pulse ${duration}ms ease-in-out`;
        setTimeout(() => {
            element.style.animation = '';
        }, duration);
    }

    static countUp(element, start, end, duration = 1000) {
        if (!DashboardConfig.ui.enableAnimations) {
            element.textContent = end;
            return;
        }

        const startTime = performance.now();
        const range = end - start;

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = start + (range * easeOutQuart);
            
            element.textContent = Math.round(current);
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    }
}

// ============================================
// NOTIFICATION SYSTEM
// ============================================

class NotificationSystem {
    constructor() {
        this.container = this.createContainer();
        this.notifications = new Map();
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            pointer-events: none;
        `;
        document.body.appendChild(container);
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const id = DashboardUtils.generateId();
        const notification = this.createNotification(message, type, id);
        
        this.container.appendChild(notification);
        this.notifications.set(id, notification);
        
        // Animate in
        requestAnimationFrame(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        });
        
        // Auto-remove
        if (duration > 0) {
            setTimeout(() => this.remove(id), duration);
        }
        
        return id;
    }

    createNotification(message, type, id) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: white;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
            pointer-events: auto;
            max-width: 400px;
            word-wrap: break-word;
            border-left: 4px solid var(--${type}-color, #007bff);
        `;
        
        const typeColors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        
        notification.style.borderLeftColor = typeColors[type] || typeColors.info;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="flex: 1; color: #333; font-weight: 500;">${message}</div>
                <button onclick="dashboardNotifications.remove('${id}')" 
                        style="background: none; border: none; color: #999; cursor: pointer; font-size: 18px;">&times;</button>
            </div>
        `;
        
        return notification;
    }

    remove(id) {
        const notification = this.notifications.get(id);
        if (notification) {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.notifications.delete(id);
            }, 300);
        }
    }

    clear() {
        this.notifications.forEach((_, id) => this.remove(id));
    }
}

// ============================================
// DATA MANAGER
// ============================================

class DataManager {
    constructor() {
        this.cache = new Map();
        this.cacheExpiry = new Map();
        this.defaultCacheDuration = 5 * 60 * 1000; // 5 minutes
    }

    async fetchData(url, options = {}) {
        const cacheKey = url + JSON.stringify(options);
        
        // Check cache
        if (this.cache.has(cacheKey) && this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey);
        }

        try {
            const response = await fetch(url, {
                timeout: DashboardConfig.api.timeout,
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache the data
            this.cache.set(cacheKey, data);
            this.cacheExpiry.set(cacheKey, Date.now() + this.defaultCacheDuration);
            
            return data;
            
        } catch (error) {
            console.error('Data fetch error:', error);
            dashboardNotifications.show(`Failed to fetch data: ${error.message}`, 'error');
            throw error;
        }
    }

    isCacheValid(cacheKey) {
        const expiry = this.cacheExpiry.get(cacheKey);
        return expiry && Date.now() < expiry;
    }

    clearCache() {
        this.cache.clear();
        this.cacheExpiry.clear();
    }

    invalidateCache(pattern) {
        for (const key of this.cache.keys()) {
            if (key.includes(pattern)) {
                this.cache.delete(key);
                this.cacheExpiry.delete(key);
            }
        }
    }
}

// ============================================
// PERFORMANCE MONITOR
// ============================================

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoadTime: 0,
            renderTimes: [],
            apiCallTimes: [],
            memoryUsage: []
        };
        
        this.startTime = performance.now();
        this.init();
    }

    init() {
        // Monitor page load
        window.addEventListener('load', () => {
            this.metrics.pageLoadTime = performance.now() - this.startTime;
            console.log(`Page loaded in ${this.metrics.pageLoadTime.toFixed(2)}ms`);
        });

        // Monitor memory usage periodically
        if ('memory' in performance) {
            setInterval(() => {
                this.metrics.memoryUsage.push({
                    timestamp: Date.now(),
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize
                });
                
                // Keep only last 50 measurements
                if (this.metrics.memoryUsage.length > 50) {
                    this.metrics.memoryUsage.shift();
                }
            }, 10000); // Every 10 seconds
        }
    }

    startTimer(name) {
        this.timers = this.timers || new Map();
        this.timers.set(name, performance.now());
    }

    endTimer(name) {
        if (this.timers && this.timers.has(name)) {
            const duration = performance.now() - this.timers.get(name);
            this.timers.delete(name);
            
            if (name.includes('render')) {
                this.metrics.renderTimes.push(duration);
            } else if (name.includes('api')) {
                this.metrics.apiCallTimes.push(duration);
            }
            
            console.log(`${name}: ${duration.toFixed(2)}ms`);
            return duration;
        }
        return 0;
    }

    getReport() {
        const avgRenderTime = this.metrics.renderTimes.length > 0 
            ? this.metrics.renderTimes.reduce((a, b) => a + b, 0) / this.metrics.renderTimes.length 
            : 0;
            
        const avgApiTime = this.metrics.apiCallTimes.length > 0 
            ? this.metrics.apiCallTimes.reduce((a, b) => a + b, 0) / this.metrics.apiCallTimes.length 
            : 0;

        return {
            pageLoadTime: this.metrics.pageLoadTime,
            averageRenderTime: avgRenderTime,
            averageApiTime: avgApiTime,
            totalRenders: this.metrics.renderTimes.length,
            totalApiCalls: this.metrics.apiCallTimes.length,
            memoryUsage: this.metrics.memoryUsage
        };
    }
}

// ============================================
// ENHANCED UI COMPONENTS
// ============================================

class EnhancedComponents {
    static createLoadingSpinner(size = 'medium') {
        const sizes = {
            small: '16px',
            medium: '24px',
            large: '32px'
        };
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.style.width = sizes[size];
        spinner.style.height = sizes[size];
        
        return spinner;
    }

    static createProgressBar(progress = 0, showText = true) {
        const container = document.createElement('div');
        container.style.cssText = `
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            height: 8px;
            position: relative;
        `;
        
        const bar = document.createElement('div');
        bar.style.cssText = `
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            height: 100%;
            width: ${progress}%;
            transition: width 0.3s ease;
        `;
        
        container.appendChild(bar);
        
        if (showText) {
            const text = document.createElement('div');
            text.style.cssText = `
                position: absolute;
                top: 100%;
                left: 0;
                font-size: 12px;
                color: #666;
                margin-top: 4px;
            `;
            text.textContent = `${progress}%`;
            container.appendChild(text);
        }
        
        return { container, bar, update: (newProgress) => {
            bar.style.width = `${newProgress}%`;
            if (showText) {
                container.querySelector('div:last-child').textContent = `${newProgress}%`;
            }
        }};
    }

    static createTooltip(element, content, position = 'top') {
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            z-index: 10000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        `;
        tooltip.textContent = content;
        
        element.addEventListener('mouseenter', (e) => {
            document.body.appendChild(tooltip);
            
            const rect = element.getBoundingClientRect();
            const tooltipRect = tooltip.getBoundingClientRect();
            
            let left, top;
            
            switch (position) {
                case 'top':
                    left = rect.left + (rect.width - tooltipRect.width) / 2;
                    top = rect.top - tooltipRect.height - 8;
                    break;
                case 'bottom':
                    left = rect.left + (rect.width - tooltipRect.width) / 2;
                    top = rect.bottom + 8;
                    break;
                case 'left':
                    left = rect.left - tooltipRect.width - 8;
                    top = rect.top + (rect.height - tooltipRect.height) / 2;
                    break;
                case 'right':
                    left = rect.right + 8;
                    top = rect.top + (rect.height - tooltipRect.height) / 2;
                    break;
            }
            
            tooltip.style.left = `${left}px`;
            tooltip.style.top = `${top}px`;
            tooltip.style.opacity = '1';
        });
        
        element.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
            setTimeout(() => {
                if (tooltip.parentNode) {
                    tooltip.parentNode.removeChild(tooltip);
                }
            }, 200);
        });
    }
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyString(e);
            const handler = this.shortcuts.get(key);
            
            if (handler) {
                e.preventDefault();
                handler(e);
            }
        });
    }

    getKeyString(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('ctrl');
        if (e.altKey) parts.push('alt');
        if (e.shiftKey) parts.push('shift');
        parts.push(e.key.toLowerCase());
        return parts.join('+');
    }

    register(key, handler, description = '') {
        this.shortcuts.set(key, handler);
        console.log(`Registered shortcut: ${key} - ${description}`);
    }

    unregister(key) {
        this.shortcuts.delete(key);
    }

    getRegisteredShortcuts() {
        return Array.from(this.shortcuts.keys());
    }
}

// ============================================
// THEME MANAGER
// ============================================

class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('dashboard-theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        
        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (this.currentTheme === 'auto') {
                    this.applyTheme('auto');
                }
            });
        }
    }

    applyTheme(theme) {
        const root = document.documentElement;
        
        switch (theme) {
            case 'dark':
                root.setAttribute('data-theme', 'dark');
                break;
            case 'light':
                root.setAttribute('data-theme', 'light');
                break;
            case 'auto':
                const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                root.setAttribute('data-theme', isDark ? 'dark' : 'light');
                break;
        }
        
        this.currentTheme = theme;
        localStorage.setItem('dashboard-theme', theme);
    }

    toggleTheme() {
        const themes = ['light', 'dark', 'auto'];
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextTheme = themes[(currentIndex + 1) % themes.length];
        this.applyTheme(nextTheme);
    }

    getCurrentTheme() {
        return this.currentTheme;
    }
}

// ============================================
// GLOBAL INSTANCES
// ============================================

// Initialize global instances
const dashboardNotifications = new NotificationSystem();
const dataManager = new DataManager();
const performanceMonitor = new PerformanceMonitor();
const keyboardShortcuts = new KeyboardShortcuts();
const themeManager = new ThemeManager();

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard Enhanced JavaScript Loaded');
    
    // Register keyboard shortcuts
    keyboardShortcuts.register('ctrl+r', () => {
        window.location.reload();
    }, 'Refresh dashboard');
    
    keyboardShortcuts.register('ctrl+t', () => {
        themeManager.toggleTheme();
    }, 'Toggle theme');
    
    keyboardShortcuts.register('ctrl+/', () => {
        showKeyboardShortcuts();
    }, 'Show keyboard shortcuts');
    
    // Performance monitoring
    performanceMonitor.startTimer('initial-render');
    
    // Add animations to existing elements
    if (DashboardConfig.ui.enableAnimations) {
        setTimeout(() => {
            document.querySelectorAll('.card').forEach((card, index) => {
                setTimeout(() => {
                    AnimationEngine.fadeIn(card);
                }, index * 100);
            });
            performanceMonitor.endTimer('initial-render');
        }, 100);
    }
    
    // Auto-refresh functionality
    if (DashboardConfig.ui.autoRefresh) {
        setInterval(() => {
            // Trigger refresh of dynamic content
            const event = new CustomEvent('dashboardRefresh');
            document.dispatchEvent(event);
        }, DashboardConfig.ui.refreshInterval);
    }
    
    // Success notification
    dashboardNotifications.show('Dashboard enhanced features loaded successfully!', 'success', 3000);
});

// ============================================
// HELPER FUNCTIONS FOR DASH CALLBACKS
// ============================================

function showKeyboardShortcuts() {
    const shortcuts = keyboardShortcuts.getRegisteredShortcuts();
    const message = `
        <div style="text-align: left;">
            <h4>Keyboard Shortcuts:</h4>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Ctrl+R:</strong> Refresh dashboard</li>
                <li><strong>Ctrl+T:</strong> Toggle theme</li>
                <li><strong>Ctrl+/:</strong> Show this help</li>
            </ul>
        </div>
    `;
    dashboardNotifications.show(message, 'info', 8000);
}

// ============================================
// ADVANCED UI ENHANCEMENTS
// ============================================

class DashboardEnhancements {
    constructor() {
        this.initializeEnhancements();
    }

    initializeEnhancements() {
        this.addLoadingStates();
        this.addTooltips();
        this.addKeyboardShortcuts();
        this.addProgressIndicators();
        this.addAutoSave();
        this.addThemeToggle();
        this.addFullscreenMode();
    }

    // Loading states for better UX
    addLoadingStates() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                if (!this.classList.contains('loading')) {
                    this.classList.add('loading');
                    this.disabled = true;
                    
                    const originalText = this.innerHTML;
                    this.innerHTML = '<span class="loading-spinner"></span> Loading...';
                    
                    // Remove loading state after 3 seconds (fallback)
                    setTimeout(() => {
                        this.classList.remove('loading');
                        this.disabled = false;
                        this.innerHTML = originalText;
                    }, 3000);
                }
            });
        });
    }

    // Enhanced tooltips
    addTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip);
            element.addEventListener('mouseleave', this.hideTooltip);
        });
    }

    showTooltip(event) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip-enhanced';
        tooltip.textContent = event.target.getAttribute('data-tooltip');
        tooltip.style.position = 'absolute';
        tooltip.style.zIndex = '10000';
        tooltip.style.pointerEvents = 'none';
        
        document.body.appendChild(tooltip);
        
        const rect = event.target.getBoundingClientRect();
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.bottom + 5) + 'px';
        
        event.target._tooltip = tooltip;
    }

    hideTooltip(event) {
        if (event.target._tooltip) {
            event.target._tooltip.remove();
            delete event.target._tooltip;
        }
    }

    // Keyboard shortcuts
    addKeyboardShortcuts() {
        document.addEventListener('keydown', function(event) {
            // Ctrl + R: Refresh data
            if (event.ctrlKey && event.key === 'r') {
                event.preventDefault();
                const refreshButton = document.getElementById('refresh-suggestions');
                if (refreshButton) refreshButton.click();
            }
            
            // Ctrl + E: Export data
            if (event.ctrlKey && event.key === 'e') {
                event.preventDefault();
                const exportButton = document.getElementById('export-csv');
                if (exportButton) exportButton.click();
            }
            
            // Ctrl + /: Focus chatbot
            if (event.ctrlKey && event.key === '/') {
                event.preventDefault();
                const chatInput = document.getElementById('chatbot-input');
                if (chatInput) chatInput.focus();
            }
            
            // Esc: Clear selections
            if (event.key === 'Escape') {
                const dropdowns = document.querySelectorAll('.Select-control');
                dropdowns.forEach(dropdown => {
                    // Clear dropdown selections if needed
                });
            }
        });
    }

    // Progress indicators for long operations
    addProgressIndicators() {
        const createProgressRing = (percentage) => {
            const radius = 30;
            const circumference = 2 * Math.PI * radius;
            const offset = circumference - (percentage / 100) * circumference;
            
            return `
                <svg class="progress-ring" width="60" height="60">
                    <circle class="progress-ring-circle"
                            cx="30" cy="30" r="${radius}"
                            style="stroke-dashoffset: ${offset}">
                    </circle>
                </svg>
            `;
        };

        // Add progress rings to KPI cards
        const kpiCards = document.querySelectorAll('.kpi-card');
        kpiCards.forEach((card, index) => {
            const percentage = Math.min((index + 1) * 20, 100);
            const progressRing = createProgressRing(percentage);
            
            const progressContainer = document.createElement('div');
            progressContainer.innerHTML = progressRing;
            progressContainer.style.position = 'absolute';
            progressContainer.style.top = '10px';
            progressContainer.style.right = '10px';
            progressContainer.style.opacity = '0.7';
            
            card.style.position = 'relative';
            card.appendChild(progressContainer);
        });
    }

    // Auto-save user preferences
    addAutoSave() {
        const savePreferences = DashboardUtils.debounce(() => {
            const preferences = {
                selectedAOs: this.getSelectedValues('ao-dropdown'),
                selectedDepts: this.getSelectedValues('dept-dropdown'),
                selectedStatuses: this.getSelectedValues('status-checklist'),
                timestamp: Date.now()
            };
            
            localStorage.setItem('dashboardPreferences', JSON.stringify(preferences));
        }, 1000);

        // Save preferences when filters change
        const filterElements = document.querySelectorAll('#ao-dropdown, #dept-dropdown, #status-checklist');
        filterElements.forEach(element => {
            element.addEventListener('change', savePreferences);
        });
    }

    getSelectedValues(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return [];
        
        // Handle different input types
        if (element.multiple) {
            return Array.from(element.selectedOptions).map(option => option.value);
        } else if (element.type === 'checkbox') {
            return element.checked;
        } else {
            return element.value;
        }
    }

    // Theme toggle functionality
    addThemeToggle() {
        const themeToggle = document.createElement('button');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        themeToggle.className = 'btn btn-outline-light btn-sm';
        themeToggle.style.position = 'fixed';
        themeToggle.style.top = '20px';
        themeToggle.style.right = '20px';
        themeToggle.style.zIndex = '10000';
        themeToggle.style.borderRadius = '50%';
        themeToggle.style.width = '40px';
        themeToggle.style.height = '40px';
        
        themeToggle.addEventListener('click', this.toggleTheme);
        document.body.appendChild(themeToggle);
    }

    toggleTheme() {
        const body = document.body;
        const isDark = body.classList.contains('dark-theme');
        
        if (isDark) {
            body.classList.remove('dark-theme');
            this.innerHTML = '<i class="fas fa-moon"></i>';
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.add('dark-theme');
            this.innerHTML = '<i class="fas fa-sun"></i>';
            localStorage.setItem('theme', 'dark');
        }
    }

    // Fullscreen mode
    addFullscreenMode() {
        const fullscreenToggle = document.createElement('button');
        fullscreenToggle.innerHTML = '<i class="fas fa-expand"></i>';
        fullscreenToggle.className = 'btn btn-outline-secondary btn-sm';
        fullscreenToggle.style.position = 'fixed';
        fullscreenToggle.style.top = '70px';
        fullscreenToggle.style.right = '20px';
        fullscreenToggle.style.zIndex = '10000';
        fullscreenToggle.style.borderRadius = '50%';
        fullscreenToggle.style.width = '40px';
        fullscreenToggle.style.height = '40px';
        
        fullscreenToggle.addEventListener('click', this.toggleFullscreen);
        document.body.appendChild(fullscreenToggle);
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            this.innerHTML = '<i class="fas fa-compress"></i>';
        } else {
            document.exitFullscreen();
            this.innerHTML = '<i class="fas fa-expand"></i>';
        }
    }
}

// ============================================
// REAL-TIME DATA UPDATES
// ============================================

class RealTimeUpdates {
    constructor() {
        this.updateInterval = null;
        this.wsConnection = null;
        this.initializeRealTime();
    }

    initializeRealTime() {
        if (DashboardConfig.ui.autoRefresh) {
            this.startPeriodicUpdates();
        }
        
        // Try to establish WebSocket connection for real-time updates
        this.attemptWebSocketConnection();
    }

    startPeriodicUpdates() {
        this.updateInterval = setInterval(() => {
            this.refreshDashboardData();
        }, DashboardConfig.ui.refreshInterval);
    }

    stopPeriodicUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    refreshDashboardData() {
        // Trigger refresh of key components
        const refreshButton = document.getElementById('refresh-suggestions');
        if (refreshButton) {
            refreshButton.click();
        }

        // Show refresh indicator
        this.showRefreshIndicator();
    }

    showRefreshIndicator() {
        const indicator = document.createElement('div');
        indicator.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Updating...';
        indicator.className = 'refresh-indicator';
        indicator.style.position = 'fixed';
        indicator.style.top = '20px';
        indicator.style.left = '50%';
        indicator.style.transform = 'translateX(-50%)';
        indicator.style.background = 'rgba(13, 71, 161, 0.9)';
        indicator.style.color = 'white';
        indicator.style.padding = '0.5rem 1rem';
        indicator.style.borderRadius = '0.5rem';
        indicator.style.zIndex = '10000';
        indicator.style.fontSize = '0.875rem';
        indicator.style.fontWeight = '600';

        document.body.appendChild(indicator);

        setTimeout(() => {
            indicator.remove();
        }, 2000);
    }

    attemptWebSocketConnection() {
        try {
            this.wsConnection = new WebSocket('ws://localhost:8000/ws');
            
            this.wsConnection.onopen = () => {
                console.log('✅ WebSocket connection established');
            };
            
            this.wsConnection.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleRealTimeUpdate(data);
            };
            
            this.wsConnection.onerror = () => {
                console.log('⚠️ WebSocket connection failed, using polling instead');
            };
            
        } catch (error) {
            console.log('⚠️ WebSocket not available, using polling instead');
        }
    }

    handleRealTimeUpdate(data) {
        // Handle different types of real-time updates
        switch (data.type) {
            case 'kpi_update':
                this.updateKPICards(data.payload);
                break;
            case 'new_vulnerability':
                this.showNotification('New vulnerability detected!', 'warning');
                break;
            case 'risk_threshold_exceeded':
                this.showNotification('Risk threshold exceeded!', 'danger');
                break;
        }
    }

    updateKPICards(data) {
        // Update KPI cards with new data
        Object.keys(data).forEach(kpiId => {
            const element = document.getElementById(kpiId);
            if (element) {
                element.textContent = data[kpiId];
                element.classList.add('highlight-update');
                setTimeout(() => {
                    element.classList.remove('highlight-update');
                }, 1000);
            }
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = `
            <i class="fas fa-bell me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        notification.style.position = 'fixed';
        notification.style.top = '80px';
        notification.style.right = '20px';
        notification.style.zIndex = '10000';
        notification.style.minWidth = '300px';
        notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

// ============================================
// PERFORMANCE MONITORING
// ============================================

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoadTime: 0,
            apiResponseTimes: [],
            renderTimes: [],
            errorCount: 0
        };
        
        this.initializeMonitoring();
    }

    initializeMonitoring() {
        // Monitor page load time
        window.addEventListener('load', () => {
            this.metrics.pageLoadTime = performance.now();
            console.log(`📊 Page loaded in ${this.metrics.pageLoadTime.toFixed(2)}ms`);
        });

        // Monitor API calls
        this.interceptFetch();
        
        // Monitor render performance
        this.observeRenderTimes();
        
        // Monitor errors
        this.setupErrorTracking();
    }

    interceptFetch() {
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            const startTime = performance.now();
            return originalFetch.apply(this, args)
                .then(response => {
                    const endTime = performance.now();
                    this.metrics.apiResponseTimes.push(endTime - startTime);
                    return response;
                })
                .catch(error => {
                    this.metrics.errorCount++;
                    throw error;
                });
        };
    }

    observeRenderTimes() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach((entry) => {
                    if (entry.entryType === 'measure') {
                        this.metrics.renderTimes.push(entry.duration);
                    }
                });
            });
            
            observer.observe({entryTypes: ['measure']});
        }
    }

    setupErrorTracking() {
        window.addEventListener('error', (event) => {
            this.metrics.errorCount++;
            console.error('Dashboard Error:', event.error);
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.metrics.errorCount++;
            console.error('Unhandled Promise Rejection:', event.reason);
        });
    }

    getPerformanceReport() {
        const avgApiTime = this.metrics.apiResponseTimes.length > 0 
            ? this.metrics.apiResponseTimes.reduce((a, b) => a + b, 0) / this.metrics.apiResponseTimes.length 
            : 0;
            
        return {
            pageLoadTime: this.metrics.pageLoadTime,
            averageApiResponseTime: avgApiTime,
            totalApiCalls: this.metrics.apiResponseTimes.length,
            errorCount: this.metrics.errorCount,
            memoryUsage: performance.memory ? {
                used: (performance.memory.usedJSHeapSize / 1024 / 1024).toFixed(2) + ' MB',
                total: (performance.memory.totalJSHeapSize / 1024 / 1024).toFixed(2) + ' MB'
            } : 'Not available'
        };
    }
}

// ============================================
// INITIALIZATION
// ============================================

// Initialize all enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Dashboard Enhancements...');
    
    // Initialize enhancement modules
    window.dashboardEnhancements = new DashboardEnhancements();
    window.realTimeUpdates = new RealTimeUpdates();
    window.performanceMonitor = new PerformanceMonitor();
    
    // Load saved preferences
    const savedPreferences = localStorage.getItem('dashboardPreferences');
    if (savedPreferences) {
        try {
            const preferences = JSON.parse(savedPreferences);
            console.log('📋 Loaded saved preferences:', preferences);
            // Apply saved preferences here
        } catch (error) {
            console.warn('⚠️ Could not load saved preferences:', error);
        }
    }
    
    // Apply saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
    
    console.log('✅ Dashboard enhancements initialized successfully!');
});

// Export for external use
window.DashboardAPI = {
    utils: DashboardUtils,
    enhancements: () => window.dashboardEnhancements,
    realTime: () => window.realTimeUpdates,
    performance: () => window.performanceMonitor,
    config: DashboardConfig
};
