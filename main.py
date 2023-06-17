import re
from itertools import count

from selenium_tools.selenium_driver import SeleniumDriver

from src import limpar_dados
from src.pages.pages import AbrirFilme, DadosFilme, Index
from src.schemas.movie_schema import Filmes, LinkTorrent, VersaoFilme
from db import db_collection

contador = count()


driver = SeleniumDriver()

movies = []
series = []

urls = open("links.txt").readlines()
urls = set(urls)

for url in urls:
    url = url.replace("\n", "")
    if "temporada" in url:
        series.append(url)
    else:
        movies.append(url)

breakpoint()
url_principal = "https://bludvfilmes.tv"
index = Index(driver)
abrir_filme = AbrirFilme(driver, url=url_principal)
dados_filme = DadosFilme(driver)

# A minha operadora de internet bloqueia esse site
# Por isso preciso tentar abrir algumas vezes.
filmes = Filmes()
for _ in range(10):
    if index.abrir_pagina.esta_aberta(url=url_principal):
        break
for url in open("links.txt").readlines():
    if "temporada" in url:
        continue
    url = url.replace("\n", "")
    abrir_filme.url = url
    abrir_filme.open()
    filme = dados_filme.pegar_dados.informacoes_filme()
    versoes_filme = []
    for dado in dados_filme.pegar_dados.dados_download_filme():
        if dado.startswith("VERSÃO"):
            versao = limpar_dados.limpar_versao(dado)
            versao_filme = VersaoFilme(versao=versao)
            versoes_filme.append(versao_filme)
        elif dado.startswith("SERVIDOR"):
            num = next(contador)
            qualidade = limpar_dados.limpar_qualidade_torrent(dado)
            _magnet = dados_filme.pegar_dados.pegar_link_torrent(num)
            magnet_torrent = limpar_dados.limpar_link_torrent(_magnet)
            link_torrent = LinkTorrent(
                qualidade_torrent=qualidade, link_torrent=magnet_torrent)
            versao_filme.links.append(link_torrent)
        contador = count()
    for versao in versoes_filme:
        filme.versao_filme.append(versao)
    db_collection.insert_one(filme.dict())
    filmes.filme.append(filme)
