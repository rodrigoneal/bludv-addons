import asyncio
import itertools
from typing import Any, Generator
from bs4 import BeautifulSoup

from tqdm import tqdm
import httpx

from extrair_informacao import pegar_imdb, pegar_informacoes, pegar_links_torrent, pegar_temporada, pegar_title_torrent, posts_passados, tipo_video

from imdb import Cinemagoer


base_url: str = "https://bludvfilmes.tv/lancamento/2023/{}"
base_url = "https://bludvfilmes.tv/"
url_post = "post-sitemap{}.xml"

async def scraper(client: httpx.Client, url:str) -> list[bytes]:
    response = await client.get(url)
    return response.content
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

def happy_path(page_html: bytes):
    soup = BeautifulSoup(page_html, 'html.parser')
    name = pegar_informacoes(soup, "Título Original:")
    type = tipo_video(soup)
    links = pegar_links_torrent(soup)
    imdb_id = pegar_imdb(soup)
    for link in links:
        season = pegar_temporada(link.name)["season"]
        episode = pegar_temporada(link.name)["episode"]
        hash = link.infohash
        catalog = pegar_title_torrent(link.name)
        breakpoint()


async def main():
    posts_links = [post_link(link) for link in generator_link()]
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*[scraper(client, link) for link in posts_links])
        posts = [posts_passados(response) for response in responses]
        total = _posts_to_tqdm(posts)
        with tqdm(total=total) as pbar:
            for pages in iter_posts(posts):
                htmls = await asyncio.gather(*[scraper(client, page) for page in pages])
                for html in htmls:
                    imdb_link = happy_path(html)
                pbar.update(4)
                await asyncio.sleep(0.5)


    
        

if __name__ == "__main__":
    response = asyncio.run(main())
    breakpoint()
