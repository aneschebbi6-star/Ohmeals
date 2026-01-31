/**
 * index.js - Homepage interactions
 * OHMEALS - Traiteur Marocain
 */

document.addEventListener('DOMContentLoaded', function () {
    // Product card hover effects for homepage
    const productBoxes = document.querySelectorAll('.food_section .box');

    productBoxes.forEach(function (box) {
        // Add smooth hover animation
        box.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 30px rgba(0,0,0,0.3)';
            this.style.transition = 'all 0.3s ease';
        });

        box.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    console.log('Homepage loaded - OHMEALS');
});
