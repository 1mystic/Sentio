document.addEventListener('DOMContentLoaded', () => {
    // Initialize all components after the DOM is loaded
    lucide.createIcons();
    initModals();
    initTabs();
    initDropdowns();
});

/**
 * Initializes all modal components
 */
function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal-trigger]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.getAttribute('data-modal-trigger');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('is-visible');
            }
        });
    });

    const modalClosers = document.querySelectorAll('[data-modal-close]');
    modalClosers.forEach(closer => {
        closer.addEventListener('click', () => {
            const modal = closer.closest('[data-modal]');
            if (modal) {
                modal.classList.remove('is-visible');
            }
        });
    });

    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (event) => {
            if (event.target === overlay) {
                overlay.classList.remove('is-visible');
            }
        });
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.is-visible').forEach(modal => {
                modal.classList.remove('is-visible');
            });
        }
    });
}

/**
 * Initializes all tab components
 */
function initTabs() {
    const tabsContainers = document.querySelectorAll('.tabs-container');

    tabsContainers.forEach(container => {
        const tabNav = container.querySelector('.tabs__nav');
        const tabButtons = container.querySelectorAll('.tabs__button');
        const tabPanels = container.querySelectorAll('.tabs__panel');

        tabNav.addEventListener('click', (e) => {
            const clickedTab = e.target.closest('button');
            if (!clickedTab) return;

            tabButtons.forEach(button => button.classList.remove('active'));
            clickedTab.classList.add('active');

            const targetPanelId = clickedTab.dataset.tabTarget;
            const targetPanel = container.querySelector(targetPanelId);

            tabPanels.forEach(panel => panel.classList.remove('active'));
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

/**
 * Initializes all dropdown components
 */
function initDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('[data-dropdown-toggle]');
        toggle.addEventListener('click', () => {
            dropdown.classList.toggle('is-open');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('is-open');
            }
        });
    });
}

/**
 * Shows a toast notification
 * @param {object} options - The toast options.
 * @param {string} options.type - 'success', 'error', or 'warning'.
 * @param {string} options.title - The title of the toast.
 * @param {string} options.message - The body message of the toast.
 */
function showToast({ type = 'success', title, message }) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    
    const iconMap = {
        success: 'check-circle-2',
        error: 'alert-circle',
        warning: 'alert-triangle'
    };
    
    toast.innerHTML = `
        <div class="toast__indicator"></div>
        <div class="toast__icon">
            <i data-lucide="${iconMap[type] || 'info'}"></i>
        </div>
        <div class="toast__body">
            <p class="toast__title">${title}</p>
            <p class="toast__message">${message}</p>
        </div>
    `;
    
    container.appendChild(toast);
    lucide.createIcons(); // Re-render icons for the new element

    // Automatically remove toast after 5 seconds
    setTimeout(() => {
        toast.classList.add('is-closing');
        toast.addEventListener('animationend', () => toast.remove());
    }, 5000);
}