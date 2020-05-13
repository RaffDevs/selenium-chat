from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from config import app_active, app_config
from Controllers.index import init_controllers
from selenium import webdriver
config = app_config[app_active]


chrome = webdriver.Chrome('./chromedriver')
chrome.get('https://web.whatsapp.com/')


def create_app(config_name):
    app = Flask(__name__, template_folder='Templates', static_folder='Static')
    socket = SocketIO(app)
    app.secret_key = config.SECRET
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(config.APP)
    db.init_app(app)
    init_controllers(app, db, socket, chrome)
    return [app, socket]





