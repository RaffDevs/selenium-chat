import sys
from app import create_app
from config import app_active, app_config

config = app_config[app_active]

app = create_app(app_active)[0]
socket = create_app(app_active)[1]
config.APP = app


if __name__ == '__main__':
    socket.run(config.APP,host=config.IP_HOST, port=config.PORT_HOST, use_reloader=False)
    reload(sys)