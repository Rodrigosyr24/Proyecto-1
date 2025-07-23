document.addEventListener('DOMContentLoaded', function () {
    const columns = document.querySelectorAll('.column-cards');

    if (columns.length === 0) {
        return; // Si no hay columnas en la página, no hacer nada
    }

    // Función para enviar la actualización al backend
    function updatePostulacionEstado(postulacionId, nuevoEstado) {
        fetch(`/postulacion/actualizar-estado/${postulacionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // (En una app real, aquí enviaríamos un token de seguridad)
            },
            body: JSON.stringify({ nuevo_estado: nuevoEstado })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Estado actualizado con éxito:', data.message);
                // (Aquí podríamos mostrar una pequeña notificación de éxito)
            } else {
                console.error('Error al actualizar:', data.error);
                // (Aquí podríamos mostrar un error y quizás devolver la tarjeta a su lugar original)
            }
        })
        .catch(error => console.error('Error de red:', error));
    }

    columns.forEach(column => {
        new Sortable(column, {
            group: 'pipeline', // Permite mover tarjetas entre columnas del mismo grupo
            animation: 150,    // La animación del movimiento
            ghostClass: 'sortable-ghost', // Una clase para estilizar el "fantasma" de la tarjeta
            
            // Esta función se ejecuta CUANDO SUELTAS una tarjeta en una nueva columna
            onEnd: function (evt) {
                const card = evt.item; // La tarjeta que se movió
                const newColumn = evt.to; // La nueva columna donde se soltó

                const postulacionId = card.dataset.id;
                const nuevoEstado = newColumn.dataset.state;

                console.log(`Mover postulación ${postulacionId} al estado: ${nuevoEstado}`);
                
                // ¡Ahora llamamos a la función que habla con el backend!
                updatePostulacionEstado(postulacionId, nuevoEstado);
            }
        });
    });
});
