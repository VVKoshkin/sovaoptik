const topInfo = 'top-info';
const slider = 'slider';
const lowPrice = 'lowPrice';
const assortment = 'assortment'


const sleep = (milliseconds) => {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}


// при загрузке страницы полностью
$(() => {
    addTopInfoListeners();
    addSliderListeners();
    addLowPricesListeners();
    addAssortmentListeners();
});

// слушатели кнопок "удалить", кнопки "добавить" и "сохранить" - информация сверху
const addTopInfoListeners = () => {
    const table = $('#top_table')[0];
    let rows = $(table).find('tr.top-table__row'); // все кроме первой - заголовочной (у них есть кнопка удаления)
    // функционал кнопки удаления на каждой строке
    rows.each((index, row) => {
        addDelButtonListener(row, topInfo);
    });
    // функционал кнопки добавления
    const addButton = $('.top-info').find('input[name="addButton"]');
    addButton.click((e) => {
        rows = $(table).find('tr.top-table__row'); // на всякий случай обновляется - вдруг что изменилось
        // верстается новая строчка с пустыми колонками
        // id меньше 0 чтоб при сохранении понимало - это новое
        let maxOrder = getMaxOrder(rows);
        const newRowHTML = `<tr data-id="-1" class="top-table__row">
            <td><input name="isPhone" type="checkbox" /></td>
            <td><input name="isBold" type="checkbox" /></td>
            <td>
                <input
                        class="text-info_input"
                        type="text"
                        placeholder="Введите текст записи"
                        name = "text"
                        required
                />
            </td>
            <td>
                <input type="text"
                       placeholder="Введите порядок записи на странице"
                       name="order"
                       value="${maxOrder + 1}"
                />
            </td>
            <td><input class="btn btn-danger" name="delButton" type="button" value="Удалить"/></td>
        </tr>`;
        const newRow = $.parseHTML(newRowHTML);
        $(table).append(newRow);
        addDelButtonListener(newRow, topInfo);
    });
    // функционал кнопки сохранения
    const saveButton = $('.top-info').find('input[name="saveButton"]');
    $(saveButton).click( () => {
        storeData(topInfo);
    });
}

// слушатели кнопок "удалить", кнопки "добавить" и "сохранить" - слайдер
const addSliderListeners =() =>{
    const sliderCards = $('#slider_cards');
    sliderCards.each((index, row) => {
        addDelButtonListener(row, slider);
    });
    // функционал кнопки добавления
    const addButton = $('.slider').find('input[name="addButton"]');
    addButton.click((e) => {
        // отображение кнопки загрузки файла
        // поскольку по политике безопасности невозможно никак изменить файл загрузчика
        // то загрузчик будет рендериться новый каждый раз
        // а старый уничтожаться
        const uploaderMarkup = `<div class="custom-file" name="file-uploader">
            <input type="file" multiple accept="image/jpeg" name="file-uploader" class="custom-file-input">
        </div>`;
            const uploader = $.parseHTML(uploaderMarkup);
        $(uploader).insertAfter($(e.target).next('input[name="saveButton"]'));
            $(uploader).find('input[type="file"]').on('change', (e) => {
                Array.from(e.target.files).forEach((file) => {
		    sleep(10);
                    const promise = SliderElement.storeNew(file);
                    promise.then(
                        result => {
                            const resultJSON = JSON.parse(result);
                            console.log(resultJSON);
                            const newImgHTML = `<div class="slider-pic" data-id="-1" data-filename = ${resultJSON['filename']}>
                            <img
                                    class="slider-pic__img mb-2"
                                    src="${resultJSON['url_new']}"
                                    alt="Ошибка при открытии файла"
                            />
                            <input
                                    class="slider-pic__text mb-2"
                                    type="text"
                                    placeholder="Введите описание под картинку"
                            />
                            <input class="btn btn-danger" type="button" value="Удалить" name="delButton"/>
                        </div>`
                        const newImg = $.parseHTML(newImgHTML);
                        $(sliderCards).append(newImg);
                        addDelButtonListener(newImg, slider);
                        },
                        error => {
                            alert("Не удалось сохранить файл: "+error.text)
                        }
                    );
                });
                $(uploader).remove();
            });
    });
    // функционал кнопки сохранения
    const saveButton = $('.slider').find('input[name="saveButton"]');
    $(saveButton).click( () => {
        storeData(slider);
    });
}

