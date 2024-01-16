document.addEventListener("DOMContentLoaded", function() {
    let slideIndex = 0;
    showSlides();

    function showSlides() {
    let slides = document.getElementsByClassName("slideshow-image");

    // Check if there are slides and if slideIndex is within valid range
    if (slides.length > 0) {
        // Hide all slides
        for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
        }

        // Increment slideIndex and check if it's within range
        slideIndex++;
        if (slideIndex > slides.length) {
        slideIndex = 1;
        }

        // Display the current slide
        slides[slideIndex - 1].style.display = "block";

        // Set the timeout for the next slide
        setTimeout(showSlides, 7500);
    } else {
        console.error("No slides found with class 'slideshow-image'");
    }
    }
});