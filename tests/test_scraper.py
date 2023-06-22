import httpx

from src.util.scraper import _parser_url, pegar_informacoes, posts_passados


def test_se_passando_0_url_nao_tera_paginacao():
    esperado = "https://bludvfilmes.tv/lancamento/2023/"
    resultado = _parser_url(0)
    assert esperado == resultado

def test_se_passando_1_url_tera_paginacao():
    esperado = "https://bludvfilmes.tv/lancamento/2023/page/1"
    resultado = _parser_url(1)
    assert esperado == resultado

def test_se_pegar_posts_passados():
    esperado = "https://bludvfilmes.tv/cut-color-murder-torrent-2022-web-dl-1080p-dual-audio/"
    url = "https://bludvfilmes.tv/post-sitemap13.xml"
    with httpx.Client() as client:
        resultado = posts_passados(client, url)
    assert esperado in resultado

def test_se_pega_os_dados_do_passado():
    esperado = "Cut, Color, Murder"
    html_page = '<span style="color: black; font-family: Arial, Helvetica, sans-serif;"><strong><em>Título Original:</em></strong> Cut, Color, Murder</span>'
    resultado = pegar_informacoes(html_page, "Título Original:")
    assert esperado == resultado



