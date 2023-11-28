import requests
import logging
import time

from lxml import etree
from bs4 import BeautifulSoup

class Requester(BeautifulSoup):
    """Classe personalizada que realiza a requisição HTTP na página web e gera uma instância do BeautifulSoup,
    herdando os métodos.
    """
    HEADERS = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 '
                          'Safari/537.36'
              }

    def __init__(self, url: str, headers: dict = HEADERS):
        """Constructor. 
        :param url: Endereço Web que deseja buscar.
        :param headers: Header(Cabeçalho) que será utilizado para realizar a requisição HTTP. Opcional.

        A requisição HTTP é realizada na construção da classe, e o resultado é utilizado para construir um objeto do
        tipo BeautifulSoup. Dessa forma o objeto gerado por essa classe além de possuir os próprios métodos,
        herda os métodos BeautifulSoup. 
        """
        self.headers = headers
        self.url = url
        self.init_class()

    def find_by_xpath(self, xpath_expression):
        """Realiza a busca na página usando xpath.
        :param xpath_expression: Expressão que será utilizada na busca.
        """
        dom = etree.HTML(str(self))
        return dom.xpath(xpath_expression)

    def get_page(self):
        '''
        Realiza a requisição HTTP e retorna a resposta.
        Caso obtenha erro na requisição, chama novamente a função de forma recursíva.
        O limite de recursividade pode ser configurado utilizando o pacote sys
        Ex. sys.setrecursionlimit(10**6)
        '''
        with requests.Session() as session:
            if self.headers:
                session.headers.update(self.headers)
            try:
                response = session.get(self.url, verify=False)
                return response
            except RecursionError:
                logging.error(f'Impossível obter url: {self.url}')
                raise ConnectionError(f'Impossível obter url: {self.url}')
            except:
                logging.warning(f'Problema ao obter a url: {self.url}')
                time.sleep(5)
                response = self.get_page()
                return response
        
    def init_class(self):
        response = self.get_page()
        super().__init__(response.text, 'html.parser')
    
    def get_valid_page(self):
        '''
        Verifica se o request retornou um conteúdo válido.

        Durante o desenvolvimento do crawler a página apresentou problemas na resposta, no entanto ao invés de retornar 
        erro na requisição, o servidor retorna status 200 e informa no corpo da página que não foi possível obter o conteúdo.

        Dessa forma foi necessário realizar um tratamento adicional para verificar se o conteúdo retornado na requisição é válido,
        caso não seja o request é refeito e a classe é reinicilizada.
        '''

        pagina_valida = False

        while not pagina_valida:
            
            texto_validacao = self.find_by_xpath('//h1')[0].text

            if texto_validacao == 'Desculpe-nos!':
                logging.warning(f'Problema com o request da página: {self.url}')
                time.sleep(5)

                # Refaz o request na página e reinicializa o objeto
                self.init_class()
            else:
                pagina_valida = True