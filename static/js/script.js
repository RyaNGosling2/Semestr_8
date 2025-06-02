let image = document.getElementById('sourceImage');
let canvas = document.getElementById('canvas');
let context = canvas.getContext('2d');
let brightnessSlider = document.getElementById("brightnessSlider");
let contrastSlider = document.getElementById("contrastSlider");
let grayscaleSlider = document.getElementById("grayscaleSlider");
let hueRotateSlider = document.getElementById("hueRotateSlider");
let saturateSlider = document.getElementById("saturationSlider");
let scale = document.getElementById("scale");         
let width = 0;
let height = 0;

image.onload = function () {
    canvas.width = this.width;
    canvas.height = this.height;
    width = canvas.width;
    height = canvas.height;
    canvas.crossOrigin = "anonymous";
    applyFilter();
    document.getElementById('scalhVal').textContent = scale.value + "%";
};

document.getElementById('myForm').addEventListener('submit', function(event) {
const canvas = document.getElementById('canvas');
const imageDataURL = canvas.toDataURL('image/png');
document.getElementById('canvasData').value = imageDataURL;
});

function applyFilter() {
    let filterString =
        "brightness(" + brightnessSlider.value + "%" +
        ") contrast(" + contrastSlider.value + "%" +
        ") grayscale(" + grayscaleSlider.value + "%" +
        ") saturate(" + saturateSlider.value + "%" +
        ") hue-rotate(" + hueRotateSlider.value + "deg" + ")";
    context.filter = filterString;
    context.drawImage(currentImage, 0, 0,canvas.width, canvas.height);
    document.getElementById('brigthVal').textContent = brightnessSlider.value + "%";
    document.getElementById('conthVal').textContent = contrastSlider.value + "%";
    document.getElementById('graythVal').textContent = grayscaleSlider.value + "%";
    document.getElementById('saturthVal').textContent = saturateSlider.value + "%";
    document.getElementById('huehVal').textContent = hueRotateSlider.value + "°";
}

function bwFilter() {
    resetImage();
    grayscaleSlider.value = 100;
    brightnessSlider.value = 120;
    contrastSlider.value = 120;
    applyFilter();
}

function resetImage() {
    brightnessSlider.value = 100;
    contrastSlider.value = 100;
    grayscaleSlider.value = 0;
    hueRotateSlider.value = 0;
    saturateSlider.value = 100;
    applyFilter();
}

function saveImage(event) {
    event.preventDefault();
    let dpi_c = document.getElementById("dpi").value;
    if(dpi_c < 50 || dpi_c > 1000){
        alert("Введите DPI в диапазоне от 50 до 1000!!!");
    }
    else{
        const originalWidth = canvas.width;
        const originalHeight = canvas.height;
        const newWidth = originalWidth * (dpi_c / 72);
        const newHeight = originalHeight * (dpi_c / 72);
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = newWidth;
        tempCanvas.height = newHeight;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.imageSmoothingEnabled = true;
        tempCtx.imageSmoothingQuality = 'high';
        tempCtx.drawImage(currentImage, 0, 0, newWidth, newHeight);
        let canvasData = tempCanvas.toDataURL("image/png");
        let linkElement = document.getElementById('link');
        linkElement.setAttribute('download', 'edited_image.png');
        canvasData = canvasData.replace("image/png", "image/octet-stream");
        linkElement.setAttribute('href', canvasData);
        linkElement.click();
    }
}

function saveMeta(event) {
    event.preventDefault();
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8, ' + encodeURIComponent(document.getElementById("story").value));
    element.setAttribute('download', 'Meta.txt');
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}




