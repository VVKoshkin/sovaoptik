# Application object
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import config

app = Flask(__name__)
# Config for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
# SQLAlchemy Object
db = SQLAlchemy(app)
# WTF settings
app.config['SECRET_KEY'] = config.secret_key

# import views
from . import views