// слушатели кнопок "удалить", кнопки "добавить" и "сохранить" - информация о низких ценах
const addLowPricesListeners = () => {
    const lowPriceList = $('#low_prices');
    lowPriceList.each((index, row) => {
        addDelButtonListener(row, lowPrice);
    });
    // функционал кнопки добавления
    const addButton = $('.low-prices').find('input[name="addButton"]');
    addButton.click((e) => {
        // верстается новая строчка с пустой записью
        // id меньше 0 чтоб при сохранении понимало - это новое
        const newRowHTML = `<div class="low-price mb-2">
            <input
                    class = "low-price__text"
                    type="text"
                    placeholder="Введите текст"
            />
            <input class="btn btn-danger" type="button" value="Удалить" name="delButton"/>
        </div>`;
        const newRow = $.parseHTML(newRowHTML);
        $(lowPriceList).append(newRow);
        addDelButtonListener(newRow, lowPrice);
    });
    // функционал кнопки сохранения
    const saveButton = $('.low-prices').find('input[name="saveButton"]');
    $(saveButton).click( () => {
        storeData(lowPrice);
    });
}

const addAssortmentListeners = () => {
    const assortmentList = $('#assortment');
    assortmentList.each((index, row) => {
        addDelButtonListener(row, assortment);
    });
    // функционал кнопки добавления
    const addButton = $('.assortment').find('input[name="addButton"]');
    addButton.click((e) => {
        // верстается новая строчка с пустой записью
        // id меньше 0 чтоб при сохранении понимало - это новое
        const newRowHTML = `<div class="assortment-elem">
        <input
                type="text"
                class="assortment-elem__head"
                placeholder="Введите текст"
        />
        <div contenteditable="true" class="assortment-elem__descr"></div>
        <input class="btn btn-danger mb-2" type="button" value="Удалить" name="delButton"/>
    </div>`;
        const newRow = $.parseHTML(newRowHTML);
        $(assortmentList).append(newRow);
        addDelButtonListener(newRow, assortment);
    });
    // функционал кнопки сохранения
    const saveButton = $('.assortment').find('input[name="saveButton"]');
    $(saveButton).click( () => {
        storeData(assortment);
    });
}


const addDelButtonListener = (row, section) => {
    const delButton = $(row).find('input[name="delButton"]'); // сами кнопки удаления - всегда с именем delButton
    // дальше ветвится в зависимости от секции
    if (section == topInfo){ // секция topInfo - табличка
        // слушатели - при нажатии удалить стирается весь tr этой кнопки со страницы
        delButton.each((index, btn) => {
            $(btn).click((e) => {
                const rowToDelete = $(e.target).parents('tr');
                if (confirm("Удалить запись?")) {
                    rowToDelete.remove();
                }
            });
        });
    } else if (section == slider) { // слайдер - див класса slider-pic стирается
        delButton.each((index, btn) => {
            $(btn).click((e) => {
                const rowToDelete = $(e.target).parents('div[class="slider-pic"]');
                if (confirm("Удалить запись?")) {
                    rowToDelete.remove();
                }
            });
        });
    } else if (section == lowPrice) {
        delButton.each((index, btn) => {
            $(btn).click((e) => {
                const rowToDelete = $(e.target).parents('div.low-price');
                if (confirm("Удалить запись?")) {
                    rowToDelete.remove();
                }
            });
        });
    } else if (section == assortment) {
        delButton.each((index, btn) => {
            $(btn).click((e) => {
                const rowToDelete = $(e.target).parents('div.assortment-elem');
                if (confirm("Удалить запись?")) {
                    rowToDelete.remove();
                }
            });
        });
    }
}

