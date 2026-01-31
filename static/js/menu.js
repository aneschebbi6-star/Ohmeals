/**
 * menu.js - Menu page interactions
 * OHMEALS - Traiteur Marocain
 */

document.addEventListener('DOMContentLoaded', function () {
    // Product card hover effects
    const productBoxes = document.querySelectorAll('.food_section .box');

    productBoxes.forEach(function (box) {
        // Add smooth hover animation
        box.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });

        box.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });

    // Filter menu animation enhancement
    const filterItems = document.querySelectorAll('.filters_menu li');

    filterItems.forEach(function (item) {
        item.addEventListener('click', function () {
            // Remove active class from all
            filterItems.forEach(function (li) {
                li.classList.remove('active');
            });
            // Add active class to clicked
            this.classList.add('active');
        });
    });

    console.log('Menu page loaded - OHMEALS');
});
