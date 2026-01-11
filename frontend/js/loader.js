// js/loader.js - FINAL MASTER VERSION

async function loadComponent(targetId, fileName) {
    const target = document.getElementById(targetId);
    if (!target) return; // Skip if element doesn't exist on this page

    try {
        const response = await fetch(`components/${fileName}`);
        if (!response.ok) throw new Error(`Failed to load ${fileName}`);
        const html = await response.text();
        target.innerHTML = html;

        // Special Logic: Highlight active link if Navbar is loaded
        if (fileName === 'navbar.html') highlightActiveLink();
        
    } catch (error) {
        console.error(`Error loading ${fileName}:`, error);
    }
}

function highlightActiveLink() {
    const currentPage = window.location.pathname.split("/").pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if(link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
}

// MAIN EXECUTION: Load all parts of the website
document.addEventListener("DOMContentLoaded", async () => {
    
    // Use Promise.all to load everything in parallel (Faster)
    await Promise.all([
        // --- 1. SHARED GLOBAL COMPONENTS ---
        loadComponent('navbar-target', 'navbar.html'),
        loadComponent('footer-target', 'footer.html'),
        loadComponent('urgency-popup-target', 'urgency_popup.html'),
        loadComponent('cta_banner-target', 'cta_banner.html'),

        // --- 2. HOME PAGE COMPONENTS ---
        loadComponent('home_hero-target', 'home_hero.html'),
        loadComponent('marquee-target', 'marquee.html'),     // New
        loadComponent('highlights-target', 'highlights.html'),
        loadComponent('features-target', 'features.html'),
        loadComponent('hygiene-target', 'hygiene.html'),     // New
        loadComponent('testimonials-target', 'testimonials.html'),
        loadComponent('blog-target', 'blog.html'),           // New
        loadComponent("stats-target", "stats.html"),
        loadComponent('final_cta_home-target', 'final_cta_home.html'),  
        loadComponent("services_overview-target", "services_overview.html"),

        // --- 3. MENU PAGE COMPONENTS ---
        loadComponent('services-target', 'services.html'),
        loadComponent('signature-target', 'signature.html'),
        loadComponent('pricing-target', 'pricing.html'),
        loadComponent('menu_book-target', 'menu_book.html'),
        loadComponent('menu_cta-target', 'menu_cta.html'),
        // --- 4. ABOUT PAGE COMPONENTS ---
        loadComponent('story-target', 'story.html'),
        loadComponent('team-target', 'team.html'),
        loadComponent('detailed_why-target', 'detailed_why.html'),

        // --- 5. CONTACT PAGE COMPONENTS ---
        loadComponent('contact_form-target', 'contact_form.html'), // Essential
        loadComponent('map-target', 'map.html'),                   // New Google Map
        loadComponent('faq-target', 'faq.html'),

        // --- 6. GALLERY PAGE COMPONENTS ---
        loadComponent('gallery-target', 'gallery_grid.html'),
        loadComponent('contact_grid-target', 'contact_grid.html'),
        loadComponent('map-target', 'map.html'),
        loadComponent('estimator-target', 'estimator.html'),
        
        loadComponent('urgency-popup-target', 'urgency_popup.html'),

        loadComponent('custom_menu-target', 'custom_menu.html'),



    ]);

    // --- 7. RE-TRIGGER ANIMATIONS (AOS) ---
    // Because content was loaded dynamically, we must tell AOS to look again.
    if (typeof AOS !== 'undefined') {
        setTimeout(() => {
            AOS.refreshHard(); 
            AOS.init();
        }, 500); 
    }
});

function updateNavbarAuth() {
    const token = localStorage.getItem('authToken');
    const username = localStorage.getItem('username');
    
    // Find the container where you want to show Login/Logout buttons
    // You might need to add <div id="auth-links"></div> to your navbar HTML
    const authContainer = document.getElementById('auth-links'); 

    if (!authContainer) return; // Stop if navbar isn't loaded yet

    if (token) {
        // User is Logged In
        authContainer.innerHTML = `
            <span style="margin-right: 15px; font-weight: bold;">Hello, ${username}</span>
            <button onclick="logout()" class="btn-gold" style="padding: 5px 15px;">Logout</button>
        `;
    } else {
        // User is Logged Out
        authContainer.innerHTML = `
            <a href="login.html" style="margin-right: 15px;">Login</a>
            <a href="signup.html" class="btn-gold" style="padding: 5px 15px;">Sign Up</a>
        `;
    }
}

function logout() {
    // 1. Remove the token
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    
    // 2. Refresh the page to update the UI
    window.location.reload();
}

// Run this check every time the page loads
document.addEventListener('DOMContentLoaded', updateNavbarAuth);