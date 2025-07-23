document.addEventListener('DOMContentLoaded', function() {
    const viewProfileModal = document.getElementById('view-profile-modal');
    const sendProposalModal = document.getElementById('send-proposal-modal');
    
    // Si los modales no existen en esta página, no hacer nada.
    if (!viewProfileModal || !sendProposalModal) return;

    const proposalForm = sendProposalModal.querySelector('form');
    const proposalTitle = sendProposalModal.querySelector('.modal-title');

    // Usamos un observador para "escuchar" cuando se abre el modal del perfil.
    // Esto es una técnica avanzada para asegurarnos de que siempre tenemos los datos correctos.
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            // Si el modal del perfil se acaba de hacer visible...
            if (mutation.attributeName === 'class' && viewProfileModal.classList.contains('active')) {
                
                // Obtenemos el ID y el nombre del perfil que guardamos en el modal
                const profileId = viewProfileModal.dataset.profileId;
                const profileName = viewProfileModal.dataset.profileName;

                if (profileId) {
                    // Actualizamos la acción del formulario y el título del modal de propuesta
                    proposalForm.action = `/propuesta/enviar/${profileId}`;
                    proposalTitle.textContent = `Enviar Propuesta a ${profileName}`;
                }
            }
        });
    });

    // Le decimos al observador que vigile los cambios en el modal del perfil.
    observer.observe(viewProfileModal, { attributes: true });
});

