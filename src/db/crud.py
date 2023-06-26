import logging
from typing import Optional
from uuid import uuid4

from imdb import Cinemagoer, IMDbDataAccessError

from src.db.models import Bludv
from src.logger import get_logger
from src.schemas import schemas

ia = Cinemagoer()
logger = get_logger("bludv")

async def get_meta(catalog: str,skip: int = 0, limit: int = 100):
    movies_meta = []
    movies = (
        await Bludv.find(Bludv.catalog == catalog)
        .sort("-updated_at")
        .to_list()
    )
    unique_names = []

    for movie in movies:
        meta_data = schemas.Meta.parse_obj(movie)
        meta_data.id = movie.imdb_id if movie.imdb_id else movie.bludv_id
        if movie.name not in unique_names:
            movies_meta.append(meta_data)
            unique_names.append(movie.name)

    return movies_meta


async def get_movies_data(video_id: str, video_type: str = "movie") -> list[Optional[Bludv]]:
    if video_id.startswith("tt"):
        movie_data = await Bludv.find(
            Bludv.imdb_id == video_id, Bludv.type == video_type
        ).to_list()
    else:
        movie_data = await Bludv.find(
            Bludv.bludv_id == video_id, Bludv.type == video_type
        ).to_list()

    return movie_data


async def get_movie_streams(video_id: str):
    movies_data = await get_movies_data(video_id)
    if not movies_data:
        return []

    stream_data = []
    for movie_data in movies_data:
        for video in movie_data.video_qualities:
                stream_data.append(
                    {
                        **video
                    }
                )

    return stream_data


async def get_series_streams(video_id: str, season: int, episode: str):
    series_data = await get_movies_data(video_id, video_type="series")
    if not series_data:
        return []

    stream_data = []
    for series in series_data:
        if series.episode == episode and series.season == season:
            for video in series.video_qualities:

                stream_data.append(
                    {
                        **video
                    }
                )

    return stream_data


async def get_movie_meta(meta_id: str):
    movies_data = await get_movies_data(meta_id)
    if not movies_data:
        return {
            "meta": {
                "id": meta_id,
                "type": "movie",
            }
        }

    return {
        "meta": {
            "id": meta_id,
            "type": "movie",
            "name": movies_data[0].name,
            "poster": movies_data[0].poster,
            "background": movies_data[0].poster,
        }
    }


async def get_series_meta(meta_id: str):
    series_data = await get_movies_data(meta_id, video_type="series")
    if not series_data:
        return {
            "meta": {
                "id": meta_id,
                "type": "series",
            }
        }

    metadata = {
        "meta": {
            "id": meta_id,
            "type": "series",
            "name": series_data[0].name,
            "poster": series_data[0].poster,
            "background": series_data[0].poster,
            "videos": [],
        }
    }
    for series in series_data:
        metadata["meta"]["videos"].append(
            {
                "id": f"{meta_id}:{series.season}:{series.episode}",
                "name": f"{series.name} S{series.season} EP{series.episode}",
                "season": series.season,
                "episode": series.episode,
                "released": series.created_at,
            }
        )

    return metadata


def search_imdb(title: str):
    try:
        result = ia.search_movie(title)
    except IMDbDataAccessError:
        return search_imdb(title)
    for movie in result:
        if movie.get("title").lower() in title.lower():
            return f"tt{movie.movieID}"


async def save_movie_metadata(metadata: dict):
    if not metadata:
        return
    logger.info(f"Salvando >>> {metadata['type']}-{metadata['name']}")
    movie_data = await Bludv.find_one(
        Bludv.name == metadata["name"],
        Bludv.catalog == metadata["catalog"],
        Bludv.season == metadata["season"],
        Bludv.episode == metadata["episode"],
    )

    if movie_data:
        if movie_data.video_qualities == metadata["video_qualities"]:
            logger.info(f"Qualidade do video inalterado")
            return
        else:
            movie_data.video_qualities = metadata["video_qualities"]

        movie_data.created_at = metadata["created_at"]
        logger.info(f"Atualizando qualidade do video {metadata['name']}")
    else:
        movie_data = Bludv.parse_obj(metadata)
        movie_data.video_qualities = metadata["video_qualities"]

        series_data = await Bludv.find_one(
            Bludv.name == metadata["name"],
            Bludv.catalog == metadata["catalog"],
            Bludv.type == "series",
        )
        if series_data:
            movie_data.bludv_id = series_data.bludv_id
            movie_data.imdb_id = series_data.imdb_id
        if not movie_data.imdb_id:
            imdb_id = search_imdb(movie_data.name)
            if any([metadata["type"] == "series" and metadata["episode"].isdigit() and imdb_id,all([metadata["type"] == "movie", imdb_id]),]):
                movie_data.imdb_id = imdb_id
            else:
                movie_data.bludv_id = f"tb{uuid4().fields[-1]}"

        logging.info(f"new movie '{metadata['name']}' added.")

    await movie_data.save()