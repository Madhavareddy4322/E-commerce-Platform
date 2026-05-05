// static/js/script.js

document.addEventListener("DOMContentLoaded", () => {
    const addToCartForms = document.querySelectorAll('form[action*="cart/add"]');
    addToCartForms.forEach(form => {
        form.addEventListener("submit", () => {
            console.log("Adding to cart...");
        });
    });
});
