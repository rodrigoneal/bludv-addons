import asyncio
import itertools
from datetime import datetime
from typing import Any, Generator
from uuid import uuid4

import httpx
from bs4 import BeautifulSoup
from imdb import Cinemagoer, IMDbDataAccessError
from qbittorrent import Client
from tqdm import tqdm

from src.db import database
from src.db.crud import save_movie_metadata
from src.logger import get_logger
from src.utils import extrair_informacao
from src.utils.torrents import listar_episodios

base_url: str = "https://bludvfilmes.tv/lancamento/2023/{}"
base_url = "https://bludvfilmes.tv/"
url_post = "post-sitemap{}.xml"

ia = Cinemagoer()

NUM_REQUEST = 12

logger = get_logger("bludv")

async def scraper(client: httpx.Client, url: str) -> list[bytes]:
    logger.info(f"Requisição na url >>> {url}")
    try:
        response = await client.get(url)
    except httpx.ReadTimeout:
        await asyncio.sleep(0.5)
        return await scraper(client, url)
    return response.content


def generator_link() -> Generator[int, Any, None]:
    for i in range(13, 8-1, -1):
        yield i


def iter_posts(posts: list[list]) -> list[str]:
    posts = list(itertools.chain.from_iterable(posts))
    iterador = iter(posts)
    while True:
        grupo = list(itertools.islice(iterador, NUM_REQUEST))
        if not grupo:
            break
        yield grupo


def post_link(index_page: int) -> str:
    return base_url+url_post.format(index_page)


def _posts_to_tqdm(posts):
    _total = list(itertools.chain.from_iterable(posts))
    return len(_total)


def search_imdb(title: str):
    logger.info(f"Procurando no imdb >>> {title}")
    try:
        result = ia.search_movie(title)
    except IMDbDataAccessError:
        return search_imdb(title)
    for movie in result:
        if movie.get("title").lower() in title.lower():
            return f"tt{movie.movieID}"
        
def serie_sem_episodio(*,season,imdb_id, name, description, infoHash):
    episodios = listar_episodios(season,imdb_id)
    _series = {}
    for episode in episodios:
        _series[f"{season},{episode}"] = []
    for k in _series:
        try:
            season, episode = k.split(",")
        except ValueError:
            breakpoint()
        index = int(episode) - 1
        _series[f"{season},{episode}"].append(dict(name=name, description=description, infoHash=infoHash,fileIdx=index))
    return _series


def gerar_metadata(page_html: bytes) -> Generator[dict[str, str | int | dict[str, str] | None],
                                                  Any, None]:
    logger.info(f"Gerando metadada")
    metadata = {}
    soup = BeautifulSoup(page_html, 'html.parser')
    links = extrair_informacao.pegar_links_torrent(soup)
    metadata["type"] = extrair_informacao.tipo_video(soup)
    metadata["poster"] = extrair_informacao.pegar_poster(soup)
    metadata["name"] = extrair_informacao.pegar_informacoes(soup, "Título Original:")
    metadata["imdb_id"] = extrair_informacao.pegar_imdb(soup)
    metadata["catalog"] = "bludv-movie"
    metadata["created_at"] = datetime.now()
    metadata["bludv_id"] = f"tb{uuid4().fields[-1]}"
    aux_dict = {}
    episodios = None
    for link in links:
        season = extrair_informacao.pegar_temporada(link.name)["season"]
        episode = extrair_informacao.pegar_temporada(link.name)["episode"]
        aux_dict[f"{season},{episode}"] = []
        if metadata["type"] == "series" and (season and not episode) and metadata["imdb_id"]:
            episodios = listar_episodios(season, metadata["imdb_id"])
            for episode in episodios:
                aux_dict[f"{season},{episode}"] = []

    for link in links:
        if metadata["type"] == "series":
            metadata["catalog"] = "bludv-series"
        season = extrair_informacao.pegar_temporada(link.name)["season"]
        episode = extrair_informacao.pegar_temporada(link.name)["episode"]
        description = extrair_informacao.pegar_title_torrent(link.name)
        name = "          ".join(("Bludv", extrair_informacao.pegar_resolucao_video(link.name)))
        infoHash = link.infohash
        if metadata["type"] == "series" and (season and not episode) and metadata["imdb_id"]:
            if not aux_dict.get(f"{season},None") is None:
                del aux_dict[f"{season},None"]
            episodios = serie_sem_episodio(season=season, imdb_id=metadata["imdb_id"], name=name,
                               description=description, infoHash=infoHash)
            for k, v in episodios.items():
                aux_dict[k].append(v[0])
        else:         
            aux_dict[f"{season},{episode}"].append(dict(name=name, description=description, infoHash=infoHash,fileIdx=None))
    for k, v in aux_dict.items():
        season, episode = k.split(",")
        try:
            metadata["season"] = int(season)
        except ValueError:
            metadata["season"] = None
        metadata["episode"] = episode
        metadata["video_qualities"] = v
        yield metadata


async def main():
    await database.init()
    posts_links = [post_link(link) for link in generator_link()]
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(*[scraper(client, link) for link in posts_links])
        posts = [extrair_informacao.posts_passados(
            response) for response in responses]
        total = _posts_to_tqdm(posts)
        with tqdm(total=total) as pbar:            
            for pages in iter_posts(posts):
                htmls = await asyncio.gather(*[scraper(client, page) for page in pages])
                for html in htmls:
                    [await save_movie_metadata(metadata) for metadata in gerar_metadata(html)]
                pbar.update(NUM_REQUEST)
                await asyncio.sleep(0.5)

async def run_schedule_scrape():
    await database.init()
    ano_atual = datetime.now().year
    url = f"https://bludvfilmes.tv/lancamento/{ano_atual}/"
    async with httpx.AsyncClient() as client:
        response = await scraper(client, url)
        [await save_movie_metadata(metadata) for metadata in gerar_metadata(response)]
