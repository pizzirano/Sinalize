window.addEventListener('DOMContentLoaded', () => {
  const track = document.getElementById('carousel-track');
  if (track) {
    const items = Array.from(track.children);
    // Clona os itens uma vez para criar um loop visual contínuo
    items.forEach((item) => {
      const clone = item.cloneNode(true);
      track.appendChild(clone);
    });

    // Aplica a animação
    track.style.animation = 'scroll-carousel 20s linear infinite';
  }
});