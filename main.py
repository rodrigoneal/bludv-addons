from selenium_tools.selenium_driver import SeleniumDriver
from tqdm import tqdm


from src.download.urls import urls_filmes
from src.pages.pages import AbrirFilme, DadosFilme, Index
from src.usecases.movies_cases import insert_movie



movies = urls_filmes()


driver = SeleniumDriver(headless=True, log=False).get_driver()

movies = urls_filmes()

url_principal = "https://bludvfilmes.tv"
index = Index(driver)
abrir_filme = AbrirFilme(driver, url=url_principal)
dados_filme = DadosFilme(driver)

for _ in range(10):
    if index.abrir_pagina.esta_aberta(url=url_principal):
        break
pbar = tqdm(movies)
for index, url in enumerate(pbar):
    if index < 440:
        continue
    pbar.set_description("Roubando dados da pagina \U0001F600")
    abrir_filme.url = url
    abrir_filme.open()
    filme = dados_filme.pegar_dados.informacoes_filme()
    insert_movie(filme)
