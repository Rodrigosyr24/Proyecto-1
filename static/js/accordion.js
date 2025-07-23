document.addEventListener('DOMContentLoaded', function () {
    const accordionContainer = document.querySelector('.accordion-filters');

    if (!accordionContainer) {
        return; // Si no hay acordeón en la página, no hacer nada
    }

    const accordionItems = accordionContainer.querySelectorAll('.accordion-item');

    accordionItems.forEach(item => {
        const header = item.querySelector('.accordion-header');

        header.addEventListener('click', () => {
            // Cierra todos los demás items para que solo uno esté abierto a la vez
            accordionItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });

            // Abre o cierra el item actual
            item.classList.toggle('active');
        });
    });
});
