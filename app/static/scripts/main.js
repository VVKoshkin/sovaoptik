class SliderImage {
    // поля: ID, ссылка, текст для картинки
    constructor(ID, imgSrc, subText) {
        this.ID = ID;
        this.imgSrc = imgSrc;
        this.subText = subText;
    }
}

const sliderPicChange = (direction) => {
    // DOM elements
    const sliderDOMElem = document.getElementById('slider');
    const sliderDOMImgElem = sliderDOMElem.getElementsByClassName('slider-img')[0];
    const sliderDOMTextElem = sliderDOMElem.getElementsByClassName('slider-text')[0];
    // из DOM элемента получается ID картинки текущей
    let picId = parseInt(sliderDOMElem.dataset.picId);
    let directionText = 'forward';
    if (direction < 0) directionText = 'backward';
    const url = `/api/0.1/slider?id=${picId}&direction=${directionText}`;
    let sliderImg = null;
    const resultPromise = getData(url);
    resultPromise.then(
            result => {
                const response = JSON.parse(result);
                sliderImg = new SliderImage(response['id'], response['ref'], response['inner_text']);
                // changing DOMs
                sliderDOMElem.dataset.picId = sliderImg.ID;
                sliderDOMImgElem.src = `/static/img/slider/${sliderImg.imgSrc}`;
                sliderDOMTextElem.innerText = sliderImg.subText;
            },
            error => {
                alert(error.text);
            }
    );
}

const toogleNav = () => {
    // Header nav DOM
    const headerNavDom = document.getElementsByClassName('header-nav')[0];
    // изначальная высота выпадающего меню нава (при открытии 0, при закрытии - какая будет)
    let navHeight = parseInt(window.getComputedStyle(headerNavDom).getPropertyValue('height'));
    // Header DOM
    const headerDOM = document.getElementsByClassName('header')[0];
    headerNavDom.style.setProperty('display', headerNavDom.style.display === 'block' ? 'none' : 'block'); // показать - скрыть при нажатии
    /* при открытии вычислить величину нава и прибавить к хедеру такой маржин */
    if (headerNavDom.style.display === 'block') {
        navHeight = parseInt(window.getComputedStyle(headerNavDom).getPropertyValue('height'));
        const headerMb = parseInt(window.getComputedStyle(headerDOM).marginBottom);
        headerDOM.style.marginBottom = headerMb + navHeight + 'px';
    } else {
        /* при закрытии берётся navHeight, вычисленная до закрытия, и из маржина хедера вычитается эта высота, чтоб вернуть всё как раньше */
        const headerMb = parseInt(window.getComputedStyle(headerDOM).marginBottom);
        headerDOM.style.marginBottom = (headerMb - navHeight) + 'px';
    }
}

// стырено https://ru.stackoverflow.com/questions/641531/Как-определить-что-элемент-в-зоне-видимости-окна-браузера
// определяется, надо ли показывать стрелочку вверх
const checkIfArrowNeeded = () => {
    const blockPosition = $('.header').offset().top;
    const blockHeight = $('.header').height();
    const windowScrollPosition = $(window).scrollTop();
    if (blockPosition + blockHeight <= windowScrollPosition) {
        $('.up').show();
    } else {
        $('.up').hide();
    }

};

$(document).ready(() => {
    checkIfArrowNeeded();
    // слушатели на выпадающие списки ассортимента
    $(".assortment-element").on("click", (e) => {
        let element = e.target;
        // надо проверить, что нажали не на assortment-element__descr (ибо это тоже часть блока assortment-element)
        if (element.className === 'assortment-element__descr') return;
        // если клик по хедеру - берётся его родитель assortment-element
        if (element.className === 'assortment-element__head')
            element = $(element).parent('.assortment-element');
        // теперь ищется текст assortment-element__descr в element
        element.children('.assortment-element__descr').toggle();
    });

    // при скролле по странице также проверяется надо ли показывать стрелочку
    $(window).on('scroll', checkIfArrowNeeded);

    // слушатель на открытие купона на скидку
    $('.dampers-coupon').on('click', () => {
        $('.coupone').css('display', 'flex');
    });
    // закрытие купона по крестику или по клику на полупрозрачный фон
    $('.coupone').on('click', (e) => {
        if ($(e.target).attr('class') !== 'coupone-img')
            $('.coupone').css('display', 'none');
    });

});

// GET и POST запросы
const getData = (url) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.addEventListener('readystatechange', () => {
            if (xhr.readyState !== 4) return;

            if (xhr.status === 200)
                resolve(xhr.response);
            else
                reject(xhr.status);
        });
    xhr.send();

  });
}