const numberInputmin = document.getElementById('numberInputmin');
const min = parseInt(numberInputmin.getAttribute('min'));
const max = parseInt(numberInputmin.getAttribute('max'));
const numberInputmax = document.getElementById('numberInputmax');
numberInputmin.value = 0;
numberInputmax.value = 255;
numberInputmin.addEventListener('input', function() {
  this.value = this.value.replace(/[^0-9]/g, '');
  let value = parseInt(this.value);
  if (isNaN(value)) {
    this.value = '';
    return;
  }
  if (value < min) {
    this.value = min;
  } else if (value > max) {
    this.value = max;
  }
});
numberInputmax.addEventListener('input', function() {
  this.value = this.value.replace(/[^0-9]/g, '');
  let value = parseInt(this.value);
  if (isNaN(value)) {
    this.value = '';
    return;
  }
  if (value < min) {
    this.value = min;
  } else if (value > max + 10) {
    this.value = max + 10;
  }
});



let isDragging = false;
let startX = 0;
let startY = 0;
const canvasContainer = document.getElementById('canvasContainer');
const td = document.getElementById('tdshka');
let selection = {
            x: 0,
            y: 0,
            width: 0,
            height: 0,
            isSelecting: false
        };
let currentImage = image;
let currentWidth = image.width;
let currentHeight = image.height;

function dlc(e) {
    isDragging = true;
    startX = e.clientX - canvasContainer.offsetLeft;
    startY = e.clientY - canvasContainer.offsetTop;
    canvas.style.cursor = 'grabbing';
}
function ulc() {
    isDragging = false;
    canvas.style.cursor = 'grab';
}
function mlc(e) {
    if (!isDragging) return;

        const x = e.clientX - startX;
        const y = e.clientY - startY;

        const maxX = td.offsetWidth - canvas.offsetWidth;
        const maxY = td.offsetHeight - canvas.offsetHeight;
        if(td.offsetWidth < canvas.offsetWidth && td.offsetHeight < canvas.offsetHeight)
        {
            canvasContainer.style.left = Math.max(maxX, Math.min(0, x)) + 'px';
            canvasContainer.style.top = Math.max(maxY, Math.min(0, y)) + 'px';
        }
        else if(td.offsetHeight < canvas.offsetHeight){
            canvasContainer.style.left = td.offsetWidth/2 - canvas.offsetWidth/2  + 'px';
            canvasContainer.style.top = Math.max(maxY, Math.min(0, y)) + 'px';
        }
        else if(td.offsetWidth < canvas.offsetWidth){
            canvasContainer.style.left = Math.max(maxX, Math.min(0, x)) + 'px';
            canvasContainer.style.top = td.offsetHeight/2 - canvas.offsetHeight/2 + 'px';
        }
        else{
            canvasContainer.style.left = td.offsetWidth/2 - canvas.offsetWidth/2  + 'px';
            canvasContainer.style.top = td.offsetHeight/2 - canvas.offsetHeight/2 + 'px';
        }
}
function drc(e) {
    selection.isSelecting = true;
            selection.x = e.offsetX;
            selection.y = e.offsetY;
}
function urc() {
    selection.isSelecting = false;
}
function mrc(e) {
            if (!selection.isSelecting) return;
            selection.width = e.offsetX - selection.x;
            selection.height = e.offsetY - selection.y;
            drawImageOnCanvas();
            context.strokeStyle = 'red';
            context.lineWidth = 0;
            context.strokeRect(selection.x, selection.y, selection.width, selection.height);
}

function handleRadioChange(radioButton) {
  if (radioButton.checked) {
    if(radioButton.id == 'option1'){
        canvas.removeEventListener("mousedown", drc);
        canvas.removeEventListener("mouseup", urc);
        canvas.removeEventListener("mousemove", mrc);
        canvas.addEventListener("mousedown", dlc);
        canvas.addEventListener("mouseup", ulc);
        canvas.addEventListener("mousemove", mlc);
        canvas.style.cursor = 'grab';
    }
    else if(radioButton.id == 'option2'){
        canvas.removeEventListener("mousedown", dlc);
        canvas.removeEventListener("mouseup", ulc);
        canvas.removeEventListener("mousedown", mlc);
        canvas.addEventListener("mousedown", drc);
        canvas.addEventListener("mouseup", urc);
        canvas.addEventListener("mousemove", mrc);
        canvas.style.cursor = 'default';
    }
  }
}


