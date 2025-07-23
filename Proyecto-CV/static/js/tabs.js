document.addEventListener('DOMContentLoaded', function () {
    const tabsContainer = document.querySelector('.tabs-nav');
    
    // Si no hay pestañas en esta página, no hacer nada.
    if (!tabsContainer) {
        return;
    }

    const tabLinks = tabsContainer.querySelectorAll('.tab-link');
    const tabPanes = document.querySelectorAll('.tabs-content .tab-pane');

    tabsContainer.addEventListener('click', function (event) {
        const clickedTab = event.target.closest('.tab-link');

        // Si no se hizo clic en un botón de pestaña, salir.
        if (!clickedTab) {
            return;
        }

        // 1. Quitar la clase 'active' de todos los botones de pestaña
        tabLinks.forEach(link => {
            link.classList.remove('active');
        });

        // 2. Quitar la clase 'active' de todos los paneles de contenido
        tabPanes.forEach(pane => {
            pane.classList.remove('active');
        });

        // 3. Añadir la clase 'active' solo al botón en el que se hizo clic
        clickedTab.classList.add('active');

        // 4. Mostrar el panel de contenido correspondiente
        const tabId = clickedTab.dataset.tab;
        const correspondingPane = document.getElementById(tabId);
        if (correspondingPane) {
            correspondingPane.classList.add('active');
        }
    });
});
