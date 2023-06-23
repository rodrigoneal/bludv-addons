import re

from bs4 import BeautifulSoup

from torrents import TorrentInfo, magnet_to_valida_torrent


def pegar_imdb(soup: BeautifulSoup) -> str | None:
    padrao = re.compile(r"(tt\d+)")
    imdb_link = soup.find("a", href=lambda href: href and "imdb" in href)
    if imdb_link:
        href = imdb_link.get("href")
        return re.search(padrao, href).group(1)
    return None


def é_dublado(text: str) -> bool:
    padrao = re.compile(r"\b(DUAL|DUBLADO|PT-BR)\b",
                        re.IGNORECASE)
    match = re.search(padrao, text)
    if match:
        return True
    return False


def informacao_video(*, name: str, idioma: str) -> str:
    return " - ".join([idioma, name])


def pegar_temporada(text: str):
    temporada = None
    episodio = None
    padrao_episodio = re.compile(
        r"(S|T)(\d{2})(E)(\d{2})", flags=re.IGNORECASE)
    match = re.search(padrao_episodio, text)
    if match:
        temporada = int(match.group(2))
        episodio = int(match.group(4))
    return {"season": temporada, "episode": episodio}


def pegar_links_torrent(soup: BeautifulSoup) -> list[TorrentInfo]:
    padrao = re.compile(r"^magnet:\?xt=urn")
    elementos = [elemento_a.get("href") for elemento_a in
                 soup.find_all("a", href=padrao)]
    return [magnet_to_valida_torrent(elemento) for elemento in elementos]


def pegar_title_torrent(link: str) -> str:
    name = link
    idioma = "&#127482;&#127480;"
    if é_dublado(name):
        idioma = "&#127463;&#127479;"
    name = name.replace(".", " ")
    return informacao_video(name=name, idioma=idioma)

def pegar_poster(page_html: bytes):
    soup = BeautifulSoup(page_html, 'html.parser')
    div_content = soup.find("div", class_="content")
    img_tag = div_content.find("img")
    return img_tag.get("src")


def posts_passados(page_html) -> list[str]:
    soup = BeautifulSoup(page_html, 'html.parser')
    return [loc.text for loc in soup.find_all("loc")]

def tipo_video(soup: BeautifulSoup):
    div_category = soup.find("div", class_="category")
    link_series = div_category.find("a", text="Séries")
    if link_series:
        return "series"
    return "movies"

def pegar_informacoes(soup: BeautifulSoup, buscar_texto: str):
    strong_tag = soup.find('strong', string=buscar_texto)
    return strong_tag.next_sibling.strip()
