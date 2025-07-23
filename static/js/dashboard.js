document.addEventListener('DOMContentLoaded', function() {
    const profileDrawer = document.getElementById('view-profile-drawer');
    if (!profileDrawer) return;

    const openButtons = document.querySelectorAll('[data-drawer-target]');
    const closeButtons = document.querySelectorAll('[data-close-drawer]');
    const overlay = document.getElementById('drawer-overlay');

    // Lógica para ABRIR el panel
    openButtons.forEach(button => {
        button.addEventListener('click', function() {
            const drawerId = this.dataset.drawerTarget;
            const drawer = document.querySelector(drawerId);
            const profileId = this.dataset.profileId;

            // Muestra un estado de "cargando"
            const drawerBody = drawer.querySelector('.drawer-body');
            drawerBody.innerHTML = '<p style="text-align: center; padding: 40px;">Cargando perfil...</p>';
            openDrawer(drawer);

            // Pide la información del perfil al servidor
            fetch(`/api/perfil/${profileId}`)
                .then(response => response.json())
                .then(data => {
                    populateDrawer(drawer, data, profileId);
                });
        });
    });

    // Lógica para CERRAR el panel
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const drawer = button.closest('.drawer');
            closeDrawer(drawer); // Llamada a la función corregida
        });
    });

    if (overlay) {
        overlay.addEventListener('click', () => {
            document.querySelectorAll('.drawer.active').forEach(drawer => {
                closeDrawer(drawer); // Llamada a la función corregida
            });
        });
    }

    function populateDrawer(drawer, data, profileId) {
        // (Aquí iría la lógica para rellenar el panel con los datos del perfil)
        const drawerBody = drawer.querySelector('.drawer-body');
        drawerBody.innerHTML = `
            <h3>${data.nombre_completo || 'N/A'}</h3>
            <p>${data.resumen || 'Sin resumen.'}</p>
        `;
    }

    function openDrawer(drawer) {
        if (drawer == null) return;
        drawer.classList.add('active');
        if (overlay) overlay.classList.add('active');
    }

    // --- CORRECCIÓN DEL NOMBRE DE LA FUNCIÓN ---
    function closeDrawer(drawer) {
        if (drawer == null) return;
        drawer.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    }
});
