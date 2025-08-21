document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll(".card");

  cards.forEach(card => {
    card.addEventListener("click", () => {
      const link = card.getAttribute("data-link");
      if (link) {
        window.location.href = link; // navigate to respective page
      }
    });
  });
});