const getMaxOrder = (rows) => {
    let maxOrder = -1;
    rows.each((index, row) => {
        const curOrder = parseInt($(row).find('input[name="order"]').val());
        if (curOrder > maxOrder) maxOrder = curOrder;
    });
    if (maxOrder < 1) maxOrder = 1;
    return maxOrder;
}

const storeData = (section) => {
    if (section===topInfo) {
        storeTopInfo()
    } else if (section == slider) {
        storeSlider();
    } else if (section == lowPrice) {
        storeLowPrices();
    } else if (section == assortment) {
        storeAssortment()
    }

}

const storeTopInfo = () => {
    const table = $('#top_table')[0];
    const rows = $(table).find('tr.top-table__row');
    const bulkElems = [];
    rows.each((index, row) =>{
        let elem = TopTableElement.parseRow(row);
        bulkElems.push(elem);                
    });
    const promise = TopTableElement.bulkPost(bulkElems);
    promise.then(
        result => {
            document.location.reload();
        },
        error => {
            alert(error.text);
        }
    );
    // TODO надо типа вывести что запощено или нет, хз
}

const storeSlider = () => {
    const sliderCards = $('#slider_cards');
    const cards = $(sliderCards).find('div[class="slider-pic"]');
    const bulkElems = [];
    cards.each((index, card) => {
        const elem = SliderElement.parseCard(card);
        bulkElems.push(elem);
    });
    const promise = SliderElement.bulkPost(bulkElems);
    promise.then(
        result => {
            document.location.reload();
        },
        error => {
            alert(error.text);
        }
    );
    // TODO надо типа вывести что запощено или нет, хз

}

const storeLowPrices = () => {
    const lowPriceList = $('#low_prices')[0];
    const rows = $(lowPriceList).find('div.low-price');
    const bulkElems = [];
    rows.each((index, row) =>{
        let elem = LowPriceElem.parseRow(row);
        bulkElems.push(elem);                
    });
    const promise = LowPriceElem.bulkPost(bulkElems);
    promise.then(
        result => {
            document.location.reload();
        },
        error => {
            alert(error.text);
        }
    );
    // TODO надо типа вывести что запощено или нет, хз

}

const storeAssortment = () => {
    const assortmentList = $('#assortment')[0];
    const rows = $(assortmentList).find('div.assortment-elem');
    const bulkElems = [];
    rows.each((index, row) =>{
        let elem = AssortmentElem.parseRow(row);
        bulkElems.push(elem);                
    });
    const promise = AssortmentElem.bulkPost(bulkElems);
    promise.then(
        result => {
            document.location.reload();
        },
        error => {
            alert(error.text);
        }
    );
    // TODO надо типа вывести что запощено или нет, хз

}

// Объект одной строки в верхнем инфо
class TopTableElement {
    constructor(id,isPhone,isBold,text,order){
        this.id = id;
        this.isPhone=isPhone;
        this.isBold = isBold;
        this.text = text;
        this.order = order;
    }
    static parseRow(row){
        const id = parseInt($(row).data('id'));
        const isPhone = $(row).find('input[name="isPhone"]').is(':checked')
        const isBold = $(row).find('input[name="isBold"]').is(':checked');
        const text = $(row).find('input[name="text"]').val();
        const order = parseInt($(row).find('input[name="order"]').val());
        return new TopTableElement(id, isPhone,isBold,text,order);
    }
    toJSON() {
        return {
            'id':this.id,
            'isPhone':this.isPhone,
            'isBold':this.isBold,
            'text':this.text,
            'order':this.order
        }
    }

    // пост одной записи
    post() {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/0.1/topInfo', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState !== 4) return;

                if (xhr.status === 200)
                    resolve(xhr.response);
                else
                    reject(xhr.status);
            });

            xhr.send(JSON.stringify(this.toJSON()));
        });
    }

    // пост всех собранных записей
    static bulkPost(array) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/0.1/topInfo', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState !== 4) return;

                if (xhr.status === 200)
                    resolve(xhr.response);
                else
                    reject(xhr.status);
            });
            const req = [];
            array.forEach(elem => {
                req.push(elem.toJSON());
            });
            xhr.send(JSON.stringify(req));
        });
    }
}

