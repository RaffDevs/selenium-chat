from whats_scrapper import Whats
from flask import render_template
from time import sleep


def init_controllers(app, db, socket, chrome):
    whats = Whats(chrome)
    
    @app.route('/')
    def index():
        return render_template('chat/template.html')

    @socket.on('start')
    def init_scrapper():
        print('Iniciando Scraping')
        while True:
            novas_conversas = chrome.find_elements_by_xpath(whats.xnovas_conversas)
            contato_atual = whats.pega_contato_atual()
            # Bloco de código para caso existam novas conversas
            if len(novas_conversas) > 0:
                print('Encontrei novas conversas')
                for conversa in novas_conversas:
                    sleep(0.2)
                    conversa.click()
                    nome_contato_whats = chrome.find_element_by_xpath(whats.xnome_contato).text
                    contato_atual = nome_contato_whats
                    mensagens_texto = chrome.find_elements_by_xpath(whats.xnovas_mensagens)
                    mensagem_to_selenium = whats.pega_mensagem_front(contato_atual)
                    if len(mensagens_texto) > 0:
                        for msg in mensagens_texto:
                            whats.insert_mensagem_selenium(msg.text, contato_atual)
                    if len(mensagem_to_selenium) > 0:
                        whats.manda_mensagens_front(mensagem_to_selenium)
                    print('Finalizei')
                    whats.scrapping_auxiliar(contato_atual)
                print('dormir1')
                whats.refresh()
                sleep(10)

            print('Passo 2')
            mensagens_para_insert = whats.pega_mensagem_front()
            if mensagens_para_insert != 'NOPE':
                print('TEM NOVAS PARA O SELENIUM')
                whats.manda_mensagens_front(mensagens_para_insert)
                whats.scrapping_auxiliar(contato_atual)
                print('dormir2')
                whats.refresh()
                sleep(10)
            print('Passo 3')
            sleep(2)
            
    @socket.on('monta_contatos')
    def pega_contatos():
        div_contatos = whats.monta_contatos_div()
        socket.emit('python_scrapper', div_contatos)

    @socket.on('contato_historico')
    def pega_historico(dados):
        mensagens_contato = whats.pega_mensagens_historico(dados['contato'])
        print(mensagens_contato)
        socket.emit('python_scrapper', mensagens_contato)
        
    @socket.on('emit_mensagens')
    def pega_mensagens_db():
        while True:
            sleep(0.5)
            msg_emit = whats.mensagens_db()
            if len(msg_emit['nova_mensagem']) > 0:
                print('Encontrei mensagens novas no DB')
                socket.emit('python_scrapper', msg_emit)
                sleep(1)
            else:
                print('Sem mensagens novas no DB')
                sleep(1)

    @socket.on('mensagem_update')
    def atualiza_status_msg(dados):
        print(dados['id_msg'])
        msg_update = whats.update_mensagens(dados['id_msg'])

    @socket.on('msg_enviada')
    def envia_mensagem(dados):
        whats.insert_mensagem_selenium(dados['mensagem'], dados['contato'], dados['hora_msg'], selenium=False)

