# venv activation
activate_this = '/var/www/test.sovaoptik.ru/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))


import sys, os
sys.path.insert(0, '/var/www/test.sovaoptik.ru/')

# .env importing
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

from app import app as application
