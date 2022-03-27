# DB main info
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_USER = 'postgres'
DB_PASSWORD = '123'
DB_DATABASE = 'SovaOptikDB'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'

# Web Form
secret_key = 'adminKey'

# Slider "filestorage"
UPLOAD_FOLDER = '\\static\\img\\slider\\new\\'
SLIDER_PATH = '\\static\\img\\slider\\'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
