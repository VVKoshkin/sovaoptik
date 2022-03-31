import os

# .env importing
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# what environment is this?
ENV = os.environ.get('EVN', 'test')

# DB main info
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DATABASE = os.environ.get('DB_NAME')

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

# Web Form
secret_key = os.environ.get('WTF_KEY')

# Slider "filestorage"
UPLOAD_FOLDER = '/static/img/slider/new/'
SLIDER_PATH = '/static/img/slider/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
