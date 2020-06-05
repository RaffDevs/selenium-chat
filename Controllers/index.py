from whats_scrapper import Whats
from flask import render_template, request, redirect, url_for
from time import sleep
from colorama import Fore, Back


def init_controllers(app, db, socket, chrome):
    whats = Whats(chrome)
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            nome = request.form['nome_chat']
            print(nome)
            return redirect(url_for('app', nome=nome))
        return render_template('chat/init.html')
        
    @app.route('/chat')
    def app():
        return render_template('chat/template.html')

    @socket.on('start')
    def init_scrapper():
        print(f'{Fore.CYAN}@start -- Iniciando Scraping')
        while True:
            contato_auxiliar = chrome.find_element_by_xpath(f"//span[text()='+55 16 99305-4020']")
            contato_auxiliar.click()
            novas_conversas = chrome.find_elements_by_xpath(whats.xnovas_conversas)
            print('QUANTIDADE DE NOVAS CONVERSAS', len(novas_conversas))
            # Bloco de código para caso existam novas conversas
            if len(novas_conversas) > 0:
                print(f'{Fore.CYAN}@start -- INICIANDO ETAPA 1')
                for conversa in novas_conversas:
                    sleep(0.2)
                    conversa.click()
                    nome_contato_whats = chrome.find_element_by_xpath(whats.xnome_contato).text
                    contato_atual = nome_contato_whats
                    mensagens_texto = chrome.find_elements_by_xpath(whats.xnovas_mensagens)
                    mensagem_to_selenium = whats.pega_mensagem_front(nome_contato_whats)
                    if len(mensagens_texto) > 0:
                        for msg in mensagens_texto:
                            whats.leia_mais()
                            whats.insert_mensagem_selenium(msg.text, nome_contato_whats) 
                    if len(mensagem_to_selenium) > 0:
                        whats.manda_mensagens_front(mensagem_to_selenium)
                    print(f'{Fore.GREEN}@start -- Contato: {nome_contato_whats}, Status: Todas as mensagens foram capturadas!')
                    whats.scrapping_auxiliar(nome_contato_whats)
                print(f'{Fore.GREEN}@start -- ETAPA 1 FINALIZADA')

            print(f'{Fore.CYAN}@start -- INICIANDO ETAPA 2')
            mensagens_para_insert = whats.pega_mensagem_front()
            if mensagens_para_insert != 'NOPE':
                print(f'{Fore.BLUE}@start -- Existem novas mensagens a serem enviadas para seus contatos!')
                whats.manda_mensagens_front(mensagens_para_insert)
                print(f'{Fore.GREEN}@start -- ETAPA 2 FINALIZADA')
            sleep(1)
   
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
            print(f'{Fore.CYAN}@emit_mensagens -- Buscando mensagens novas para o javascript!')
            sleep(0.5)
            msg_emit = whats.mensagens_db()
            if len(msg_emit['nova_mensagem']) > 0:
                socket.emit('python_scrapper', msg_emit)
                size = len(msg_emit['nova_mensagem'])
                print(f'{Fore.GREEN}@emit_mensagens -- Foram emitidos {size} novas mensagens para o javascript!')
                sleep(1)
            else:
                print(f'{Fore.RED}@emit_mensagens -- Sem mensagens...')
                sleep(1)

    @socket.on('mensagem_update')
    def atualiza_status_msg(dados):
        print(f'{Fore.CYAN}@mensagem_update -- Recebi o evento! Iniciando update das mensagens!')
        msg_update = whats.update_mensagens(dados['id_msg'])

    @socket.on('msg_enviada')
    def envia_mensagem(dados):
        print(f'{Fore.CYAN}@msg_enviada -- Recebi o evento! Iniciando a inserção das mensagens!')
        print('AS MENSAGENS', dados)
        whats.insert_mensagem_selenium(dados['mensagem'], dados['contato'], dados['hora_msg'], selenium=False)

