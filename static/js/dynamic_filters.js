document.addEventListener('DOMContentLoaded', function() {
    // Buscamos todos los contenedores de filtros dinámicos
    const dynamicFilterSections = document.querySelectorAll('.accordion-item[data-type]');

    dynamicFilterSections.forEach(section => {
        const type = section.dataset.type;
        const inputElement = section.querySelector('.dynamic-input');
        const addButton = section.querySelector('.btn-add-item');
        const listContainer = section.querySelector('.dynamic-items-list');

        if (!inputElement || !addButton || !listContainer) return;

        // Función para crear la etiqueta correcta (habilidad o idioma)
        function createTag(name) {
            const item = document.createElement('div');
            item.classList.add('dynamic-item');

            const nameSpan = document.createElement('span');
            nameSpan.textContent = name;
            item.appendChild(nameSpan);

            const optionsDiv = document.createElement('div');
            optionsDiv.classList.add('item-options');
            
            if (type === 'skill') {
                const expInput = document.createElement('input');
                expInput.type = 'number';
                expInput.classList.add('item-input');
                expInput.placeholder = 'Años Exp.';
                optionsDiv.appendChild(expInput);
            } else if (type === 'language') {
                const levelSelect = document.createElement('select');
                levelSelect.classList.add('item-select');
                levelSelect.innerHTML = `
                    <option>Nivel</option>
                    <option>A2</option>
                    <option>B1</option>
                    <option>B2</option>
                    <option>C1</option>
                    <option>C2</option>
                    <option>Nativo</option>
                `;
                optionsDiv.appendChild(levelSelect);
            }
            
            const removeButton = document.createElement('button');
            removeButton.classList.add('btn-remove-item');
            removeButton.innerHTML = '&times;';
            removeButton.addEventListener('click', () => listContainer.removeChild(item));
            optionsDiv.appendChild(removeButton);

            item.appendChild(optionsDiv);
            return item;
        }

        // Evento para el botón "Añadir"
        addButton.addEventListener('click', () => {
            const value = inputElement.value.trim();
            if (value) {
                const newTag = createTag(value);
                listContainer.appendChild(newTag);
                inputElement.value = '';
                inputElement.focus();
            }
        });

        // Evento para la tecla "Enter"
        inputElement.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                addButton.click();
            }
        });
    });
});
