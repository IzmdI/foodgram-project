const counterId = document.querySelector('#counter');

const ingredientsContainer = document.querySelector('.form__field-group-ingredientes-container');
const nameIngredient = document.querySelector('#nameIngredient');
const formDropdownItems = document.querySelector('.form__dropdown-items');
const cantidadVal = document.querySelector('#cantidadVal');
const cantidad = document.querySelector('#cantidad')
const addIng = document.querySelector('#addIng');

const fileUpload = document.querySelector('#id_image')
const fileUploadName = document.querySelector('.form__upload-file')

const fileUploadWrapper = document.querySelector('.form__upload-wrapper')
const deleteButton = document.querySelector('.form__upload-delete');
const clearCheckbox = document.querySelector('#image-clear_id')

const api = new Api(apiUrl);
const header = new Header(counterId);

if (fileUploadName.textContent) {
    fileUploadWrapper.classList.toggle('form__upload-wrapper_active')
}

deleteButton.addEventListener('click', () => {
  fileUploadName.textContent = '';
    if (clearCheckbox) {
        clearCheckbox.checked = true
    }
  fileUploadWrapper.classList.toggle('form__upload-wrapper_active')
})

const readFile = (event) => {
  let file = event.target.files[0];
  let reader = new FileReader();
  reader.readAsText(file);

  reader.onload = function() {
    fileUploadName.textContent = file.name
      if (!fileUploadWrapper.classList.contains('form__upload-wrapper_active')) {
        fileUploadWrapper.classList.toggle('form__upload-wrapper_active')
      }
      if (clearCheckbox) {
        clearCheckbox.checked = false
    }
  };

  reader.onerror = function() {
    console.log(reader.error);
  };

}

const clearUpload = (event) => {
    event.target.value = ''
}

fileUpload.addEventListener('click', clearUpload)
fileUpload.addEventListener('change', readFile)

const defineInitialIndex = function () {
    const ingredients = ingredientsContainer.querySelectorAll('.form__field-item-ingredient')
    if (ingredients.length === 0) { return 1 }
    const data = Array.from(ingredients).map(item => {
        if (!item.getAttribute('id')) { return 0 }
        if (!item.getAttribute('id').split('_')[1]) { return 0 }
        return Number(item.getAttribute('id').split('_')[1])
    })
    data.sort((a, b) => a-b)
    return data[data.length - 1] + 1
}

function Ingredients() {
    let cur = defineInitialIndex();
    // клик по элементам с сервера
    const dropdown = (e) => {
        if (e.target.classList.contains('form__item-list')) {
            nameIngredient.value = e.target.textContent;
            formDropdownItems.style.display = ''
            cantidadVal.textContent = e.target.getAttribute('data-val');
        }
    };
    // Добавление элемента из инпута
    const addIngredient = (e) => {
        if(nameIngredient.value && cantidad.value > 0 && cantidad.value < 10000) {
            const data = getValue();
            const elem = document.createElement('div');
            elem.classList.add('form__field-item-ingredient');
            elem.id = `ing_${cur}`;
            elem.innerHTML = `<span> ${data.name} ${data.value} ${data.units}</span> <span class="form__field-item-delete"></span>
                             <input id="nameIngredient_${cur}" name="nameIngredient_${cur}" type="hidden" value="${data.name}">
                             <input id="valueIngredient_${cur}" name="valueIngredient_${cur}" type="hidden" value="${data.value}">
                             <input id="unitsIngredient_${cur}" name="unitsIngredient_${cur}" type="hidden" value="${data.units}">`;
            cur++;
            
            ingredientsContainer.appendChild(elem);
        }
    };
    // удаление элемента

    const eventDelete = (e) => {
        if(e.target.classList.contains('form__field-item-delete')) {
            const item = e.target.closest('.form__field-item-ingredient');
            item.removeEventListener('click',eventDelete);
            item.remove()
        };
    };
    ingredientsContainer.addEventListener('click', eventDelete);
    // получение данных из инпутов для добавления
    const getValue = (e) => {
        const data = {
            name: nameIngredient.value,
            value: cantidad.value,
            units: cantidadVal.textContent
        };
        clearValue(nameIngredient);
        clearValue(cantidad);
        return data;
    };
    // очистка инпута
    const clearValue = (input) => {
        input.value = '';
    };
    return {
        clearValue,
        getValue,
        addIngredient,
        dropdown
    }
}

const cbEventInput = (elem) => {
    return api.getIngredients(elem.target.value).then( e => {
        if(e.length !== 0 ) {
            const items = e.map( elem => {
                return `<a class="form__item-list" data-val="${elem.dimension}"">${elem.title}</a>`
            }).join(' ')
            formDropdownItems.style.display = 'flex';
            formDropdownItems.innerHTML = items;
        }
    })
    .catch( e => {
        console.log(e)
    })
};

const eventInput = debouncing(cbEventInput, 1000);

// вешаем апи
nameIngredient.addEventListener('input', eventInput);
const ingredients = Ingredients();
// вешаем слушатель на элементы с апи
formDropdownItems.addEventListener('click', ingredients.dropdown);
// вешаем слушатель на кнопку
addIng.addEventListener('click', ingredients.addIngredient);
