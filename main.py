from selenium_tools.selenium_driver import SeleniumDriver

from db import db_collection
from src.download.urls import urls_filmes
from src.pages.pages import AbrirFilme, DadosFilme, Index

driver = SeleniumDriver()

movies = urls_filmes()

url_principal = "https://bludvfilmes.tv"
index = Index(driver)
abrir_filme = AbrirFilme(driver, url=url_principal)
dados_filme = DadosFilme(driver)

for _ in range(10):
    if index.abrir_pagina.esta_aberta(url=url_principal):
        break

total_filmes = len(movies)
for num, url in enumerate(movies):
    print(url)
    print(f"{num} de {total_filmes}")
    abrir_filme.url = url
    abrir_filme.open()
    filme = dados_filme.pegar_dados.informacoes_filme()
    db_collection.insert_one(filme.dict())
