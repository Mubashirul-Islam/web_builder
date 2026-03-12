// Mobile menu toggle
const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

// Contact form submit simulation
const form = document.getElementById('contact-form');
const formMessage = document.getElementById('form-message');

form.addEventListener('submit', (e) => {
    e.preventDefault();
    formMessage.textContent = "Thank you! Your message has been sent.";
    form.reset();
    setTimeout(() => {
        formMessage.textContent = "";
    }, 3000);
});