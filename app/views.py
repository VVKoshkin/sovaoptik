# Routing
from flask import render_template, session, request, flash, url_for, redirect
from werkzeug.utils import secure_filename

from .DAO import *
from .forms import AdminForm
from .utils import *


@app.route('/')
def index():
    info_top = get_top_info()
    assortment = get_assortment()
    damp_list = get_damp_list()
    slider_img = get_slider_first()
    return render_template('index.html', info_top=info_top, assortment=assortment, damp_list=damp_list,
                           slider_img=slider_img)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    formAuth = AdminForm(request.form)
    topInfo = None
    sliderInfo = None
    lowPrice = None
    assortment = None
    if session.get('authorized') is None or not session.get('authorized'):  # если нет инфы об авторизации - вывод формы
        formAuth = AdminForm(request.form)
        if formAuth.validate():
            login = formAuth.login.data
            password = formAuth.password.data
            if correct_auth(login, password):
                session['authorized'] = True
            else:
                session['authorized'] = False
                flash('Неверный логин или пароль')

            return redirect(url_for('admin'))
    else:  # если авторизован - заполнение из БД всей нужной инфой
        if request.method == 'GET':
            topInfo = get_top_info()
            sliderInfo = get_slider_list()
            lowPrice = get_damp_list()
            assortment = get_assortment()

    return render_template('admin.html', formAuth=formAuth, authorized=session.get('authorized'), topInfo=topInfo,
                           sliderInfo=sliderInfo, lowPrice=lowPrice, assortment=assortment)


# REST for slider
@app.route('/api/0.1/slider', methods=['GET', 'POST'])
def slider_controller():
    if (request.method == 'GET'):
        id = request.args.get('id')
        direction = request.args.get('direction')
        if request.args.__len__() == 0:
            if request.method == 'GET':  # просто посмотреть весь слайдер
                res = get_slider_list()
                return sliderImg_list_to_json(res)
        elif request.args.__len__() == 1 and id is not None:
            if request.method == 'GET':  # посмотреть по ID картинку
                res = get_slider_current(id)
                return sliderImg_to_json(res)
        elif request.args.__len__() == 2 and id is not None and direction is not None:  # посмотреть картинку, следующую за ID в направлении direction
            res = []
            if direction == 'forward':
                res = get_slider_next(id)
            elif direction == 'backward':
                res = get_slider_prev(id)
            return sliderImg_to_json(res)
    elif request.method == 'POST':
        # TODO if not authorized then 403 Forbidden
        request_json = request.get_json()
        result = None
        if type(request_json) is list:
            result = {'elements': []}
            ids = []
            new_records = 0
            updated_records = 0
            deleted_records = 0
            # insert/update + счетчики их
            for elem in request_json:
                result_by_elem = store_slider_card(elem)
                id = result_by_elem.get('id')
                ids.append(id)
                if result_by_elem.get('new_record'):
                    new_records += 1
                else:
                    updated_records += 1
                result.get('elements').append(result_by_elem)
            #  удаление из БД и хранилища удалённых с фронта файлов
            # удаление элементов, id которых не пришли с формы
            elems_2_delete = None
            if ids.__len__() > 0:
                elems_2_delete = SliderImg.query.filter(SliderImg.id.not_in(ids)).all()
            else:  # на случай если пользователь удалил вообще все элементы и надо вычищать БД полностью
                elems_2_delete = SliderImg.query.all()
            for elem in elems_2_delete:
                path_2_delete = app.root_path + config.SLIDER_PATH + elem.ref
                os.remove(path_2_delete)
                db.session.delete(elem)
                deleted_records += 1
            db.session.commit()
            result['new_records'] = new_records
            result['updated_records'] = updated_records
            result['deleted_records'] = deleted_records
            return result


# SLIDER - store new pic in temp folder
@app.route('/api/0.1/slider/new', methods=['POST'])
def slider_store_new():
    if 'fileObject' not in request.files:
        return None  # TODO
    file = request.files['fileObject']
    if file.filename == '':
        return None  # TODO
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        url_new = config.UPLOAD_FOLDER + filename
        path_new = app.root_path + url_new
        file.save(path_new)  # сохраняется в папку new
        return {"result": "ok", "url_new": url_new, "filename": filename}


