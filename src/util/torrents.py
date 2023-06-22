


import base64
import binascii
from urllib.parse import parse_qs, urlparse

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
        
    return infohash, trackers, name


url = "magnet:?xt=urn:btih:MHQQZDRDRSLMRUM2QDMFHSIKK5DAEMR2&dn=Avatar%20-%20O%20Caminho%20da%20%C3%81gua%202022%20WEB-DL%201080p%20x264%20DUAL%207.1&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80%2Fannounce"

hash = magnet_to_valida_torrent(url)
breakpoint()