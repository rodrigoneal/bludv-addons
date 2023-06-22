from time import sleep

from selenium.common.exceptions import (JavascriptException, TimeoutException,
                                        WebDriverException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
from selenium_tools.page_objects import Element

from src import limpar_dados
from src.db.models import Bludv


class AbrirPagina(Element):
    nav_menu = (By.ID, "menu")

    def esta_aberta(self, url: str) -> bool:
        try:
            self.driver.get(url)
        except WebDriverException:
            sleep(1)
        try:
            self.find_element(self.nav_menu, 
                              condition=EC.visibility_of_element_located, time=2)
            return True
        except (TimeoutException, WebDriverException):
            return False

class AbrirFilme(Element):
    ...

class PegarDados(Element):
    titulo = (By.XPATH,"//em[contains(text(),'Título Original:')]/ancestor::span")
    genero = (By.XPATH, "//em[contains(text(),'Gênero')]/ancestor::span")
    qualidade_audio = (By.XPATH, "//em[contains(text(),'Qualidade de Áudio')]/ancestor::span")
    qualidade_video = (By.XPATH, "//em[contains(text(),'Qualidade de Áudio')]/ancestor::span")
    duracao = (By.XPATH, "//em[contains(text(),'Duração')]/ancestor::span")
    lancamento = (By.XPATH, "//em[contains(text(),'Lançamento')]/ancestor::span")
    poster = (By.XPATH, "//span/img")
    imdb = (By.XPATH, "//a[contains(@href, 'imdb')]")
    sinopse = (By.XPATH, "//span[contains(text(),'SINOPSE')]/ancestor::p")
    qualidade_torrent = (By.XPATH, "//em[contains(text(), 'SERVIDOR')] ") 
    versao_torrent = (By.XPATH, "//preceding::strong[contains(text(), 'VERSÃO')]")
    atualizacao = (By.XPATH, "//div[2]/div[1]/div[1]/div")


    def informacoes_filme(self) -> Filme:

        torrents = self.find_elements(self.qualidade_torrent)
        titulo = self.find_element(self.titulo,time=2).text
        genero = self.find_element(self.genero,time=2).text
        qualidade_audio = self.find_element(self.qualidade_audio,
                                            time=2).text
        qualidade_video = self.find_element(self.qualidade_video,
                                            time=2).text
        imdb_id = self.find_element(self.imdb,
                                    time=2).get_attribute("href")
        imdbRating = self.find_element(self.imdb,
                                      time=2).text
        lancamento = self.find_element(self.lancamento,
                                       time=2).text
        poster = self.find_element(self.poster,
                                   time=2).get_attribute("src")
        sinopse = self.find_element(self.sinopse,time=2).text
        duracao = self.find_element(self.duracao).text
        atualizacao = self.find_element(self.atualizacao)
        links_torrent = []

        try:
            torrents_link = [torrent for torrent in self.execute_script(f"return arrDBLinks") if torrent.startswith("magnet")]
        except JavascriptException:
            sleep(2)
            torrents_link = [torrent for torrent in self.execute_script(f"return arrDBLinks") if torrent.startswith("magnet")]
        torrents_hash = limpar_dados.limpar_link_torrent(torrents_link)
        atualizado = limpar_dados.limpar_atualizacao(atualizacao.get_attribute("innerHTML"))
        sub_index = 0
        for index, torrent in enumerate(torrents):  
            resolucao_filme = limpar_dados.limpar_qualidade_torrent(torrent.text)
            _linguagem = self.driver.find_element(locate_with(*self.versao_torrent).above(torrent))
            linguagem = limpar_dados.limpar_versao(_linguagem.text)

            title = linguagem +" "+ resolucao_filme
            if "BREVE" in torrent.text.upper():
                infohash = None
                sub_index += 1
            else:
                try:
                    infohash = torrents_hash[index - sub_index]["hash"]
                except IndexError:
                    infohash = None
        
            links_torrent.append(LinkTorrent(title=title, infoHash=infohash))
        name = limpar_dados.remover_texto_titulo(titulo)
        genres = limpar_dados.transformar_genero(genero)
        qualidade_audio = limpar_dados.limpar_video_e_audio(qualidade_audio)
        qualidade_video = limpar_dados.limpar_video_e_audio(qualidade_video)
        id = limpar_dados.pegar_id_imdb(imdb_id)
        releaseInfo = limpar_dados.limpar_lancamento(lancamento)
        description = limpar_dados.limpar_sinopse(sinopse)
        logo = limpar_dados.limpar_poster(poster)
        runtime = limpar_dados.limpar_duracao(duracao)



        
        return Filme(name=name, genres=genres,
                    qualidade_audio=qualidade_audio,
                    qualidade_video=qualidade_video,
                    id=id, releaseInfo=releaseInfo,
                    logo=logo,description=description,
                    imdbRating=imdbRating,
                    runtime=runtime, 
                    versao_filme=links_torrent,
                    atualizado=atualizado)