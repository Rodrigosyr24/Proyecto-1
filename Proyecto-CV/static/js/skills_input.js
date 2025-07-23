document.addEventListener('DOMContentLoaded', function () {

    // --- FUNCIÓN REUTILIZABLE PARA INICIALIZAR UN COMPONENTE DINÁMICO ---
    function setupDynamicComponent(inputId, listId, type) {
        const inputElement = document.getElementById(inputId);
        // Salir si el input no existe en la página actual.
        if (!inputElement) {
            return;
        }

        // CORRECCIÓN: Encontrar el botón "Añadir" que es hermano del input.
        // Se busca el contenedor padre y luego el botón dentro de ese contenedor.
        const addButton = inputElement.closest('.dynamic-add-container').querySelector('.btn-add-item');
        const listContainer = document.getElementById(listId);

        // Si los elementos no existen, no hacer nada.
        if (!addButton || !listContainer) {
            return;
        }

        // Evento al hacer clic en el botón "Añadir"
        addButton.addEventListener('click', function() {
            const value = inputElement.value.trim();

            if (value) {
                const newItem = createDynamicItem(value, type);
                listContainer.appendChild(newItem);
                inputElement.value = ''; // Limpiar el input
                inputElement.focus(); // Poner el foco de nuevo en el input
            }
        });
        
        // También permitir añadir con la tecla "Enter" en el input
        inputElement.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                addButton.click(); // Simular un clic en el botón de añadir
            }
        });

        // Evento para eliminar items (usando delegación de eventos)
        listContainer.addEventListener('click', function(event) {
            // Asegurarse de que se hizo clic en un botón de eliminar
            const removeButton = event.target.closest('.btn-remove-item');
            if (removeButton) {
                const itemToRemove = removeButton.closest('.dynamic-item');
                listContainer.removeChild(itemToRemove);
            }
        });
    }

    // --- FUNCIÓN PARA CREAR UN NUEVO ITEM (HABILIDAD O IDIOMA) ---
    function createDynamicItem(name, type) {
        const item = document.createElement('div');
        item.classList.add('dynamic-item');

        const nameSpan = document.createElement('span');
        nameSpan.textContent = name;

        const optionsDiv = document.createElement('div');
        optionsDiv.classList.add('item-options');

        // Crear el input correcto según el tipo (habilidad o idioma)
        if (type === 'skill') {
            const experienceInput = document.createElement('input');
            experienceInput.type = 'number';
            experienceInput.classList.add('item-input');
            experienceInput.placeholder = 'Años Exp.';
            optionsDiv.appendChild(experienceInput);
        } else if (type === 'language') {
            const levelSelect = document.createElement('select');
            levelSelect.classList.add('item-select');
            levelSelect.innerHTML = `
                <option>Nivel...</option>
                <option>Básico (A2)</option>
                <option>Intermedio (B1)</option>
                <option>Avanzado (C1)</option>
                <option>Nativo</option>
            `;
            optionsDiv.appendChild(levelSelect);
        }

        const removeButton = document.createElement('button');
        removeButton.classList.add('btn-remove-item');
        removeButton.innerHTML = '&times;';

        optionsDiv.appendChild(removeButton);

        item.appendChild(nameSpan);
        item.appendChild(optionsDiv);

        return item;
    }

    // --- INICIALIZAR AMBOS COMPONENTES ---
    // Se pasa el ID del input, el ID de la lista y el tipo de item a crear.
    setupDynamicComponent('skill-input', 'skills-list', 'skill');
    setupDynamicComponent('language-input', 'languages-list', 'language');
});
