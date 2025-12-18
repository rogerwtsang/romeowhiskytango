// Personal Website - Main JavaScript

// ======================================
// Smooth Scrolling for Navigation Links
// ======================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ======================================
// Active Navigation State on Scroll
// ======================================
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('nav a');

window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.style.color = '';
        if (link.getAttribute('href').slice(1) === current) {
            link.style.color = '#e74c3c';
        }
    });
});

// ======================================
// Multi-Step Contact Form
// ======================================
const contactForm = document.getElementById('contactForm');

if (contactForm) {
    let currentStep = 1;
    const totalSteps = 3;
    
    const nextBtn = document.getElementById('nextBtn');
    const backBtn = document.getElementById('backBtn');
    const submitBtn = document.getElementById('submitBtn');
    const successMessage = document.getElementById('successMessage');
    
    function updateStep() {
        // Update form steps
        document.querySelectorAll('.form-step').forEach((step, index) => {
            step.classList.remove('active');
            if (index + 1 === currentStep) {
                step.classList.add('active');
            }
        });
        
        // Update progress dots
        document.querySelectorAll('.progress-dot').forEach((dot, index) => {
            dot.classList.remove('active');
            if (index < currentStep) {
                dot.classList.add('active');
            }
        });
        
        // Update buttons
        if (backBtn) backBtn.style.display = currentStep > 1 ? 'block' : 'none';
        if (nextBtn) nextBtn.style.display = currentStep < totalSteps ? 'block' : 'none';
        if (submitBtn) submitBtn.style.display = currentStep === totalSteps ? 'block' : 'none';
    }
    
    function validateCurrentStep() {
        const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
        const input = currentStepElement.querySelector('input, textarea');
        return input.value.trim() !== '';
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (validateCurrentStep()) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    updateStep();
                }
            } else {
                const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
                const input = currentStepElement.querySelector('input, textarea');
                input.focus();
            }
        });
    }
    
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                updateStep();
            }
        });
    }
    
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        if (validateCurrentStep()) {
            // For Netlify forms, just submit normally
            if (contactForm.hasAttribute('data-netlify')) {
                contactForm.submit();
                return;
            }
            
            // Otherwise show success message
            contactForm.style.display = 'none';
            if (successMessage) successMessage.style.display = 'block';
            
            // Reset form after 5 seconds
            setTimeout(() => {
                contactForm.reset();
                currentStep = 1;
                updateStep();
                contactForm.style.display = 'block';
                if (successMessage) successMessage.style.display = 'none';
            }, 5000);
        }
    });
    
    // Allow Enter key to advance
    document.querySelectorAll('.form-step input').forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (nextBtn) nextBtn.click();
            }
        });
    });
    
    // Initialize form state
    updateStep();
}

// ======================================
// Mobile Menu Toggle (Optional)
// ======================================
// Uncomment if you add a mobile hamburger menu later
/*
const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
const mobileNav = document.querySelector('nav ul');

if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        mobileNav.classList.toggle('open');
        mobileMenuToggle.classList.toggle('open');
    });
}
*/