import re
from datetime import datetime

from bs4 import BeautifulSoup

from src.utils.torrents import TorrentInfo, magnet_to_valida_torrent


def pegar_imdb(soup: BeautifulSoup) -> str | None:
    padrao = re.compile(r"(tt\d+)")
    imdb_link = soup.find(
        "a", href=lambda href: href and "imdb.com/title" in href)
    if imdb_link:
        href = imdb_link.get("href")
        return re.search(padrao, href).group(1)
    return None


def é_dublado(text: str) -> bool:
    padrao = re.compile(r"\b(DUAL|DUBLADO|PT-BR|PORTUGUESE)\b",
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
    padrao_sem_epidosio = r"S(\d+)"
    match = re.search(padrao_episodio, text)
    if match:
        temporada = int(match.group(2))
        episodio = int(match.group(4))
    else:
        match = re.search(padrao_sem_epidosio, text)
        if match:
            temporada = int(match.group(1))
    return {"season": temporada, "episode": episodio}


def pegar_links_torrent(soup: BeautifulSoup) -> list[TorrentInfo]:
    padrao = re.compile(r"^magnet:\?xt=urn")
    elementos = [elemento_a.get("href") for elemento_a in
                 soup.find_all("a", href=padrao)]
    return [magnet_to_valida_torrent(elemento) for elemento in elementos]


def pegar_title_torrent(link: str) -> str:
    name = link
    idioma = "\U0001F1EC\U0001F1E7"
    if é_dublado(name):
        idioma = "\U0001F1E7\U0001F1F7"
    name = name.replace(".", " ")
    return informacao_video(name=name, idioma=idioma)


def pegar_resolucao_video(text: str) -> str:
    text = text.replace(".", " ")
    padrao = r"\d+[Kk]\s|\d{3,4}[Pp]\s"
    match = re.search(padrao, text)
    if match:
        return match.group(0).strip()
    return ""


def pegar_poster(soup: BeautifulSoup):
    div_content = soup.find("div", class_="content")
    img_tag = div_content.find("img")
    return img_tag.get("data-src")


def posts_passados(page_html) -> list[str]:
    soup = BeautifulSoup(page_html, 'html.parser')
    return [loc.text for loc in soup.find_all("loc")]


def categoria_video(soup: BeautifulSoup):
    categorias = ("Documentário", "Filmes",
                  "Novela", "Anime", "Séries")
    div_category = soup.find("div", class_="category")
    for categoria in categorias:
        if div_category.find("a", text=categoria):
            return categoria.replace("á", "a").replace("é","e")

def tipo_video(soup: BeautifulSoup)-> str:
    categorias = soup.find("div", class_="category")
    if "Filmes" in categorias.text:
        return "movie"
    else:
        return "series"


def data_postagem(soup: BeautifulSoup) -> datetime:
    padrao = r"\d{2}/\d{2}/\d{4}"
    texto = soup.find("div", class_="icon").text
    match = re.search(padrao, texto)
    if match:
        atualizado = match.group(0)
        return datetime.strptime(atualizado,
                                 "%d/%m/%Y")
    return


def pegar_informacoes(soup: BeautifulSoup, buscar_texto: str):
    strong_tag = soup.find('strong', string=buscar_texto)
    return strong_tag.next_sibling.strip()
