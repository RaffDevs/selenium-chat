from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
import psycopg2
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from colorama import Fore, Back



class Whats:        
    def __init__(self, chrome):
        self.xnome_contato = "//div[@class='_3XrHh']//span"
        self.xteste = "//div[@class='_1mq8g']/div[contains(@class, 'vW7d1 message-out')]"
        self.xnovas_mensagens = "//div[contains(@class,'_1mq8g')]/following-sibling::div[contains(@class, 'message-in')]//span[@class='_3FXB1 selectable-text invisible-space copyable-text']"
        self.xnovas_mensagens_depois = "//div[contains(@class,'_1mq8g')]/following-sibling::div[contains(@class, 'message-out')][last()]/following-sibling::span[@class='_3FXB1 selectable-text invisible-space copyable-text']"
        self.xnovas_conversas = "//div[@class='_2EXPL CxUIE']"
        self.html = BeautifulSoup
        self.chrome = chrome

    def insert_mensagem_selenium(self, msg, nome_contato, hora=False, selenium=True):
        #Insere a mensagem do contato no DB
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            timestamp = datetime.now().time()
            string_timestamp = str(timestamp)
            tempo = string_timestamp[:string_timestamp.rindex('.')]
            mensagem = self.escape(msg)
            print(f'{Fore.YELLOW}(insert_mensagem_selenium) -- Vou inserir a mensagem: {mensagem}')
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
            print(f'{Fore.GREEN}(insert_mensagem_selenium) -- Mensagem inserida com sucesso!')
        except Exception as erro:
            print(f'{Fore.RED}(insert_mensagem_selenium) -- {erro}')

    def pega_ultima_mensagem(self, nome_contato):
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            print(f'{Fore.YELLOW}(pega_ultima_mensagem) -- Buscando a ultima mensagem do contato {nome_contato}...')
            cursor.execute(f"""
                SELECT mensagem FROM mensagens WHERE mensagem_recebida = 'true' AND id_contato = '{nome_contato}' ORDER BY ID DESC LIMIT 1
            """)
            retorno = list(cursor)
            conn.close()
            for msg in retorno:
                print(f'{Fore.GREEN}(pega_ultima_mensagem) -- Ultima mensagem de {nome_contato}:{msg[0]}')
                return msg[0]
        except Exception as erro:
            print(f'{Fore.RED}(pega_ultima_mensagem) -- {erro}')
            
    def main_scrapper(self, nome_contato, ultima_msg):
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
            pass
        self.leia_mais()
        #-----------------------/ALTERANDO HTML------------------#

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
        print(f'{Fore.YELLOW}(main_scrapper) -- Contato: {nome_contato}, ultima_mensagem: {ultima_msg}')
        try: 
            ultimas_msgs = soup.find_all('span', class_='_3FXB1 selectable-text invisible-space copyable-text', string=f'{ultima_msg}')[-1]
            div_pai = ultimas_msgs.find_parent('div', class_='message-in')
            parentes = div_pai.find_next_siblings('div', class_='message-in')
            mensagens_to_selenium = self.pega_mensagem_front(nome_contato)
            if len(parentes) > 0:
                for parent in parentes:
                    self.leia_mais()
                    msg = parent.select_one('span[class*="_3FXB1 selectable-text"]')
                    self.manda_mensagens_front(mensagens_to_selenium)
                    if msg != None:
                        self.insert_mensagem_selenium(msg.text, nome_contato)
                        print(f'{Fore.GREEN}(main_scrapper) -- A mensagem[{msg.text}] foi inserida com sucesso!')
                        
                    else:
                        print(f'{Fore.MAGENTA}(main_scrapper) -- Não encontrei nenhum texto nessa mensagem...')
                          
            else:
                print(f'{Fore.MAGENTA}(main_scrapper) -- Não haviam novas mensagens...')
                self.manda_mensagens_front(mensagens_to_selenium)

        except IndexError as erro_indice:
            print(f'{Fore.RED}(main_scrapper) -- Um erro de indice:{erro_indice}')
        
        except Exception as erro:
            print(f'{Fore.RED}(main_scrapper) -- {erro}')
            sleep(3)

    def scrapping_auxiliar(self, nome):
        print(f'{Fore.YELLOW}(scrapping_auxiliar) -- Verificando se há algum conteudo restante do : {nome}')
        try:
            ultima_msg = self.pega_ultima_mensagem(nome)
            retorno = self.main_scrapper(nome,ultima_msg)
        except Exception as erro:
            print(f'{Fore.RED}(scrapping_auxiliar) -- Nenhum historico de mensagem rederizado!')
    
    def monta_contatos_div(self):
        print(f'{Fore.YELLOW}(monta_contatos_div) -- Buscando contatos para javascript ')
        conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
        cursor = conn.cursor()
        cursor.execute(f"""with sql_mensagens as (
            SELECT max(id) AS id,id_contato FROM mensagens group by id_contato ORDER BY id DESC
            )
            SELECT sql_mensagens.id_contato,mensagens.mensagem from sql_mensagens inner join mensagens on (sql_mensagens.id = mensagens.id)
            ORDER BY sql_mensagens.id DESC """)
        lista_query = list(cursor)
        dicio_sql = {'dados_contatos':[]}
        for element in lista_query:
            dicio_sql['dados_contatos'].append({'contato':element[0], 'mensagem':element[1]})
        size = len(dicio_sql['dados_contatos'])
        print(f'{Fore.GREEN}(monta_contatos_div) -- {size} encontrados!')
        return dicio_sql

    def pega_mensagens_historico(self, contato):
        print(f'{Fore.YELLOW}(pega_mensagens_historico) -- Buscando historico de mensagens para javascript...')
        conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
        cursor = conn.cursor()
        cursor.execute(f"SELECT mensagem_recebida, mensagem, to_char(hora_mensagem, 'HH24:MI') FROM mensagens WHERE id_contato = '{contato}' ORDER BY id;")
        mensagens_query = list(cursor)
        dicio_mensagens = {'historico_mensagem':[]}
        for dado in mensagens_query:
            dicio_mensagens['historico_mensagem'].append({'recebida':dado[0], 'mensagem':dado[1], 'hora_mensagem':dado[2]})
        conn.close()
        size = len(dicio_mensagens['historico_mensagem'])
        print(f'{Fore.GREEN}(pega_mensagens_historico) -- Retornando {size} itens para javascript!')
        return dicio_mensagens
    
    def mensagens_db(self):
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, id_contato, mensagem, to_char(hora_mensagem, 'HH24:MI')  FROM mensagens WHERE mensagem_recebida = 'true' AND mensagem_nova = 'true' ORDER BY id ASC")
            mensagens_query = list(cursor)
            json_mensagens = {'nova_mensagem':[]}
            for element in mensagens_query:
                json_mensagens['nova_mensagem'].append({'id':element[0], 'contato':element[1], 'mensagem':element[2], 'hora_mensagem':element[3]})
                conn.close()
            return json_mensagens
        except Exception as erro:
            print(f'{Fore.RED}(mensagens_db) -- {erro}')       

    def update_mensagens(self, id_msg):
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            print(f'{Fore.YELLOW}(update_mensagens) -- Iniciando update: {id_msg}')
            cursor.execute(f"UPDATE mensagens SET mensagem_nova = 'false' WHERE id = '{id_msg}'")
            conn.commit()
            conn.close()
            print(f'{Fore.GREEN}(update_mensagens) -- Mensagem atualizada com sucesso!')
        except Exception as erro:
            print(f'{Fore.RED}(update_mensagens) -- {erro}')

    def pega_mensagem_front(self,nome=False):
        try:
            conn = psycopg2.connect(database="whats_forip",host="localhost", user="raffdevs", password="yma2578k")
            cursor = conn.cursor()
            lista_mensagens = {'dados':[]}
            if nome != False:
                print(f'{Fore.YELLOW}(pega_mensagem_front) -- Contexto: Buscando mensagens para o contato {nome}')
                cursor.execute(f"SELECT id, mensagem FROM mensagens WHERE id_contato = '{nome}' AND mensagem_recebida = 'false' AND mensagem_nova = 'true' ORDER BY id ASC")
                retorno = list(cursor)
                if len(retorno) > 0:
                    for obj in retorno:
                        lista_mensagens['dados'].append({'id_msg':obj[0], 'mensagem':obj[1]})
                    size = len(lista_mensagens['dados'])
                    print(f'{Fore.GREEN}(pega_mensagem_front) -- Retornando {size} mensagens para o selenium!')
                    return lista_mensagens
                else:
                    print(f'{Fore.MAGENTA}(pega_mensagem_front) -- Sem mensagens para selenium...')
                    return 'NOPE'
            else:
                print(f'{Fore.YELLOW}(pega_mensagem_front) -- Contexto: Buscando todas as mensagens novas...')
                cursor.execute("SELECT id, id_contato, mensagem FROM mensagens WHERE mensagem_recebida = 'false' AND mensagem_nova = 'true' ORDER BY id ASC ")
                retorno = list(cursor)
                if len(retorno) > 0:
                    for obj in retorno:
                        lista_mensagens['dados'].append({'id_msg':obj[0], 'contato':obj[1], 'mensagem':obj[2]})
                    size = len(lista_mensagens['dados'])
                    print(f'{Fore.GREEN}(pega_mensagem_front) -- Retornando {size} mensagens para o selenium!')
                    return lista_mensagens
                else:
                    print(f'{Fore.MAGENTA}(pega_mensagem_front) -- Sem mensagens para selenium...')
                    return 'NOPE'
        except Exception as erro:
            print(f'{Fore.RED}(pega_mensagem_front) -- {erro}')

    def manda_mensagens_front(self,iteravel):
        if isinstance(iteravel, str):
            pass
        else:
            for obj in iteravel['dados']:
                if 'contato' in obj:
                    nome_contato = obj['contato']
                    msg = obj['mensagem']
                    id_mensagem = obj['id_msg']
                    print(f'{Fore.YELLOW}(manda_mensagens_front) -- Contexto: Escrevendo mensagens do contato {nome_contato}')
                    print('ESSES DADOS CHEGARAM A MIM', iteravel[''])
                    try:
                        sleep(0.5)
                        contato_whats = self.chrome.find_element_by_xpath(f"//span[text()='{nome_contato}']")
                        contato_whats.click()
                        input_texto = self.chrome.find_element_by_xpath("//div[contains(@class, '_3F6QL _2WovP')]//div[contains(@class, '_2S1VP copyable-text selectable-text')]")
                        input_texto.click()
                        input_texto.send_keys(msg)
                        input_texto.send_keys(Keys.ENTER)
                        print(f'{Fore.GREEN}(manda_mensagens_front) -- Mensagem escrita com sucesso!')
                        self.update_mensagens(id_mensagem)
                        self.scrapping_auxiliar(nome_contato)
                    except NoSuchElementException as erro:
                        print(f'{Fore.RED}(manda_mensagens_front) -- Não encontrei o elemento...')
                        print(f'{Fore.RED}(manda_mensagens_front) -- Iniciando a procura do contato...')
                        self.procura_elemento(nome_contato, msg, id_mensagem)
                    except Exception as erro:
                        print(f'{Fore.RED}(manda_mensagens_front) -- {erro}')
                        sleep(1)
                else:
                    print(f'{Fore.YELLOW}(manda_mensagens_front) -- Contexto: Escrevendo mensagens novas!')
                    msg = obj['mensagem']
                    id_mensagem = obj['id_msg']
                    try:
                        input_texto = self.chrome.find_element_by_xpath("//div[contains(@class, '_3F6QL _2WovP')]//div[contains(@class, '_2S1VP copyable-text selectable-text')]")
                        input_texto.click()
                        print('Passei do click')
                        input_texto.send_keys(msg)
                        input_texto.send_keys(Keys.ENTER)
                        print(f'{Fore.GREEN}(manda_mensagens_front) -- Mensagem escrita com sucesso!')
                        self.update_mensagens(id_mensagem)
                        sleep(0.5)
                    except Exception as erro:
                        print(f'{Fore.RED}(manda_mensagens_front) -- {erro}')
                        sleep(1)

    def pega_contato_atual(self):
        try:
            contato = self.chrome.find_element_by_xpath("//div[@class='_3XrHh']//span[@class='_1wjpf _3NFp9 _3FXB1']").text
            print(f'{Fore.YELLOW}Ultimo contato acessado: {contato}')
            return contato
        except Exception as erro:
            print(f'{Fore.MAGENTA}Não encontrei o ultimo contato!')

    def refresh(self):
        self.chrome.refresh()
        try:
            alert = self.chrome.switch_to_alert()
            alert.accept()
        except Exception as erro:
            print('Erro no alert')

    def procura_elemento(self, nome, msg, id_msg):
        y = 200
        status = 'NOPE'
        while True:
            self.chrome.execute_script("document.querySelector('div._1vDUw').scrollTo(0, {});".format(y))
            sleep(1)
            print(f'{Fore.YELLOW}(procura_elemento) -- Tentando encontrar o elemento....')
            try:
                self.chrome.find_element_by_xpath(f"//span[text()='{nome}']")
                status = 'OK'
                print(f'{Fore.GREEN}(procura_elemento) -- Elemento encontrado!')
            except Exception as erro:
                print(f'{Fore.MAGENTA}(procura_elemento) -- Ainda não encontrei o elemento')
                y = y + 200
            if status == 'OK':
                contato = self.chrome.find_element_by_xpath(f"//span[text()='{nome}']")
                contato.click()
                input_texto = self.chrome.find_element_by_xpath("//div[contains(@class, '_3F6QL _2WovP')]//div[contains(@class, '_2S1VP copyable-text selectable-text')]")
                input_texto.click()
                input_texto.send_keys(msg)
                input_texto.send_keys(Keys.ENTER)
                print(f'{Fore.GREEN}(procura_elemento) -- Mensagen escrita com sucesso!')
                self.update_mensagens(id_msg)
                sleep(1)
                break
        self.chrome.execute_script("document.querySelector('div._1vDUw').scrollTo(0,1000);")

    def leia_mais(self):
        try:
            elemento = self.chrome.find_element_by_xpath("//span[@class='_3BIvq']")
            elemento.click()
        except Exception as erro:
            print(f'{Fore.MAGENTA}Nenhum LEIA MAIS')

    def escape(self, mensagem):
        if "'" in mensagem:
            nova_msg = mensagem.replace("'", '"')
            print(nova_msg)
            return nova_msg
        else:
            return mensagem