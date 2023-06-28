import asyncio
import base64
import binascii
import functools
from collections import namedtuple
from urllib.parse import parse_qs, urlparse

from imdb import Cinemagoer

TorrentInfo = namedtuple("TorrentInfo", ["infohash", "trackers", "name"])

ia = Cinemagoer()


def magnet_to_valida_torrent(magnet_torrent: str) -> TorrentInfo:
    url = urlparse(magnet_torrent)
    url_query = parse_qs(url.query)
    hash = url_query["xt"][0].split(":")[2]
    if len(hash) == 40:
        bytes_hash = binascii.unhexlify(hash)
    elif len(hash) == 32:
        bytes_hash = base64.b32decode(hash)
    else:
        raise Exception("Unable to parse infohash")
    infohash = binascii.hexlify(bytes_hash).decode()
    trackers = url_query.get("tr", [])
    name = url_query.get("dn")
    if name:
        name = name[0]
    return TorrentInfo(infohash=infohash, trackers=trackers, name=name)


def run_in_executor(f):
    @functools.wraps(f)
    def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: f(*args, **kwargs))

    return inner


@functools.lru_cache(maxsize=5)
def listar_episodios(season: str, imdb_id: str):
    imdb = imdb_id.replace("tt", "")
    series = ia.get_movie(imdb)
    ia.update(series, "episodes")
    sorted(series["episodes"].keys())
    return list(series["episodes"][season].keys())