// объект одной карточки с картинкой и описанием для слайдера
class SliderElement {
    constructor(id,ref,text,name) {
        this.id = id;
        this.ref = ref;
        this.text = text;
        this.name = name;
    }
    static parseCard(card) {
        const id = parseInt($(card).data('id'));
        const ref = $(card).find('img.slider-pic__img').attr('src');
        const text = $(card).find('input.slider-pic__text').val();
        const name = $(card).data('name');
        return new SliderElement(id,ref,text,name);
    }

    toJSON() {
        return {
            'id':this.id,
            'ref':this.ref,
            'text':this.text,
            'name': this.name
        };
    }

    static bulkPost(array) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/0.1/slider', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState !== 4) return;

                if (xhr.status === 200)
                    resolve(xhr.response);
                else
                    reject(xhr.status);
            });
            const req = [];
            array.forEach(elem => {
                req.push(elem.toJSON());
            });
            xhr.send(JSON.stringify(req));
        });
    }

    static getFileName() {
        const date = new Date();
        const year = date.getFullYear();
        const month = date.getMonth() < 10 ? `0${date.getMonth()}` : date.getMonth();
	const day = date.getDate() < 10 ? `0${date.getDate()}` : date.getDate();
	const hour = date.getHours < 10 ? `0${date.getHours()}` : date.getHours();
	const minutes = date.getMinutes() < 10 ? `0${date.getMinutes()}` : date.getMinutes();
	const seconds = date.getSeconds() < 10 ? `0${date.getSeconds()}` : date.getSeconds();
	const ms = date.getMilliseconds();
	const result = `${year}-${month}-${day}-${hour}-${minutes}-${seconds}-${ms}.jpg`;
	console.log(result);
	return result;
    }
    static storeNew(file) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/0.1/slider/new', true);
            // файлы кладутся в объект запроса
            let formData = new FormData();
            formData.append('fileObject', file);
            formData.append('fileName', SliderElement.getFileName());
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState !== 4) return;

                if (xhr.status === 200)
                    resolve(xhr.response);
                else
                    reject(xhr.status);
            });
            xhr.send(formData);
        });
    }
}

class LowPriceElem {
    constructor(id,text){
        this.id = id;
        this.text = text;
    }
    static parseRow(row){
        const id = parseInt($(row).data('id'));
        const text = $(row).find('input.low-price__text').val();
        return new LowPriceElem(id,text);
    }
    toJSON() {
        return {
            'id':this.id,
            'text':this.text
        }
    }

    // пост всех собранных записей
    static bulkPost(array) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/0.1/lowPrice', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState !== 4) return;

                if (xhr.status === 200)
                    resolve(xhr.response);
                else
                    reject(xhr.status);
            });
            const req = [];
            array.forEach(elem => {
                req.push(elem.toJSON());
            });
            xhr.send(JSON.stringify(req));
        });
    }
}

class AssortmentElem {
    constructor(id,header, description){
        this.id = id;
        this.header = header;
        this.description = description;
    }

    static parseRow(row){
        const id = parseInt($(row).data('id'));
        const header = $(row).find('input.assortment-elem__head').val();
        const description = $(row).find('div.assortment-elem__descr').text();
        return new AssortmentElem(id,header,description);
    }

    toJSON() {
        return {
            'id':this.id,
            'header':this.header,
            'description':this.description
        }
    }

    // пост всех собранных записей
    static bulkPost(array) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/0.1/assortment', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.addEventListener('readystatechange', () => {
                if (xhr.readyState !== 4) return;

                if (xhr.status === 200)
                    resolve(xhr.response);
                else
                    reject(xhr.status);
            });
            const req = [];
            array.forEach(elem => {
                req.push(elem.toJSON());
            });
            xhr.send(JSON.stringify(req));
        });
    }
}
