// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Enhanced Hamburger Menu
    const hamburger = document.getElementById('hamburger');
    const navLinksWrapper = document.getElementById('navLinksWrapper');
    
    if (hamburger && navLinksWrapper) {
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            navLinksWrapper.classList.toggle('active');
            const icon = hamburger.querySelector('i');
            if (navLinksWrapper.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
                document.body.style.overflow = 'hidden';
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (navLinksWrapper.classList.contains('active') && 
                !navLinksWrapper.contains(event.target) && 
                !hamburger.contains(event.target)) {
                navLinksWrapper.classList.remove('active');
                hamburger.querySelector('i').classList.remove('fa-times');
                hamburger.querySelector('i').classList.add('fa-bars');
                document.body.style.overflow = '';
            }
        });
        
        // Close menu when a link is clicked (mobile)
        const navLinks = document.querySelectorAll('.nav-links a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 992) {
                    navLinksWrapper.classList.remove('active');
                    hamburger.querySelector('i').classList.remove('fa-times');
                    hamburger.querySelector('i').classList.add('fa-bars');
                    document.body.style.overflow = '';
                }
            });
        });
    }
    
    // Auto-hide flash messages with animation
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => { if(alert.parentNode) alert.remove(); }, 300);
        });
    }, 4000);
    
    // Close flash message on click
    document.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
    
    // Close modals when clicking outside
    window.onclick = function(event) {
        const modals = document.querySelectorAll('.upload-modal, .search-modal, .stats-modal');
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    };
    
    // Smooth scroll to top button (dynamic)
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.className = 'scroll-top-btn';
    scrollBtn.style.cssText = `
        position: fixed; bottom: 20px; right: 20px; background: var(--primary); color: white;
        border: none; width: 45px; height: 45px; border-radius: 50%; cursor: pointer;
        display: none; z-index: 1000; transition: all 0.3s; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) scrollBtn.style.display = 'block';
        else scrollBtn.style.display = 'none';
    });
    
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // Add loading animation to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitBtn.disabled = true;
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 2000);
            }
        });
    });
    
    // Category filter enhancement
    const categorySelect = document.querySelector('select[name="category"]');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const searchForm = document.getElementById('searchForm');
            if (searchForm) searchForm.submit();
        });
    }
});

// Additional animation keyframes
const styleSheet = document.createElement("style");
styleSheet.textContent = `
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .scroll-top-btn:hover { transform: scale(1.1); background: var(--primary-dark); }
    .book-card { animation: fadeInUp 0.4s ease; }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(styleSheet);