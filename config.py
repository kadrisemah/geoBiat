from email.mime import base
from os import path
from sre_parse import FLAGS 
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class BaseConfig:

    FLASK_APP = 'dashapp.py'
    FLASK_ENV = 'development'
    SECRET_KEY ='d5Vez8FLrKP--E_1QNQ9NA'