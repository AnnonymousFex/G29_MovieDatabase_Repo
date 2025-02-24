// Toggle mobile menu
const mobileMenu = document.getElementById('mobile-menu');
const navLinks = document.querySelector('.nav-links');
const searchIcon = document.getElementById('search-icon');
const searchBar = document.getElementById('search-bar');

mobileMenu.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    mobileMenu.classList.toggle('active');
});

// Toggle search bar
searchIcon.addEventListener('click', () => {
    searchBar.classList.toggle('active');
    if (searchBar.classList.contains('active')) {
        searchBar.focus();
    } else {
        searchBar.value = '';
    }
});

// Carousel Functionality
const carouselItems = document.querySelectorAll('.carousel-item');
let currentIndex = 0;

function showSlide(index) {
    carouselItems.forEach((item) => {
        item.classList.remove('active', 'next', 'prev');
    });

    carouselItems[currentIndex].classList.add('prev');
    carouselItems[index].classList.add('next');

    setTimeout(() => {
        carouselItems[currentIndex].classList.remove('prev');
        carouselItems[index].classList.remove('next');
        carouselItems[index].classList.add('active');
        currentIndex = index;
    }, 10);
}

function prevSlide() {
    const newIndex = (currentIndex - 1 + carouselItems.length) % carouselItems.length;
    showSlide(newIndex);
}

function nextSlide() {
    const newIndex = (currentIndex + 1) % carouselItems.length;
    showSlide(newIndex);
}

let autoPlayInterval;

function startAutoPlay() {
    autoPlayInterval = setInterval(nextSlide, 5000);
}

function stopAutoPlay() {
    clearInterval(autoPlayInterval);
}

startAutoPlay();

const carousel = document.getElementById('carouselVideoExample');
carousel.addEventListener('mouseenter', stopAutoPlay);
carousel.addEventListener('mouseleave', startAutoPlay);

// Movie Carousel Functionality
document.addEventListener("DOMContentLoaded", function () {
    const container1 = document.querySelectorAll(".movies-container")[0];
    const leftArrow1 = document.getElementById("left-arrow-1");
    const rightArrow1 = document.getElementById("right-arrow-1");

    if (container1 && leftArrow1 && rightArrow1) {
        rightArrow1.addEventListener("click", function () {
            container1.scrollBy({ left: 300, behavior: "smooth" });
        });

        leftArrow1.addEventListener("click", function () {
            container1.scrollBy({ left: -300, behavior: "smooth" });
        });
    }

    const container2 = document.querySelectorAll(".movies-container")[1];
    const leftArrow2 = document.getElementById("left-arrow-2");
    const rightArrow2 = document.getElementById("right-arrow-2");

    if (container2 && leftArrow2 && rightArrow2) {
        rightArrow2.addEventListener("click", function () {
            container2.scrollBy({ left: 300, behavior: "smooth" });
        });

        leftArrow2.addEventListener("click", function () {
            container2.scrollBy({ left: -300, behavior: "smooth" });
        });
    }

    const container3 = document.querySelectorAll(".movies-container")[2];
    const leftArrow3 = document.getElementById("left-arrow-3");
    const rightArrow3 = document.getElementById("right-arrow-3");

    if (container3 && leftArrow3 && rightArrow3) {
        rightArrow3.addEventListener("click", function () {
            container3.scrollBy({ left: 300, behavior: "smooth" });
        });

        leftArrow3.addEventListener("click", function () {
            container3.scrollBy({ left: -300, behavior: "smooth" });
        });
    }
});



document.addEventListener("DOMContentLoaded", function () {
    // Get the container and arrows for the "Explore What's Streaming" section
    const exploreStreamingContainer = document.getElementById("explore-streaming-container");
    const leftArrow4 = document.getElementById("left-arrow-4");
    const rightArrow4 = document.getElementById("right-arrow-4");

    // Add event listeners for smooth scrolling
    if (exploreStreamingContainer && leftArrow4 && rightArrow4) {
        // Scroll right
        rightArrow4.addEventListener("click", function () {
            exploreStreamingContainer.scrollBy({ left: 300, behavior: "smooth" });
        });

        // Scroll left
        leftArrow4.addEventListener("click", function () {
            exploreStreamingContainer.scrollBy({ left: -300, behavior: "smooth" });
        });
    }
});


// Video Carousel Functionality
document.addEventListener("DOMContentLoaded", function () {
    const videosContainer = document.querySelector(".videos-container");
    const leftArrowVideo = document.getElementById("left-arrow-video");
    const rightArrowVideo = document.getElementById("right-arrow-video");

    if (videosContainer && leftArrowVideo && rightArrowVideo) {
        rightArrowVideo.addEventListener("click", function () {
            videosContainer.scrollBy({ left: 300, behavior: "smooth" });
        });

        leftArrowVideo.addEventListener("click", function () {
            videosContainer.scrollBy({ left: -300, behavior: "smooth" });
        });
    }
});

// Search Bar Functionality
document.addEventListener("DOMContentLoaded", function () {
    const searchBar = document.getElementById("search-bar");
    const resultsContainer = document.getElementById("search-results");

    if (!searchBar || !resultsContainer) {
        console.error("Search elements not found!");
        return;
    }

    searchBar.addEventListener("input", function (e) {
        const query = e.target.value.trim();
        if (query.length < 3) {
            resultsContainer.innerHTML = "";
            resultsContainer.style.display = "none";
            return;
        }

        fetch(`/search?q=${query}`)
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = "";

                if (data.length > 0) {
                    data.forEach(movie => {
                        const movieElement = document.createElement("div");
                        movieElement.className = "search-result-item";
                        movieElement.innerHTML = `
                            <img src="${movie.Poster}" alt="${movie.Title}">
                            <div>
                                <h3>${movie.Title}</h3>
                                <p>${movie.Year}</p>
                            </div>
                        `;
                        resultsContainer.appendChild(movieElement);
                    });
                    resultsContainer.style.display = "block";
                } else {
                    resultsContainer.innerHTML = "<p>No results found.</p>";
                    resultsContainer.style.display = "block";
                }
            })
            .catch(error => {
                console.error("Error fetching search results:", error);
            });
    });

    searchBar.addEventListener("click", function (e) {
        if (resultsContainer.innerHTML.trim() !== "") {
            resultsContainer.style.display =
                resultsContainer.style.display === "block" ? "none" : "block";
        }
        e.stopPropagation();
    });

    document.addEventListener("click", function (e) {
        if (!searchBar.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.style.display = "none";
        }
    });
});