import json
import logging
from typing import Literal

import emoji
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import BackgroundTasks, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.db import crud, database
from src.schemas import schemas
from src.utils import scraper


def emoji_decoder(data):
    if isinstance(data, str):
        return emoji.demojize(data)
    return data


logging.basicConfig(format="%(levelname)s::%(asctime)s - %(message)s",
                    datefmt="%d-%b-%y %H:%M:%S", level=logging.INFO)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.mount("/static", StaticFiles(directory="resources"), name="static")
# TEMPLATES = Jinja2Templates(directory="resources")


def replace_emoji(match):
    code_point = match.group(0).encode().decode('unicode-escape')
    return emoji.emojize(code_point, use_aliases=True)


with open("resources/manifest.json") as file:
    # Função personalizada para substituir a sequência de escape pela representação do emoji

    # Substituir a sequência de escape Unicode pela representação do emoji
    json_data = emoji.demojize(file.read(), delimiters=(
        "\\", "\\")).encode().decode('unicode-escape')
    manifest = json.loads(json_data, object_hook=emoji_decoder)


@app.on_event("startup")
async def init_db():
    await database.init()


@app.on_event("startup")
async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scraper.run_schedule_scrape, CronTrigger(hour="*/3"))
    scheduler.start()
    app.state.scheduler = scheduler


@app.on_event("shutdown")
async def stop_scheduler():
    app.state.scheduler.shutdown(wait=False)


@app.get("/manifest.json")
async def get_manifest(response: Response):
    response.headers.update(
        {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"})
    return manifest


@app.get("/catalog/movie/{catalog_id}.json", response_model=schemas.Movie)
@app.get("/catalog/movie/{catalog_id}/skip={skip}.json", response_model=schemas.Movie)
async def get_catalog(response: Response, catalog_id: str, skip: int = 0):
    response.headers.update(
        {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"})
    movies = schemas.Movie()
    movies.metas.extend(await crud.get_meta(catalog_id, skip))
    return movies


@app.get("/catalog/series/{catalog_id}.json", response_model=schemas.Movie)
@app.get("/catalog/series/{catalog_id}/skip={skip}.json", response_model=schemas.Movie)
async def get_catalog(response: Response, catalog_id: str, skip: int = 0):
    response.headers.update(
        {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"})
    movies = schemas.Movie()
    movies.metas.extend(await crud.get_meta(catalog_id, skip))
    return movies


@app.get("/meta/movie/{meta_id}.json")
async def get_meta(meta_id: str, response: Response):
    response.headers.update(
        {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"})
    return await crud.get_movie_meta(meta_id)


@app.get("/stream/movie/{video_id}.json", response_model=schemas.Streams)
async def get_stream(video_id: str, response: Response):
    response.headers.update(
        {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"})
    streams = schemas.Streams()
    streams.streams.extend(await crud.get_movie_streams(video_id))
    return streams


@app.post("/scraper")
def run_scraper(
    background_tasks: BackgroundTasks,
    language: Literal["tamil", "malayalam", "telugu",
                      "hindi", "kannada", "english"] = "tamil",
    video_type: Literal["hdrip", "tcrip", "dubbed", "series"] = "hdrip",
    pages: int = 1,
    start_page: int = 1,
    is_scrape_home: bool = False,
):
    background_tasks.add_task(
        scrap.run_scraper, language, video_type, pages, start_page, is_scrape_home)
    return {"message": "Scraping in background..."}


@app.get("/meta/series/{meta_id}.json")
async def get_series_meta(meta_id: str, response: Response):
    response.headers.update(
        {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"})
    return await crud.get_series_meta(meta_id)


@app.get("/stream/series/{video_id}:{season}:{episode}.json", response_model=schemas.Streams)
async def get_series_streams(video_id: str, season: int, episode: str, response: Response):
    response.headers.update(
        {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*"})
    streams = schemas.Streams()
    streams.streams.extend(await crud.get_series_streams(video_id, season, episode))
    return streams
