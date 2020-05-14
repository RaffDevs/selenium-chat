import os
from selenium import webdriver
class Config(object):
    # Habilita o uso de criptografia em sessões do Flask
    CSRF_ENABLED = True
    #Chave de criptografia 
    SECRET = 'ysb_92=qe#djf8%ng+a*#4rt#5%3*4k5%i2bck*gn@w3@f&-&'
    #Caminho do local em que os arquivos de template do projeto ficarão
    TEMPLATE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    #Caminho do local em que a raiz do projeto se encontra.
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    #Recebe a propriedade do app
    APP = None
    SQLALCHEMY_DATABASE_URI = "caminho_para_conexão_com_banco"

class DevelopmentConfig(Config):
    # Constante que habilita do ambiente de teste no flask.
    TESTING = True
    # Constante que habilita o ou desabilita os debus na console do python.
    DEBUG = True
    #IP para informar em qual endereço será rodado o projeto.
    IP_HOST = 'localhost'
    # Porta em que a aplicação irá rodar!
    PORT_HOST = 5000
    # O url da aplicação!
    URL_MAIN = 'http://%s:%s/' % (IP_HOST, PORT_HOST)

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    IP_HOST = 'localhost' # Aqui geralmente é um IP de um servidor na nuvem e não o endereço da máquina local

    PORT_HOST = 5000
    URL_MAIN = 'http://%s:%s/' % (IP_HOST, PORT_HOST)

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    IP_HOST = 'localhost' # Aqui geralmente é um IP de um servidor na nuvem e não o endereço da máquina local

    PORT_HOST = 8080
    URL_MAIN = 'http://%s:%s/' % (IP_HOST, PORT_HOST)

#Define quais camadas serão usadas no projeto. Recebe app_active como parâmetro
app_config = {
'development': DevelopmentConfig(),
'testing': TestingConfig(),
'production': ProductionConfig()
}
# Variavel de ambiente que define qual camada será usada na aplicação.
app_active = os.getenv('FLASK_ENV')