# REST for top-info (only POST, for admin panel)
@app.route('/api/0.1/topInfo', methods=['POST'])
def top_info_controller():
    # TODO if session.get('authorized') итд
    request_json = request.get_json()
    result = None
    if type(request_json) is list:
        result = {'elements': []}
        ids = []
        new_records = 0
        updated_records = 0
        deleted_records = 0
        # insert/update + счетчики их
        for elem in request_json:
            result_by_elem = store_top_info(elem)
            id = result_by_elem.get('id')
            ids.append(id)
            if result_by_elem.get('new_record'):
                new_records += 1
            else:
                updated_records += 1
            result.get('elements').append(result_by_elem)
        # удаление элементов, id которых не пришли с формы
        elems_2_delete = None
        if ids.__len__() > 0:
            elems_2_delete = TopInfo.query.filter(TopInfo.id.not_in(ids)).all()
        else:  # на случай если пользователь удалил вообще все элементы и надо вычищать БД полностью
            elems_2_delete = TopInfo.query.all()
        for elem in elems_2_delete:
            db.session.delete(elem)
            deleted_records += 1
        db.session.commit()
        result['new_records'] = new_records
        result['updated_records'] = updated_records
        result['deleted_records'] = deleted_records
        return result
    elif type(request_json) is dict:  # одиночное сохранение
        result = store_top_info(request_json)
        db.session.commit()
        return result

    # TODO catch 400 Bad Request


# REST for low-price (only POST, for admin panel)
@app.route('/api/0.1/lowPrice', methods=['POST'])
def low_price_controller():
    # TODO if not authorized then 403 Forbidden
    requestJSON = request.get_json()
    if type(requestJSON) is list:
        result = {'elements': []}
        ids = []
        new_records = 0
        updated_records = 0
        deleted_records = 0
        for rec in requestJSON:
            result_by_elem = store_low_price(rec)
            id = result_by_elem.get('id')
            ids.append(id)
            if result_by_elem.get('new_record'):
                new_records += 1
            else:
                updated_records += 1
            result.get('elements').append(result_by_elem)
        # удаление элементов, id которых не пришли с формы
        elems_2_delete = None
        if ids.__len__() > 0:
            elems_2_delete = DampersList.query.filter(DampersList.id.not_in(ids)).all()
        else:  # на случай если пользователь удалил вообще все элементы и надо вычищать БД полностью
            elems_2_delete = DampersList.query.all()
        for elem in elems_2_delete:
            db.session.delete(elem)
            deleted_records += 1
        db.session.commit()
        result['new_records'] = new_records
        result['updated_records'] = updated_records
        result['deleted_records'] = deleted_records
        return result


# REST for assortment (only POST, for admin panel)
@app.route('/api/0.1/assortment', methods=['POST'])
def assortment_controller():
    # TODO if not authorized then 403 Forbidden
    requestJSON = request.get_json()
    if type(requestJSON) is list:
        result = {'elements': []}
        ids = []
        new_records = 0
        updated_records = 0
        deleted_records = 0
        for rec in requestJSON:
            result_by_elem = store_assortment_elem(rec)
            id = result_by_elem.get('id')
            ids.append(id)
            if result_by_elem.get('new_record'):
                new_records += 1
            else:
                updated_records += 1
            result.get('elements').append(result_by_elem)
        # удаление элементов, id которых не пришли с формы
        elems_2_delete = None
        if ids.__len__() > 0:
            elems_2_delete = Assortment.query.filter(Assortment.id.not_in(ids)).all()
        else:  # на случай если пользователь удалил вообще все элементы и надо вычищать БД полностью
            elems_2_delete = Assortment.query.all()
        for elem in elems_2_delete:
            db.session.delete(elem)
            deleted_records += 1
        db.session.commit()
        result['new_records'] = new_records
        result['updated_records'] = updated_records
        result['deleted_records'] = deleted_records
        return result
