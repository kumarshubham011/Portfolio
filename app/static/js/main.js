/**
 * Portfolio JavaScript - Minimal
 */

(function() {
    'use strict';

    // Mobile Navigation
    function initMobileNav() {
        const toggle = document.querySelector('.nav-toggle');
        const navLinks = document.querySelector('.nav-links');
        
        if (!toggle || !navLinks) return;
        
        toggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
        
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.nav')) {
                navLinks.classList.remove('active');
            }
        });
    }

    // Focus Mode (Shift + F)
    function initFocusMode() {
        const indicator = document.getElementById('focus-indicator');
        let focusModeActive = false;
        
        // Restore saved preference
        try {
            if (localStorage.getItem('focusMode') === 'true') {
                focusModeActive = true;
                document.body.classList.add('focus-mode');
            }
        } catch (e) {}
        
        document.addEventListener('keydown', function(e) {
            if (e.shiftKey && (e.key === 'F' || e.key === 'f')) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    return;
                }
                
                focusModeActive = !focusModeActive;
                document.body.classList.toggle('focus-mode', focusModeActive);
                
                if (indicator) {
                    indicator.classList.add('visible');
                    indicator.textContent = focusModeActive ? 'Focus Mode On' : 'Focus Mode Off';
                    
                    setTimeout(function() {
                        indicator.classList.remove('visible');
                    }, 2000);
                }
                
                try {
                    localStorage.setItem('focusMode', focusModeActive);
                } catch (e) {}
            }
        });
    }

    // Delete Confirmation
    function initDeleteConfirmation() {
        const deleteButtons = document.querySelectorAll('[data-confirm]');
        
        deleteButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                const message = this.dataset.confirm || 'Are you sure?';
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        });
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        initMobileNav();
        initFocusMode();
        initDeleteConfirmation();
        
        console.log('Portfolio loaded. Press Shift+F for focus mode.');
    });

})();
