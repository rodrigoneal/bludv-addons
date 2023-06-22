import re

from bs4 import BeautifulSoup

from torrents import TorrentInfo, magnet_to_valida_torrent


def é_dublado(text: str) -> bool:
    padrao = re.compile(r"\b(DUAL|DUBLADO|PT-BR)\b",
                        re.IGNORECASE)
    match = re.search(padrao, text)
    if match:
        return True
    return False


def informacao_video(*, name: str, idioma: str) -> str:
    return " - ".join([idioma, name])

def pegar_temporada(text:str):
    padrao_episodio = re.compile(r"(S|T)(\d{2})(E)(\d{2})", flags=re.IGNORECASE)
    match = re.search(padrao_episodio, text)
    if match:
        temporada = int(match.group(2))
        episodio = int(match.group(4))
    return {"temporada":temporada, "episodio": episodio}

def pegar_links_torrent(html_page: str) -> list[TorrentInfo]:
    padrao = re.compile(r"^magnet:\?xt=urn")
    soup = BeautifulSoup(html_page, 'html.parser')
    elementos = [elemento_a.get("href") for elemento_a in
                  soup.find_all("a", href=padrao)]
    return [magnet_to_valida_torrent(elemento) for elemento in elementos]

def pegar_info_hash(torrents_info: list[TorrentInfo]) -> list[str]:
    return [torrent_info.infohash for torrent_info in torrents_info]

def pegar_title_torrent(torrents_info: list[TorrentInfo]) -> list[str]:
    titles = []
    for torrent_info in torrents_info:
        name = torrent_info.name
        idioma = "&#127482;&#127480;"
        if é_dublado(name):
            idioma = "&#127463;&#127479;"
        title = informacao_video(name=name, idioma=idioma)
        titles.append(title)
    return titles

def posts_passados(html_page) -> list[str]:
    soup = BeautifulSoup(html_page, 'html.parser')
    return [loc.text for loc in soup.find_all("loc")]


def pegar_informacoes(html_page: str, buscar_texto: str):
    soup = BeautifulSoup(html_page, 'html.parser')
    strong_tag = soup.find('strong', string=buscar_texto)
    return strong_tag.next_sibling.strip()