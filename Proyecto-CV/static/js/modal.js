document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('modal-overlay');

    // --- LÓGICA GENÉRICA PARA ABRIR Y CERRAR MODALES (TU CÓDIGO ORIGINAL) ---
    function openModal(modal) {
        if (modal == null) return;
        modal.classList.add('active');
        if (overlay) overlay.classList.add('active');
    }

    function closeModal(modal) {
        if (modal == null) return;
        modal.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
    }

    document.addEventListener('click', event => {
        const openButton = event.target.closest('[data-modal-target]');
        if (openButton) {
            const modal = document.querySelector(openButton.dataset.modalTarget);
            openModal(modal);
        }

        const closeButton = event.target.closest('[data-close-button]');
        if (closeButton) {
            const modal = closeButton.closest('.modal');
            closeModal(modal);
        }
    });

    if (overlay) {
        overlay.addEventListener('click', () => {
            document.querySelectorAll('.modal.active').forEach(closeModal);
        });
    }

    // --- NUEVA LÓGICA PARA GUARDAR DATOS DESDE LOS MODALES ---

    // Función genérica para enviar datos y manejar la respuesta
    async function guardarDatos(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (response.ok && result.status === 'success') {
                window.location.reload(); // Recarga la página para mostrar los nuevos datos
            } else {
                console.error('Error del servidor:', result.message);
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error de red:', error);
            alert('No se pudo conectar con el servidor.');
        }
    }

    // 1. Guardar Experiencia
    const guardarExpBtn = document.getElementById('guardar-experiencia-btn');
    if (guardarExpBtn) {
        guardarExpBtn.addEventListener('click', () => {
            const data = {
                cargo: document.getElementById('exp-title').value,
                empresa: document.getElementById('exp-company').value,
                ubicacion: document.getElementById('exp-location').value,
                tipo_empleo: document.getElementById('exp-type').value,
                fecha_inicio: document.getElementById('exp-start-date').value,
                fecha_fin: document.getElementById('exp-end-date').value,
                actualmente_aqui: document.getElementById('exp-current').checked,
                descripcion: document.getElementById('exp-description').value,
            };
            guardarDatos('/experiencia/agregar', data);
        });
    }

    // 2. Guardar Formación
    const guardarEduBtn = document.getElementById('guardar-formacion-btn');
    if (guardarEduBtn) {
        guardarEduBtn.addEventListener('click', () => {
            const data = {
                institucion: document.getElementById('edu-institution').value,
                titulo: document.getElementById('edu-degree').value,
                campo: document.getElementById('edu-field').value,
                fecha_inicio: document.getElementById('edu-start-date').value,
                fecha_fin: document.getElementById('edu-end-date').value,
                descripcion: document.getElementById('edu-description').value,
            };
            guardarDatos('/educacion/agregar', data);
        });
    }

    // 3. Guardar Proyecto
    const guardarProyBtn = document.getElementById('guardar-proyecto-btn');
    if (guardarProyBtn) {
        guardarProyBtn.addEventListener('click', () => {
            const data = {
                nombre: document.getElementById('project-title').value,
                asociado: document.getElementById('project-association').value,
                tecnologias: document.getElementById('project-tech').value,
                enlace: document.getElementById('project-link').value,
                descripcion: document.getElementById('project-description').value,
            };
            guardarDatos('/proyecto/agregar', data);
        });
    }
});