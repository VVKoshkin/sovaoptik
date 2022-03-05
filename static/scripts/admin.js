const topInfo = 'top-info';

// при загрузке страницы полностью
$(() => {
    addTopInfoListeners()
});

// слушатели кнопок "удалить" и кнопки "добавить
const addTopInfoListeners = () => {
    const table = $('#top_table')[0];
    let rows = $(table).find('tr.top-table__row'); // все кроме первой - заголовочной (у них есть кнопка удаления)
    // функционал кнопки удаления на каждой строке
    rows.each((index, row) => {
        addDelButtonListener(row);
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
            <td><input name="delButton" type="button" value="Удалить"/></td>
        </tr>`;
        const newRow = $.parseHTML(newRowHTML);
        $(table).append(newRow);
        addDelButtonListener(newRow);
    });
    // функционал кнопки сохранения
    const saveButton = $('.top-info').find('input[name="saveButton"]');
    $(saveButton).click( () => {
        storeData(topInfo);
    });
}

const addDelButtonListener = (row) => {
    const delButton = $(row).find('input[name="delButton"]'); // сами кнопки удаления
    // слушатели - при нажатии удалить стирается весь tr этой кнопки со страницы
    delButton.each((index, btn) => {
        $(btn).click((e) => {
            const rowToDelete = $(e.target).parents('tr');
            if (confirm("Удалить запись?")) {
                rowToDelete.remove();
            }
        });
    });
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
    }

}

const storeTopInfo = () => {
    const table = $('#top_table')[0];
    const rows = $(table).find('tr.top-table__row');
    const bulkElems = [];
    rows.each((index, row) =>{
        let elem = TopTableElement.parseRow(row);
        bulkElems.push(elem);
        /*const promise = elem.post();
        promise.then(
            result => {
                console.log(result); // TODO рисовать галочку и плюсик и обновлять в соответствии с БД
            },
            error => {
                alert(error.text);
            }

        )*/
                
    });
    const promise = TopTableElement.bulk_post(bulkElems);
    promise.then(
        result => {
            console.log(result); // TODO рисовать галочку и плюсик и обновлять в соответствии с БД
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
    static bulk_post(array) {
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