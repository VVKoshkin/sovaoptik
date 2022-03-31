from . import db
from .models import TopInfo, Assortment, DampersList, SliderImg, Users
from .utils import copy_from_new


# DAO - GET
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


# DAO - POST
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
