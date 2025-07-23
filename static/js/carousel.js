document.addEventListener('DOMContentLoaded', function() {
    const carouselWindow = document.querySelector('.cv-carousel-window');
    if (!carouselWindow) {
        return; // No hay carrusel en esta página, no hacer nada.
    }

    const track = carouselWindow.querySelector('.cv-carousel-track');
    const dotsNav = document.querySelector('.carousel-dots');
    let originalCards = Array.from(track.children);

    if (originalCards.length === 0) {
        return; // No hay tarjetas que mostrar.
    }

    // --- CLONACIÓN ---
    // Clonar al final
    originalCards.forEach(card => {
        track.appendChild(card.cloneNode(true));
    });
    // Clonar al principio
    originalCards.slice().reverse().forEach(card => {
        track.insertBefore(card.cloneNode(true), track.firstChild);
    });

    let allCards = Array.from(track.children);
    let cardWidth;
    let currentIndex = originalCards.length;
    let isTransitioning = false;
    let autoPlayInterval;

    function initializeCarousel() {
        cardWidth = originalCards[0].getBoundingClientRect().width + 20; // Ancho + margen (10px a cada lado)
        
        // Posicionar el carrusel en el inicio real sin animación
        track.style.transition = 'none';
        track.style.transform = `translateX(-${cardWidth * currentIndex}px)`;
        
        // Forzar al navegador a aplicar el cambio antes de reactivar la transición
        track.offsetHeight; 
        
        track.style.transition = 'transform 0.5s ease-in-out';
        
        startAutoPlay();
    }

    // --- PUNTOS DE NAVEGACIÓN ---
    dotsNav.innerHTML = '';
    originalCards.forEach((_, index) => {
        const button = document.createElement('button');
        button.classList.add('dot');
        if (index === 0) button.classList.add('active');
        button.addEventListener('click', () => {
            moveToSlide(index + originalCards.length);
        });
        dotsNav.appendChild(button);
    });
    const dots = Array.from(dotsNav.children);

    // --- FUNCIONES DE MOVIMIENTO ---
    function moveToSlide(index) {
        if (isTransitioning) return;
        isTransitioning = true;
        track.style.transform = `translateX(-${cardWidth * index}px)`;
        currentIndex = index;
        updateDots();
    }

    function updateDots() {
        const currentDotIndex = (currentIndex - originalCards.length + originalCards.length) % originalCards.length;
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentDotIndex);
        });
    }

    function moveToNext() {
        moveToSlide(currentIndex + 1);
    }

    // --- SALTO INVISIBLE ---
    track.addEventListener('transitionend', () => {
        isTransitioning = false;
        if (currentIndex >= originalCards.length * 2) {
            track.style.transition = 'none';
            currentIndex = originalCards.length;
            track.style.transform = `translateX(-${cardWidth * currentIndex}px)`;
            track.offsetHeight; // Forzar reflow
            track.style.transition = 'transform 0.5s ease-in-out';
        }
        if (currentIndex <= 0) {
            track.style.transition = 'none';
            currentIndex = originalCards.length;
            track.style.transform = `translateX(-${cardWidth * currentIndex}px)`;
            track.offsetHeight; // Forzar reflow
            track.style.transition = 'transform 0.5s ease-in-out';
        }
    });

    // --- AUTO-PLAY ---
    function startAutoPlay() {
        stopAutoPlay(); // Limpiar cualquier intervalo anterior
        autoPlayInterval = setInterval(moveToNext, 4000);
    }

    function stopAutoPlay() {
        clearInterval(autoPlayInterval);
    }

    carouselWindow.addEventListener('mouseenter', stopAutoPlay);
    carouselWindow.addEventListener('mouseleave', startAutoPlay);

    // --- INICIALIZACIÓN ---
    // Esperar a que las imágenes se carguen para evitar cálculos de tamaño incorrectos
    window.addEventListener('load', initializeCarousel);
});