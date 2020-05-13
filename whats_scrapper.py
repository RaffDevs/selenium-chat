from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
import psycopg2
from selenium.webdriver.common.keys import Keys



class Whats:        
    def __init__(self, chrome):
        self.xnome_contato = "//div[@class='_3XrHh']//span"
        self.xteste = "//div[@class='_1mq8g']/div[contains(@class, 'vW7d1 message-out')]"
        self.xnovas_mensagens = "//div[contains(@class,'_1mq8g')]/following-sibling::div[contains(@class, 'message-in')]//span[@class='_3FXB1 selectable-text invisible-space copyable-text']"
        self.xnovas_mensagens_depois = "//div[contains(@class,'_1mq8g')]/following-sibling::div[contains(@class, 'message-out')][last()]/following-sibling::span[@class='_3FXB1 selectable-text invisible-space copyable-text']"
        self.xnovas_conversas = "//div[@class='_2EXPL CxUIE']"
        self.html = BeautifulSoup
        self.chrome = chrome


    def nome_contato_in_db(self, contato_nome):
        #Verifica se o contato ja está cadastrado no DB
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            cursor.execute(f"SELECT nome_contato FROM contatos WHERE nome_contato = '{contato_nome}'")
            retorno = list(cursor)
            print('Verificando nome')
            if len(retorno) > 0:
                return True
            else:
                return False
            cursor.close()
            conn.close()
        except Exception as erro:
            print(erro)

    def insert_contato(self, contato_nome):
        #Insere o contato no db
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            cursor.execute(f"""
            INSERT INTO contatos (nome_contato, contato_cadastrado)
            VALUES('{contato_nome}', 'F')
            """)
            print('Inserindo nome')
            conn.commit()
            conn.close()
        except Exception as erro:
            print(erro)

    def insert_mensagem_selenium(self, mensagem, nome_contato, hora=False, selenium=True):
        #Insere a mensagem do contato no DB
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            timestamp = datetime.now().time()
            string_timestamp = str(timestamp)
            tempo = string_timestamp[:string_timestamp.rindex('.')]
            print(f'Vou inserir a mensagem: {mensagem}')
            cursor = conn.cursor()
            if selenium:
                cursor.execute(f"""
                    INSERT INTO mensagens(mensagem_recebida, mensagem, data_mensagem, hora_mensagem, mensagem_nova, id_contato)
                    VALUES('T', '{mensagem}', CURRENT_DATE, '{tempo}','T','{nome_contato}')
                """)
                conn.commit()
            else:
                cursor.execute(f"""
                    INSERT INTO mensagens(mensagem_recebida, mensagem, data_mensagem, hora_mensagem, mensagem_nova, id_contato)
                    VALUES('F', '{mensagem}', CURRENT_DATE, '{hora}','T','{nome_contato}')
                """)
                conn.commit()
            conn.close()
            print(f'Inseri a mensagem!')
        except Exception as erro:
            print(erro)

    def verifica_msg_depois(self):
        # Verifica se há novas mensagens depois de ter pegado as primeiras
        # mensagens ao clicar
        try:
            mensagens_depois = chrome.find_elements_by_xpath(self.xnovas_mensagens_depois)
            if len(mensagens_depois) > 0:
                return dict(msg = True, mensagens=mensagens_depois)
            else:
                return False
        except Exception as erro:
            print(erro)

    def pega_ultima_mensagem(self, nome_contato):
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT mensagem FROM mensagens WHERE mensagem_recebida = 'true' AND id_contato = '{nome_contato}' ORDER BY ID DESC LIMIT 1
            """)
            retorno = list(cursor)
            conn.close()
            for msg in retorno:
                print('A ultima mensagem deste contato é:', msg[0])
                return msg[0]
        except Exception as erro:
            print(erro)
            
    def main_scrapper(self, nome_contato, ultima_msg):
        print('ULTIMA:', ultima_msg)
        div_html = self.chrome.find_element_by_xpath('//div[@class="_9tCEa"]').get_attribute('innerHTML')
        soup = self.html(div_html, 'html.parser')

        #----------------------ALTERANDO O HTML---------------------#
        # - Seção responsável por deletar alguns elementos do html.

        #Deleta o html de emojis junto com textos
        deleta_emoji_texto = [emoji.decompose() for emoji in soup.findAll('img',class_='emoji')]
        deleta_emoji_2 = [emoji.decompose() for emoji in soup.findAll('img', class_='b90 emoji wa _3FXB1 selectable-text invisible-space copyable-text')]
        #Bloco try para  pegar mensagens que contem somente emojis.
        # Caso haja, seu html deletado.
        try:
            span_emoji = soup.findAll('span', class_='QN22c')
            for emoji in span_emoji:
                div_emoji_pai = emoji.find_parent('div', class_='message-in')
                div_emoji_pai.decompose()
        except:
            print('Não mandaram nenhum emoji sozinho!')
        #-----------------------/ALTERANDO HTML------------------#

        print('Peguei o html')
        #---------------------SCRAPING DAS MENSAGENS-----------#
        # - Seção responsável por caputarar as mensagens no whatsapp
        
        # Pego o ultimo span que contém a ultima mensagem enviada pelo o usuario e armazeno em ultimas_msgs.
        # ultimas_msgs é uma lista pois o usuario pode mandar duas mensagens com o mesmo texto,
        # logo se peço pra ele procurar somente um span com a mensagem, ele sempre irá retornar a primeira mensagem que encontrar.
        
        # A variavel div_pai localiza o pai message-in do span da ultima mensagem.
        # E encontro todas as divs message-in que são irmãs da div_pai e armazeno na variavel parentes.
        # Faço isso para pegar as novas mensagens enviadas depois da ultima mensagem registra no banco de dados

        # if msg != None: Quando a mensagem enviada é qualquer coisa que não seja um texto
        # o beautifulsoup me retorna um None

        # return False: Retorna False para ficar ouvindo as mensagens da conversa atual
        # e verificar as novas conversas. 
        # Essa verificação está na index.py

        try: 
            ultimas_msgs = soup.find_all('span', class_='_3FXB1 selectable-text invisible-space copyable-text', string=f'{ultima_msg}')[-1]
            div_pai = ultimas_msgs.find_parent('div', class_='message-in')
            parentes = div_pai.find_next_siblings('div', class_='message-in')
            print('Peguei os parentes')
            if len(parentes) > 0:
                for parent in parentes:
                    msg = parent.select_one('span[class*="_3FXB1 selectable-text"]')
                    if msg != None:
                        self.insert_mensagem_selenium(msg.text, nome_contato)
                        print('Inseri a mensagem', msg.text)
                    else:
                        print('Essa mensagem não é um texto...')
                        # mensagem_to_selenium = self.pega_mensagem_front(nome_contato)
                        # self.manda_mensagens_front(mensagem_to_selenium)
                        return False
            else:
                print('Vim para o ELSE')
                return False

        except IndexError as erro_indice:
            print('Um erro de indice:', erro_indice)
            return False
        
        except Exception as erro:
            print('Excessão')
            print(erro)
            sleep(3)

    def scrapping_auxiliar(self, nome):
        print(nome)
        try:
            ultima_msg = self.pega_ultima_mensagem(nome)
            retorno = self.main_scrapper(nome,ultima_msg)
            novas_conversas = self.chrome.find_elements_by_xpath(self.xnovas_conversas)
            mensagens_para_insert = self.pega_mensagem_front(nome)
            if retorno is False:
                print('Sem mensagens novas para pegar!')
        except Exception as erro:
            print('Nada renderizado!')
    
    def monta_contatos_div(self):
        conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
        cursor = conn.cursor()
        cursor.execute(f"""with sql_mensagens as (
            SELECT max(id) AS id,id_contato FROM mensagens group by id_contato ORDER BY id DESC
            )
            SELECT sql_mensagens.id_contato,mensagens.mensagem from sql_mensagens inner join mensagens on (sql_mensagens.id = mensagens.id)""")
        lista_query = list(cursor)
        dicio_sql = {'dados_contatos':[]}
        for element in lista_query:
            dicio_sql['dados_contatos'].append({'contato':element[0], 'mensagem':element[1]})
        print(dicio_sql['dados_contatos'])
        return dicio_sql

    def pega_mensagens_historico(self, contato):
        conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
        cursor = conn.cursor()
        cursor.execute(f"SELECT mensagem_recebida, mensagem, to_char(hora_mensagem, 'HH24:MI') FROM mensagens WHERE id_contato = '{contato}' ORDER BY id;")
        mensagens_query = list(cursor)
        dicio_mensagens = {'historico_mensagem':[]}
        for dado in mensagens_query:
            dicio_mensagens['historico_mensagem'].append({'recebida':dado[0], 'mensagem':dado[1], 'hora_mensagem':dado[2]})
        conn.close()
        return dicio_mensagens
    
    def mensagens_db(self):
        conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, id_contato, mensagem, to_char(hora_mensagem, 'HH24:MI')  FROM mensagens WHERE mensagem_recebida = 'true' AND mensagem_nova = 'true' ORDER BY id ASC")
        mensagens_query = list(cursor)
        json_mensagens = {'nova_mensagem':[]}
        for element in mensagens_query:
            json_mensagens['nova_mensagem'].append({'id':element[0], 'contato':element[1], 'mensagem':element[2], 'hora_mensagem':element[3]})
        conn.close()
        return json_mensagens

    def update_mensagens(self, id_msg):
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            cursor.execute(f"UPDATE mensagens SET mensagem_nova = 'false' WHERE id = '{id_msg}'")
            conn.commit()
            conn.close()
            print('Mensagem atualizada com sucesso!')
        except Exception as erro:
            print('Erro ao atualizar o status da mensagem')
            print(erro)

    def pega_mensagem_front(self,nome=False):
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            lista_mensagens = {'dados':[]}
            if nome != False:
                cursor.execute(f"SELECT id, mensagem FROM mensagens WHERE id_contato = '{nome}' AND mensagem_recebida = 'false' AND mensagem_nova = 'true' ORDER BY id ASC")
                retorno = list(cursor)
                if len(retorno) > 0:
                    print('SELECIONANDO MENSAGENS PARA O SELENIUM')
                    for obj in retorno:
                        lista_mensagens['dados'].append({'id_msg':obj[0], 'mensagem':[1]})
                    print('AQUI È O SELECT', lista_mensagens)
                    return lista_mensagens
                else:
                    print('NENHUMA MENSAGEM PARA ENVIAR PARA O SELENIUM')
                    return 'NOPE'
            else:
                cursor.execute("SELECT id, id_contato, mensagem FROM mensagens WHERE mensagem_recebida = 'false' AND mensagem_nova = 'true' ORDER BY id ASC ")
                retorno = list(cursor)
                if len(retorno) > 0:
                    print('SELECIONANDO MENSAGENS PARA O SELENIUM')
                    for obj in retorno:
                        lista_mensagens['dados'].append({'id_msg':obj[0], 'contato':obj[1], 'mensagem':obj[2]})
                    print('AQUI È O SELECT', lista_mensagens)
                    return lista_mensagens
                    print(lista_mensagens['dados'])

                else:
                    print('NENHUMA MENSAGEM PARA ENVIAR PARA O SELENIUM')
                    return 'NOPE'
        except Exception as erro:
            print('Um erro aconteceu quando busquei mensagens para o selinium!')
            print(erro)

    def manda_mensagens_front(self,iteravel):
        print('ISSO È UM ITERAVEL', iteravel)
        if isinstance(iteravel, str):
            print('Sem mensagens')
        else:
            for obj in iteravel['dados']:
                if 'contato' in obj:
                    nome_contato = obj['contato']
                    msg = obj['mensagem']
                    id_mensagem = obj['id_msg']
                    print(obj)
                    try:
                        sleep(0.5)
                        contato_whats = self.chrome.find_element_by_xpath(f"//span[text()='{nome_contato}']")
                        contato_whats.click()
                        input_texto = self.chrome.find_element_by_xpath("//div[contains(@class, '_3F6QL _2WovP')]//div[contains(@class, '_2S1VP copyable-text selectable-text')]")
                        input_texto.click()
                        input_texto.send_keys(msg)
                        input_texto.send_keys(Keys.ENTER)
                        print('ESCREVI A MENSAGEM!')
                        self.update_mensagens(id_mensagem)
                    except Exception as erro:
                        print('Um erro aconteceu ao escrever mensagens para o selenium')
                        print(erro)
                        sleep(1)
                else:
                    msg = obj['mensagem']
                    id_mensagem = obj['id_msg']
                    print(id_mensagem)
                    try:
                        input_texto = self.chrome.find_element_by_xpath("//div[contains(@class, '_3F6QL _2WovP')]//div[contains(@class, '_2S1VP copyable-text selectable-text')]")
                        input_texto.click()
                        print('Passei do click')
                        input_texto.send_keys(msg)
                        input_texto.send_keys(Keys.ENTER)
                        print('ESCREVI A MENSAGEM!')
                        self.update_mensagens(id_mensagem)
                        sleep(0.5)
                    except Exception as erro:
                        print('Um erro aconteceu ao escrever mensagens para o selenium')
                        print(erro)
                        sleep(1)

    def pega_contato_atual(self):
        try:
            contato = self.chrome.find_element_by_xpath("//div[@class='_3XrHh']//span[@class='_1wjpf _3NFp9 _3FXB1']").text
            print(contato)
            return contato
        except Exception as erro:
            print('Não encontrei o contato atual!')

    def refresh(self):
        self.chrome.refresh()
        try:
            alert = self.chrome.switch_to_alert()
            alert.accept()
        except Exception as erro:
            print('Erro no alert')