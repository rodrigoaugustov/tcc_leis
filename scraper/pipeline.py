import datetime
import time
import re
import logging

from random import randint

from scraper.parser import Scraper
from src.utils.request_html import Requester
from src.entities.normas import Normas
from src.utils.functions import already_exists

def run_pipeline():
    '''
    Pipeline de busca das Leis Ordinárias e Leis Complementares no site da Câmara Legislativa
    Utiliza o próprio mecânismo de busca do website como ponto de partida, ordenando as leis da
    mais recente para a mais antiga.
    
    Navega pelas diversas páginas de resultados até 05/10/1988, ou até chegar na página em que as
    leis já foram foram capturadas. Dessa forma o mesmo job pode utilizado para realizar a primeira
    carga e também para a busca incremental das futuras leis publicadas, sem necessidade de consultar
    todas as páginas de resultado.
    '''
    logging.info('Início da execução')

    url_base = "https://www.camara.leg.br/legislacao/busca"
    
    proxima_pagina = "https://www.camara.leg.br/legislacao/busca?abrangencia=Legislação+Federal&tipo=Lei+Ordinária&ordenacao=data:DESC"

    busca_concluida = False

    while not busca_concluida:
        try:
            sc = Requester(proxima_pagina)
            sc.get_valid_page()

            normas = sc.find_by_xpath('//*[@id="impressaoPDF"]/ul/li')

            conta_repetidos = 0

            for norma in normas:
                
                scrap = Scraper(norma)

                titulo = scrap.titulo
                url = scrap.url
                
                if not already_exists(url, Normas):
                    scrap.busca_norma()
                    scrap.salva_objeto()

                    logging.info(f'"{titulo}" capturada com sucesso!')

                else:
                    logging.info(f'"{titulo}" já capturada anteriormente')
                    conta_repetidos += 1
                    if conta_repetidos == 20:
                        busca_concluida = True
                        continue
                    else:
                        continue

            proxima_pagina = sc.find_by_xpath('//*[@id="main-content"]/div[5]/div/div[2]/section[2]/nav/ul/li[6]/a')

            if len(proxima_pagina) == 1:
                pagina = re.search("pagina=(.*)", proxima_pagina[0].get("href")).group(1)
                logging.info(f'Iniciado captura da página {pagina}')
                if pagina == '501':
                    proxima_pagina = 'https://www.camara.leg.br/legislacao/busca?abrangencia=Legislação+Federal&tipo=Lei+Ordinária&ordenacao=data:ASC'
                else:
                    proxima_pagina = url_base + proxima_pagina[0].get('href')
            elif len(proxima_pagina) > 1:
                logging.error('Erro na captura do link para próxima página')
            else:
                logging.info('Processo de Crawling Concluído')
                busca_concluida = True
            
            # Adicionado sleep para evitar sobrecarga no servidor
            time.sleep(randint(1,3))
            
        except ConnectionError:
            continue