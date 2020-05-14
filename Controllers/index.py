from whats_scrapper import Whats,TColors
from flask import render_template
from time import sleep
from colorama import Fore, Back


def init_controllers(app, db, socket, chrome):
    whats = Whats(chrome)
    
    @app.route('/')
    def index():
        return render_template('chat/template.html')

    @socket.on('start')
    def init_scrapper():
        print(f'{Fore.CYAN}@start -- Iniciando Scraping')
        while True:
            novas_conversas = chrome.find_elements_by_xpath(whats.xnovas_conversas)
            contato_atual = whats.pega_contato_atual()
            atualiza = False
            # Bloco de código para caso existam novas conversas
            if len(novas_conversas) > 0:
                print(f'{Fore.CYAN}@start -- INICIANDO ETAPA 1')
                for conversa in novas_conversas:
                    sleep(0.2)
                    conversa.click()
                    nome_contato_whats = chrome.find_element_by_xpath(whats.xnome_contato).text
                    contato_atual = nome_contato_whats
                    mensagens_texto = chrome.find_elements_by_xpath(whats.xnovas_mensagens)
                    mensagem_to_selenium = whats.pega_mensagem_front(contato_atual)
                    if len(mensagens_texto) > 0:
                        for msg in mensagens_texto:
                            whats.leia_mais()
                            whats.insert_mensagem_selenium(msg.text, contato_atual)
                    if len(mensagem_to_selenium) > 0:
                        whats.manda_mensagens_front(mensagem_to_selenium)
                    print(f'{Fore.GREEN}@start -- Contato: {contato_atual}, Status: Todas as mensagens foram capturadas!')
                    whats.scrapping_auxiliar(contato_atual)
                atualiza = True
                print(f'{Fore.GREEN}@start -- ETAPA 1 FINALIZADA')

            print(f'{Fore.CYAN}@start -- INICIANDO ETAPA 2')
            mensagens_para_insert = whats.pega_mensagem_front()
            if mensagens_para_insert != 'NOPE':
                print(f'{Fore.BLUE}@start -- Existem novas mensagens a serem enviadas para seus contatos!')
                whats.manda_mensagens_front(mensagens_para_insert)
                whats.scrapping_auxiliar(contato_atual)
                atualiza = True
                print(f'{Fore.GREEN}@start -- ETAPA 2 FINALIZADA')
                
            print(f'{Fore.CYAN}@start -- TENTANDO INICIAR REFRESH')
            if atualiza is True:
                print(f'{Fore.BLUE}@start -- INICIANDO O REFRESH')
                whats.refresh()
                print(f'{Fore.GREEN}@start -- REFRESH CONCLUÍDO')
                sleep(10)
            print(f'{Fore.BLUE}@start -- Encerrando o ciclo...')
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
                print(f'{Fore.GREEN}@emit_mensagens -- Foram emitidos {len(msg_emit['nova_mensagem'])} novas mensagens para o javascript!')
                sleep(1)
            else:
                print(f'{Fore.RED}@emit_mensagens -- Sem mensagens...')
                sleep(1)

    @socket.on('mensagem_update')
    def atualiza_status_msg(dados):
        print(dados['id_msg'])
        msg_update = whats.update_mensagens(dados['id_msg'])

    @socket.on('msg_enviada')
    def envia_mensagem(dados):
        whats.insert_mensagem_selenium(dados['mensagem'], dados['contato'], dados['hora_msg'], selenium=False)

