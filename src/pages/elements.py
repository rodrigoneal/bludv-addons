from time import sleep
from typing import Iterable

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium_tools.page_objects import Element

from src import limpar_dados
from src.schemas.movie_schema import Filme, Genero


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
    lancamento = (By.XPATH, "//em[contains(text(),'Lançamento')]/ancestor::span")
    poster = (By.XPATH, "//span/img")
    imdb = (By.XPATH, "//a[contains(@href, 'imdb')]")
    sinopse = (By.XPATH, "//span[contains(text(),'SINOPSE')]/ancestor::p")
    versoes_filme = (By.XPATH, "//center")


    def informacoes_filme(self) -> Filme:
        titulo = self.find_element(self.titulo).text
        genero = self.find_element(self.genero).text
        qualidade_audio = self.find_element(self.qualidade_audio).text
        qualidade_video = self.find_element(self.qualidade_video).text
        imdb_id = self.find_element(self.imdb).get_attribute("href")
        imdb_nota = self.find_element(self.imdb).text
        lancamento = self.find_element(self.lancamento).text
        poster = self.find_element(self.poster).get_attribute("src")
        sinopse = self.find_element(self.sinopse).text


        titulo = limpar_dados.remover_texto_titulo(titulo)
        genero = limpar_dados.transformar_genero(genero)
        qualidade_audio = limpar_dados.limpar_video_e_audio(qualidade_audio)
        qualidade_video = limpar_dados.limpar_video_e_audio(qualidade_video)
        id_imdb = limpar_dados.pegar_id_imdb(imdb_id)
        imdb_nota = limpar_dados.limpar_nota_imdb(imdb_nota)
        lancamento = limpar_dados.limpar_lancamento(lancamento)
        sinopse = limpar_dados.limpar_sinopse(sinopse)


        genero = Genero(genero=genero)
        return Filme(titulo=titulo, generos=genero,
                        qualidade_audio=qualidade_audio,
                        qualidade_video=qualidade_video,
                        id_imdb=id_imdb, lancamento=lancamento,
                        poster=poster,sinopse=sinopse)
    def dados_download_filme(self) -> Iterable[str]:
        versoes = self.find_elements(self.versoes_filme)
        for versao in versoes:
            yield versao.text

    def pegar_link_torrent(self, num: int) -> str:
        return self.driver.execute_script(f"return getLinkDB({num})")

