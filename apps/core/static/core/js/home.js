document.querySelectorAll(".js-start").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector("#steps").scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

const track = document.querySelector("#carouselTrack");
const cards = Array.from(track.querySelectorAll(".carousel-card"));
const prevBtn = document.querySelector("#prevBtn");
const nextBtn = document.querySelector("#nextBtn");
const dotsWrap = document.querySelector("#dots");
let currentIndex = 0;

cards.forEach((_, index) => {
  const dot = document.createElement("button");
  dot.type = "button";
  dot.className = "h-2.5 w-2.5 rounded-full bg-stone-300 transition-all";
  dot.setAttribute("aria-label", `前往第 ${index + 1} 張`);
  dot.addEventListener("click", () => goTo(index));
  dotsWrap.appendChild(dot);
});

const dots = Array.from(dotsWrap.children);

function updateCarousel() {
  track.style.transform = window.innerWidth < 768 ? `translateX(-${currentIndex * 100}%)` : "";
  dots.forEach((dot, index) => {
    dot.className = index === currentIndex
      ? "h-2.5 w-6 rounded-full bg-blue-600 transition-all"
      : "h-2.5 w-2.5 rounded-full bg-stone-300 transition-all";
    dot.setAttribute("aria-current", index === currentIndex ? "true" : "false");
  });
}

function goTo(index) {
  currentIndex = (index + cards.length) % cards.length;
  updateCarousel();
}

prevBtn.addEventListener("click", () => goTo(currentIndex - 1));
nextBtn.addEventListener("click", () => goTo(currentIndex + 1));
window.addEventListener("resize", updateCarousel);

let touchStartX = null;
track.addEventListener("touchstart", (event) => { touchStartX = event.touches[0].clientX; }, { passive: true });
track.addEventListener("touchend", (event) => {
  if (touchStartX === null || window.innerWidth >= 768) return;
  const delta = event.changedTouches[0].clientX - touchStartX;
  if (Math.abs(delta) > 45) goTo(delta < 0 ? currentIndex + 1 : currentIndex - 1);
  touchStartX = null;
}, { passive: true });

updateCarousel();
