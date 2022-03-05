from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import config, json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

# Application object
app = Flask(__name__)
# Config for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
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
            return redirect(url_for('admin'))
    else:  # если авторизован - заполнение из БД всей нужной инфа
        if request.method == 'GET':
            topInfo = get_top_info()
            sliderInfo = get_slider_list()
            lowPrice = get_damp_list()
            assortment = get_assortment()
        elif request.method == 'POST':
            # сохранение инфы сверху
            section = request.args.get('section')
            if section == 'top-info':
                return 'TOP INFO'
            else:
                pass  # TODO бросить исключение о неправавильном запросе типа 400 Bad Request

    return render_template('admin.html', formAuth=formAuth, authorized=session.get('authorized'), topInfo=topInfo,
                           sliderInfo=sliderInfo, lowPrice=lowPrice, assortment=assortment)


# REST for slider
@app.route('/api/0.1/slider', methods=['GET', 'POST'])
def slider_controller():
    id = request.args.get('id')
    direction = request.args.get('direction')
    if request.args.__len__() == 0:
        if request.method == 'GET':  # просто посмотреть весь слайдер
            res = get_slider_list()
            return sliderImg_list_to_json(res)
        elif request.method == 'POST':
            pass  # TODO поклажа новой картинки
    elif request.args.__len__() == 1 and id is not None:
        if request.method == 'GET':  # посмотреть по ID картинку
            res = get_slider_current(id)
            return sliderImg_to_json(res)
        elif request.method == 'POST':
            pass  # TODO изменение существующей картинки по ID
    elif request.args.__len__() == 2 and id is not None and direction is not None:  # посмотреть картинку, следующую за ID в направлении direction
        res = []
        if direction == 'forward':
            res = get_slider_next(id)
        elif direction == 'backward':
            res = get_slider_prev(id)
        return sliderImg_to_json(res)


# REST for top-info (only POST, for admin panel)
@app.route('/api/0.1/topInfo', methods=['POST'])
def top_info_controller():
    # TODO if session.get('authorized') итд
    request_json = request.get_json()
    if type(request_json) is list:
        result = {}
        new_records = 0
        updated_records = 0
        deleted_records = 0
        for elem in request_json:
            result_by_elem = store_top_info(elem)

        # TODO удаление элементов
        db.session.commit()

    elif type(request_json) is dict:  # одиночное сохранение
        store_top_info(request_json)

    # TODO catch 400 Bad Request


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


class DampersList(db.Model):
    __tablename__ = 'DAMPERS_LIST'
    id = db.Column('id', db.Integer, primary_key=True)
    text = db.Column('text', db.Text, nullable=False)


class SliderImg(db.Model):
    __tablename__ = 'SLIDER_IMG'
    id = db.Column('id', db.Integer, primary_key=True)
    ref = db.Column('ref', db.String, nullable=False)
    inner_text = db.Column('inner_text', db.String, nullable=True)


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


def get_damp_list():
    return DampersList.query.order_by(DampersList.id).all()


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


# admin Form class
class AdminForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Войти')


# Startpoint
if __name__ == '__main__':
    app.run(debug=True)
