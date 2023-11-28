
from datetime import datetime
import logging
import re
from src.entities.normas import Normas
from src.services.crud import create_session

from src.utils.request_html import Requester


class Scraper():

    def __init__(self, norma):

        self.norma = norma
        self.pagina = None

        self.titulo = self.busca_titulo()
        self.numero = self.busca_numero()
        self.ementa = self.busca_ementa()
        self.url = self.busca_url()
        self.data = self.busca_data()
        self.indexacao = None
        self.texto = None

    def busca_titulo(self):
        return self.norma.xpath('h3/a/text()')[0]
    
    def busca_numero(self):

        titulo = self.busca_titulo()
        number = int(re.search("nº(.*),", titulo).group(1).strip().replace('.', ''))
        return number
    
    def busca_ementa(self):
        return self.norma.xpath('div/p/text()')[0]
    
    def busca_url(self):
        return self.norma.xpath('h3/a/@href')[0]
    
    def busca_data(self):

        titulo = self.busca_titulo()
        return datetime.strptime(titulo.split(',')[1].replace('º', ''), " de %d de %B de %Y")
    
    def busca_indexacao(self):    
        try:
            indexacao = self.pagina.select('#content > div > div.grupoRetratil > div.corpo')[0].text
            return indexacao

        except IndexError:
            logging.warning(f'Não encontrado indexação para: {self.url}')
            return None
        
    def busca_texto(self):
        '''
        Busca o texto de publicação original da norma. Recebe o objeto com a página referente aos dados da norma.
        Realiza uma busca na página para identificar a URL com o texto de publicação original.
        Faz a requisição nessa URL e extrai o texto original.
        '''
        
        try:
            url_texto = self.pagina.select('#content > div.dadosNorma > div.sessao > a')[0].get('href')
        except IndexError:
            logging.warning(f'Não encontrado url do texto para: {self.url}')
            return None

        # O atributo 'href' contem apenas o final da url, dessa forma foi preciso realizar tratamento especial para
        # extrair a url base, que é dinamica conforme o ano de publicação da lei            
        url_base = self.pagina.url.split('/')
        url_base[-1] = url_texto

        url_texto = '/'.join(url_base)
        
        to = Requester(url_texto)
        to.get_valid_page()

        texto_original = to.select('#content > div.textoNorma > div')[0].text
        
        return texto_original
    
    def busca_norma(self):
        pagina = Requester(self.url)
        pagina.get_valid_page()

        self.pagina = pagina
        self.indexacao = self.busca_indexacao()
        self.texto = self.busca_texto()

    def gera_objeto(self):

        objeto = Normas(
                        titulo=self.titulo,
                        nr_norma=self.numero,
                        ementa=self.ementa,
                        url=self.url,
                        data_norma=self.data,
                        data_captura=datetime.now(),
                        indexacao=self.indexacao,
                        texto=self.texto
                       )
        return objeto
    
    def salva_objeto(self):

        objeto = self.gera_objeto()

        with create_session() as session:
            session.add(objeto)