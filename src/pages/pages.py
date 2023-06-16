from selenium_tools.page_objects import Page

from src.pages.elements import AbrirPagina, PegarDados


class Index(Page):
    abrir_pagina = AbrirPagina()

class AbrirFilme(Page):
    ...

class DadosFilme(Page):
    pegar_dados = PegarDados()