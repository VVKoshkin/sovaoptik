from app import db

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
