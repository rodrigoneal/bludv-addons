import asyncio
import itertools
import re
from typing import Any, Generator

from tqdm import tqdm
import httpx
from bs4 import BeautifulSoup
from extrair_informacao import informacao_video, é_dublado
from torrents import TorrentInfo, magnet_to_valida_torrent

base_url: str = "https://bludvfilmes.tv/lancamento/2023/{}"

def posts_passados(html_page) -> list[str]:
    soup = BeautifulSoup(html_page, 'html.parser')
    return [loc.text for loc in soup.find_all("loc")]


def pegar_informacoes(html_page: str, buscar_texto: str):
    soup = BeautifulSoup(html_page, 'html.parser')
    strong_tag = soup.find('strong', string=buscar_texto)
    return strong_tag.next_sibling.strip()


# def pegar_todas_versao(html_page: str) -> list[str]:
#     videos_info = []
#     padrao_servidor = re.compile(r'SERVIDOR.*')
#     padrao_versao = re.compile(r'^VERSÃO')
#     soup = BeautifulSoup(html_page, 'html.parser')
#     servidores = soup.find_all('strong', string=padrao_servidor)
#     for servidor in servidores:
#         elemento = servidor.find_previous("strong", string=padrao_versao)
#         if é_dublado(elemento.text):
#             idioma = "&#127463;&#127479;"
#         else:
#             idioma = "&#127482;&#127480;"
#         video_info = informacao_video(qualidade=servidor.text, idioma=idioma)
#         videos_info.append(video_info)
#     return videos_info

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

async def scraper(client: httpx.Client, url:str) -> list[bytes]:
    response = await client.get(url)
    return response.content

base_url = "https://bludvfilmes.tv/"
url_post = "post-sitemap{}.xml"
def generator_link() -> Generator[int, Any, None]:
    for i in range(13,11-1,-1):
        yield i

def iter_posts(posts: list[list])-> list[str]:
    posts = list(itertools.chain.from_iterable(posts))
    iterador = iter(posts)
    while True:
        grupo = list(itertools.islice(iterador, 4))
        if not grupo:
            break
        yield grupo

def post_link(index_page: int) -> str:
    return base_url+url_post.format(index_page)

def _posts_to_tqdm(posts):
    _total = list(itertools.chain.from_iterable(posts))
    return len(_total)

async def main():
    posts_links = [post_link(link) for link in generator_link()]
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*[scraper(client, link) for link in posts_links])
        posts = [posts_passados(response) for response in responses]
        total = _posts_to_tqdm(posts)
        with tqdm(iter_posts(total)) as pbar:
            for pages in iter_posts(posts):
                htmls = await asyncio.gather(*[scraper(client, page) for page in pages])
                pbar.update(4)
                await asyncio.sleep(0.5)


    
        

if __name__ == "__main__":
    response = asyncio.run(main())
    breakpoint()
