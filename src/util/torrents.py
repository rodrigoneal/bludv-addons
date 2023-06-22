

import base64
import binascii
from collections import namedtuple
from urllib.parse import parse_qs, urlparse

TorrentInfo = namedtuple('TorrentInfo', ['infohash', 'trackers', 'name'])


def magnet_to_valida_torrent(magnet_torrent: str) -> str:
    url = urlparse(magnet_torrent)
    url_query = parse_qs(url.query)
    infohash = url_query["xt"][0].split(":")[2]
    if len(infohash) == 40:
        infohash = binascii.unhexlify(infohash)
    elif len(infohash) == 32:
        infohash = base64.b32decode(infohash)
    else:
        raise Exception("Unable to parse infohash")
    infohash = binascii.hexlify(infohash).decode()
    trackers = url_query.get("tr", [])
    name = url_query.get("dn")
    if name:
        name = name[0]
    return TorrentInfo(infohash=infohash, trackers=trackers, name=name)