const cropButton = document.getElementById('cropButton');
cropButton.addEventListener('click', () => {
    const originalWidth = canvas.width;
    const originalHeight = canvas.height;
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = selection.width;
    tempCanvas.height = selection.height;
    const tempCtx = tempCanvas.getContext('2d');
    tempCtx.drawImage(
        canvas,
        selection.x + 1,
        selection.y + 1,
        selection.width - 2,
        selection.height - 2,
        0,0,
        selection.width,
        selection.height);
    canvas.width = selection.width;
    canvas.height = selection.height;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(
        tempCanvas,
        0,0,
        selection.width,
        selection.height,
        0,0,
        selection.width,
        selection.height);
    currentImage = new Image();
    currentImage.src = canvas.toDataURL();
    currentImage.onload = () => {
        drawImageOnCanvas();
    };
    currentWidth = canvas.width;
    currentHeight = canvas.height;
});


function drawImageOnCanvas() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(currentImage, 0, 0, canvas.width, canvas.height);
}


function scaleCanvas() {
    canvas.width = currentWidth * (scale.value / 100);
    canvas.height = currentHeight * (scale.value / 100);
    applyFilter();
    canvasContainer.style.left = td.offsetWidth/2 - canvas.offsetWidth/2  + 'px';
    canvasContainer.style.top = td.offsetHeight/2 - canvas.offsetHeight/2 + 'px';
    document.getElementById('scalhVal').textContent = scale.value + "%";
}


const customSelect = document.querySelector('.custom-select');
const selectedOption = document.querySelector('.selected-option');
const options = document.querySelectorAll('.option');
const hiddenSelect = document.querySelector('.hidden-select');

selectedOption.addEventListener('click', () => {
  customSelect.classList.toggle('open');
});

options.forEach(option => {
  option.addEventListener('click', () => {
    selectedOption.textContent = option.textContent; // Или используйте innerHTML, если нужно отобразить картинку
    customSelect.classList.remove('open');
    if (hiddenSelect) {
      hiddenSelect.value = option.dataset.value;
      console.log(hiddenSelect.value);
    }
  });
});



document.getElementById('about-button').addEventListener('click', function() {
    showAboutInfo();
});

