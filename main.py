import ntpath
import os
import shutil

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import config, json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

# Application object
app = Flask(__name__)
# Config for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
# SQLAlchemy Object
db = SQLAlchemy(app)
# WTF settings
app.config['SECRET_KEY'] = config.secret_key


#  ORM To Json
def sliderImg_list_to_json(slider_img_list):
    arr = []
    for rec in slider_img_list:
        temp = sliderImg_to_json(rec)
        arr.append(temp)
    return json.dumps(arr)


def sliderImg_to_json(slider_img):
    return {
        'id': slider_img.id,
        'ref': slider_img.ref,
        'inner_text': slider_img.inner_text
    }


# Routing
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


# DB Models
class TopInfo(db.Model):
    __tablename__ = 'TOP_INFO'
    # TODO по хорошему тут нужна инкапсуляция + геттеры и сеттеры
    id = db.Column('id', db.Integer, primary_key=True)
    order = db.Column('rec_order', db.Integer, nullable=False)
    text = db.Column('rec_text', db.Text)
    is_phone = db.Column('is_phone', db.Integer, default=False)
    is_bold = db.Column('is_bold', db.Integer, default=False)

    def __init__(self, order, text, is_phone, is_bold):
        self.order = order
        self.text = text
        self.is_phone = is_phone
        self.is_bold = is_bold


class Assortment(db.Model):
    __tablename__ = 'ASSORTMENT'
    id = db.Column('id', db.Integer, primary_key=True)
    header_text = db.Column(db.Text, nullable=False)
    description_text = db.Column(db.Text, nullable=False)

    def __init__(self, header_text, description_text):
        self.header_text = header_text
        self.description_text = description_text


class DampersList(db.Model):
    __tablename__ = 'DAMPERS_LIST'
    id = db.Column('id', db.Integer, primary_key=True)
    text = db.Column('text', db.Text, nullable=False)

    def __init__(self, text):
        self.text = text


class SliderImg(db.Model):
    __tablename__ = 'SLIDER_IMG'
    id = db.Column('id', db.Integer, primary_key=True)
    ref = db.Column('ref', db.String, nullable=False)
    inner_text = db.Column('inner_text', db.String, nullable=True)

    # TODO по хорошему тут нужна инкапсуляция + геттеры и сеттеры
    def __init__(self, ref, inner_text):
        self.ref = ref
        self.inner_text = inner_text


class Users(db.Model):
    __tablename__ = 'USERS'
    id = db.Column('id', db.Integer, primary_key=True)
    login = db.Column('login', db.String, nullable=False)
    password = db.Column('password', db.String, nullable=False)


# DAO
def get_top_info():
    return TopInfo.query.order_by(TopInfo.order).all()


def get_top_info_by_id(id):
    return TopInfo.query.filter_by(id=id).first()


def get_assortment():
    return Assortment.query.order_by(Assortment.id).all()


def get_assortment_row(id):
    return Assortment.query.filter_by(id=id).first()


def get_damp_list():
    return DampersList.query.order_by(DampersList.id).all()


def get_damp_curr(id):
    return DampersList.query.filter_by(id=id).first()


def get_slider_list():
    return SliderImg.query.order_by(SliderImg.id).all()


def get_slider_first():
    return SliderImg.query.order_by(SliderImg.id).first()


def get_slider_last():
    return SliderImg.query.order_by(SliderImg.id.desc()).first()


def get_slider_prev(id):
    res = SliderImg.query.filter(SliderImg.id < id).order_by(SliderImg.id.desc()).first()
    if res is None:
        res = get_slider_last()
    return res


def get_slider_next(id):
    res = SliderImg.query.filter(SliderImg.id > id).order_by(SliderImg.id).first()
    if res is None:
        res = get_slider_first()
    return res


def get_slider_current(id):
    return SliderImg.query.filter_by(id=id).first()


def correct_auth(login, password):
    return Users.query.filter(Users.login == login, Users.password == password).count() > 0


def store_top_info(request_json):
    id = request_json.get('id')
    new_record = False
    top_info_row = None
    if id < 0:  # для новых записей, сиквенс сам подставит новый ID в постгресе
        new_record = True
        top_info_row = TopInfo(request_json.get('order'), request_json.get('text'), int(request_json.get('isPhone')),
                               int(request_json.get('isBold')))
        db.session.add(top_info_row)
    else:  # для старых просто обновляется вся инфа в базе
        top_info_row = get_top_info_by_id(id)
        top_info_row.order = request_json.get('order')
        top_info_row.text = request_json.get('text')
        top_info_row.is_phone = int(request_json.get('isPhone'))
        top_info_row.is_bold = int(request_json.get('isBold'))
        db.session.add(top_info_row)
    id = top_info_row.id
    return {
        'id': id,
        'result': 'ok',
        'new_record': new_record
    }


def store_slider_card(request_json):
    id = request_json.get('id')
    new_record = False
    slider_card = None
    if id < 0:  # для новых записей, сиквенс сам подставит новый ID в постгресе
        new_record = True
        ref = copy_from_new(request_json.get('ref'))
        slider_card = SliderImg(ref, request_json.get('text'))
        db.session.add(slider_card)
        db.session.commit()
    else:  # для старых просто обновляется текст в базе (фото остаётся старое в любом случае)
        slider_card = get_slider_current(id)
        slider_card.inner_text = request_json.get('text')
        db.session.add(slider_card)
    id = slider_card.id
    return {
        'id': id,
        'result': 'ok',
        'new_record': new_record
    }


def store_low_price(request_json):
    id = request_json.get('id')
    new_record = False
    low_price_row = None
    if id is None:  # для новых записей, сиквенс сам подставит новый ID в постгресе
        new_record = True
        low_price_row = DampersList(request_json.get('text'))
        db.session.add(low_price_row)
        db.session.commit()
    else:  # для старых просто обновляется текст в базе
        low_price_row = get_damp_curr(id)
        low_price_row.text = request_json.get('text')
        db.session.add(low_price_row)
    id = low_price_row.id
    return {
        'id': id,
        'result': 'ok',
        'new_record': new_record
    }


def store_assortment_elem(request_json):
    id = request_json.get('id')
    new_record = False
    assortment_row = None
    if id is None:  # для новых записей, сиквенс сам подставит новый ID в постгресе
        new_record = True
        assortment_row = Assortment(request_json.get('header'), request_json.get('description'))
        db.session.add(assortment_row)
        db.session.commit()
    else:  # для старых просто обновляется текст в базе
        assortment_row = get_assortment_row(id)
        assortment_row.header_text = request_json.get('header')
        assortment_row.description_text = request_json.get('description')
        db.session.add(assortment_row)
    id = assortment_row.id
    return {
        'id': id,
        'result': 'ok',
        'new_record': new_record
    }


# закачка в постоянное хранилище с папки new
def copy_from_new(tempRef):
    oldRef = app.root_path + tempRef
    file_name = ntpath.basename(oldRef)
    newRef = app.root_path + config.SLIDER_PATH + file_name
    shutil.copy(oldRef, newRef)
    os.remove(oldRef)
    return file_name


# проверка корректности расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


# admin Form class
class AdminForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Войти')


# Startpoint
if __name__ == '__main__':
    app.run(debug=True)