let aboutDiv = document.createElement('div');
function showAboutInfo() {
  aboutDiv.id = 'about-modal';
  aboutDiv.classList.add('scroll')
  aboutDiv.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: white;
    border: 1px solid #ccc;
    padding: 20px;
    z-index: 1000; /* Чтобы окно было поверх всего */
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  `;
  let content = `
    <h2>Пользовательское руководство</h2>
    <p>Версия: 1.0.0</p>
    <p>Разработчик: Студент ПрИб-211 Астахов Данила Александрович</p>
    <p>Приложения для обработки данных FITS из файлов.</p>

    <h3>Функциональные возможности</h3>
    <ul>
        <li><strong>Поле "Загрузка основного FITS файла":</strong> поле для зрагрузки FITS файла.</li>
        <li><strong>Кнопка "Открыть загруженный файл":</strong> отображает данные data (изображение) и metadata (данные описывающие изображение) в соответсвующих полях на странице. По умолчанию обрабатываются данные из нулевой ячейки файла. Если файл содержит трёхмерные данные, то одно измерение отбрамывается и отображаются только два. Если в нулевой ячейке файла не содержится изображение, то будут отображаться данные первой ячейки файла.</li>
        <li><strong>Кнопка "Загрузить файл с кубом данных":</strong> загружает файл с кубом данных из поля "Загрузка основного FITS файла". Используется для просмотра матаданных файла, а именно размерности куба данных.</li>
        <li><strong>Кнопка "Поиск локальных пиков":</strong> функция для поиска локальных пиков на изображении. Если помимо основного файла загружены 2 дополнительных (dark.fits и flat.fits), то перед поиском локальных пиков проводится улучшение исходного изображения (при этом точность поиска снижается). Результатом работы функции является изображение, хранящееся в исходном файле, с выделенными красными областями найденными локальными пиками.</li>
        <li><strong>Выпадающий список "Дополнительные файлы":</strong> имеет 2 поля для загрузки FITS файлов, которые используются для предобработки в процессе функции поиска локальных пиков.</li>
        <ul>  
            <li><strong>Тёмное изображение:</strong> поле принимает FITS файл с "тёмным" изображением основного FITS файла. Используется для снижения шумов на изображении</li>
            <li><strong>Плоское изображение:</strong> поле принимает FITS файл с "плоским" изображением основного FITS файла. Используется для снижения аберрационного эффекта оптики.</li>
        </ul>
        <li><strong>Выпадающий список "Дополнительные методы обработки":</strong> содержит 2 функции: "Взять срез куба данных" и "Обработка куба данных"</li>
        <ul>  
            <li><strong>Кнопка "Обработка куба данных":</strong> функция обрабатывающая файл с кубом данных, прикреплённым в поле "Загрузка основного FITS файла". Функция создаёт карту первого момента на основе первого среза куба данных. Далее функция обращается к данным мисии телескопа Гершель и берёт данные в тех же координатах, идентичных координатам карты первого момента. Следом карта первого момента накладывается на данные телескопа Гершель, результат наложения визуализируется от отображается на странице.</li>
            <li><strong>Кнопка "Взять срез куба данных":</strong> имеет 2 поля для указания оси по которой будет взят срез и область среза (задаётся числом). Предполагается что выбор оси и места среза будет основываться на просмотренных матаданных.</li>
        </ul>
        <li><strong>Кнопка "Пользовательское руководство":</strong> открывает окно с пользовательским руководством.</li>
        <li><strong>Кнопка "Переключить тему":</strong> переключает тему страницы со светлой на тёмную и обратно.</li>
        <li><strong>Выпадающий спсиок "Стандартные методы обработки":</strong></li>
        <ul>  
            <li><strong>Кнопка "Перевести изображение в чёрно-белое":</strong> переводит изображение в чёрно-белое.</li>
            <li><strong>Кнопка "Сброс":</strong> возвращает изображение в изночальное состояние.</li>
            <li><strong>Ползунок "Яркость":</strong> изменяет яркость изображения в диапазоне от 0% до 500%.</li>
            <li><strong>Ползунок "Контрастность":</strong> изменяет контрасность изображения в диапазоне от 0% до 500%.</li>
            <li><strong>Ползунок "Насыщенность":</strong> изменяет насыщенность изображения в диапазоне от 0% до 500%.</li>
            <li><strong>Ползунок "Градиент серого":</strong> применяет на изображение градиент серого в диапазоне от 0% до 100%.</li>
            <li><strong>Ползунок "Цветовая карта":</strong> изменяет цветовую карту изображения в соответсвии с цветовым кругов в диапозоне от 0° до 360°. Не работает на чёрно-белых изображениях.</li>
            <li><strong>Ползунок "Масштабирование":</strong> позволяет изменять масштаб изображения в диапазоне от 10% до 300%.</li>
            <li><strong>Режимы:</strong>.</li>
            <ul>  
                <li><strong>Перемещение:</strong> позволяет перемещать изображение внутри ячейки зажатием ЛКМ, если оно имеет размеры превышающие ячейку.</li>
                <li><strong>Образка:</strong> позволяет выделять прямоугольные области на изображении зажатием ЛКМ. После выделения и нажатия на кнопку "Обрезать" замещает изображение ранее выделенной областью</li>
            </ul>
        </ul>
        <li><strong>Выпадающий список "Работа с FITS файлом":</strong></li>
        <ul>
            <li><strong>Кнопка "Выгрузить файл":</strong> создаёт FITS файл из изображения и метаданных, находящихся в соответсвующих полях на странице, и отправляет его на скачивение пользователю.</li>
            <li><strong>Кнопка "Выгрузить изображение":</strong> позволяет пользователю скачать изображение со страницы в формате .png с расширением, указанным в поле "Введите DPI (от 50 до 1000):".</li>
            <li><strong>Кнопка "Выгрузить метаданные":</strong> позволяет скачать пользователю метаданные из соответсвующего поля на странице в формате .txt.</li>
        </ul>
        <li><strong>Выпадающий список "Обработка цветовой карты":</strong></li>
        <ul>
            <li><strong>Выбор готвой цветовой карты:</strong> имеет выпадающий список с 6ю наиболее распространёнными цветовыми картами и кнопку "Изменить цветовую карту", при нажатиии на которую цветовая карта изображения изменяется в соответсвии с выбранной. По умолчанию выбрана цветовая карта "Gray".</li>
            <li><strong>Изменение границ цветовой краты:</strong> имеет 2 поля для ввобда значений (минимального и максимального в диапазоне от 0 до 255) и кнопку "Изменить диапазон отображения", при нажатию на которую диапазоны отображения цветов меняются в соответсвии с введёнными значениями.</li>
            <li><strong>Применение нормализации:</strong> имеет выпадающий список с 4 типами нормализации и кнопку "Применить нормализацию". Одновременно к изображению может применятся либо нормализация, либо изменение границ цветовой карты.</li>
        </ul>
        <li><strong>Выпадающий список "Мета данные":</strong> позволяет скрывать или отображать поле, в котором хранятся метаданные загруженного FITS файла.</li>
        <li><strong>Поле с изображением:</strong> находится слева от поля метаданных. Отображает изображение из загруженного файла.</li>
    </ul>

    <p>Обратная связь: <a href="prib-211_582519@volsu.ru">prib-211_582519@volsu.ru</a></p>
  `;
  aboutDiv.innerHTML = content;
  let closeButton = document.createElement('button');
  closeButton.innerText = 'Закрыть';
  closeButton.addEventListener('click', function() {
    document.body.removeChild(aboutDiv);
  });
  aboutDiv.appendChild(closeButton);
  document.body.appendChild(aboutDiv);
}

const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const detailses = document.querySelectorAll('details');
const imgs = document.querySelectorAll('img');
const bb1 = document.getElementById('about-button');
const bb2 = document.getElementById('theme-toggle');
const bb3 = document.getElementById('darkik');
const bb4 = document.getElementById('darkik1');
const bb5 = document.getElementById('darkik2');
const bb6 = document.getElementById('darkik3');
const bb7 = document.getElementById('darkik4');
let dMODE = 'f';

function notform(event) {
    event.preventDefault();
}

themeToggle.addEventListener('click', () => {
    if(dMODE === 'f'){
        dMODE = 't';
        localStorage.setItem('dMODE', 't');
    }
    else{
        dMODE = 'f';
        localStorage.setItem('dMODE', 'f');
    }
    body.classList.toggle('dark-mode');
    bb1.classList.toggle('inverted');
    bb2.classList.toggle('inverted');
    bb3.classList.toggle('inverted');
    bb4.classList.toggle('inverted');
    bb5.classList.toggle('inverted');
    bb6.classList.toggle('inverted');
    bb7.classList.toggle('inverted');
    detailses.forEach(details => {
        details.classList.toggle('inverted');
    });
    imgs.forEach(img => {
        img.classList.toggle('inverted');
    });
    
        aboutDiv.classList.toggle('inverted');
    
});
(function () {
    const isDarkMode = localStorage.getItem('dMODE');
    if(isDarkMode === 't'){
        dMODE = 't';
        body.classList.toggle('dark-mode');
        bb1.classList.toggle('inverted');
        bb2.classList.toggle('inverted');
        bb3.classList.toggle('inverted');
        bb4.classList.toggle('inverted');
        bb5.classList.toggle('inverted');
        bb6.classList.toggle('inverted');
        bb7.classList.toggle('inverted');
        detailses.forEach(details => {
            details.classList.toggle('inverted');
        });
        imgs.forEach(img => {
            img.classList.toggle('inverted');
        });
            aboutDiv.classList.toggle('inverted');
        
    }
})();