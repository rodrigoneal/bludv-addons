import asyncio
import datetime
import re

import httpcore
import httpx

from src.translate import translate_gen


def remover_texto_titulo(text: str) -> str:
    return text.replace("Título Original: ", "")


def _remover_texto_genero(text: str) -> str:
    return text.replace("Gênero: ", "").strip()


def _genero_pt_p_en(text: str) -> str:
    return translate_gen(text)


def transformar_genero(text: str) -> list[str]:
    _texto = _remover_texto_genero(text)
    traduzido = _genero_pt_p_en(_texto)
    return [t.strip() for t in traduzido.split("|")]


def limpar_video_e_audio(text: str) -> int:
    qualidade = re.search(r"(\d+)", text).group()
    return int(qualidade)


def limpar_versao(text: str) -> str:
    regex = re.compile(r"(?i)\b(dual|dublado)\b")
    if regex.search(text.lower()):
        return "Dublado"
    else:
        return "Legendado"


def limpar_qualidade_torrent(text: str) -> str:
    padrao = r"([A-Za-z-]+ \d+p(?: [A-Za-z0-9\s]+)?)"
    match = re.search(padrao, text)
    if match:
        return match.group(0).strip()


def limpar_atualizacao(text: str) -> str:
    padrao = r"(\d{2}\/\d{2}\/\d{4})"
    match = re.search(padrao, text)
    if match:
        return match.group(1)


async def torrent_hash(link_magnet: str) -> httpx.Response:
    json_data = {
        "query": link_magnet,
    }
    url = "http://localhost:3000"
    async with httpx.AsyncClient() as client:
        return await client.post(url, json=json_data, timeout=None)


async def pagar_link_torrent(links_magnet: list[str]) -> list[httpx.Response]:
    return await asyncio.gather(
        *[torrent_hash(link_magnet) for link_magnet in links_magnet]
    )


def parser_response(response: httpx.Response) -> str:
    info_hash = response.json()["data"]["infoHash"]
    name = response.json()["data"]['name']
    return {"hash": info_hash, "name": name}


def limpar_link_torrent(links_magnet: list[str]):
    results = asyncio.run(pagar_link_torrent(links_magnet))
    return [parser_response(result) for result in results]


def pegar_id_imdb(text: str) -> str:
    padrao = r"\/title\/([a-z0-9]+)\/"
    match = re.search(padrao, text)
    if match:
        return match.group(1)


def limpar_lancamento(text: str) -> str:
    padrao = r"\d{4}"
    match = re.search(padrao, text)
    if match:
        return match.group()


def limpar_sinopse(text: str) -> str:
    padrao = r"(?<=,).*"
    match = re.search(padrao, text)
    if match:
        return match.group().strip()


def limpar_poster(text: str) -> str:
    if text:
        padrao = r"\/([^\/]+)\.jpg"
        match = re.search(padrao, text)
        if match:
            return match.group(1)
    return None


def limpar_duracao(text: str) -> str:
    padrao_hora = r"(\d+) H"
    padrao_minuto = r"(\d+) Min"
    match_hora = re.search(padrao_hora, text)
    match_min = re.search(padrao_minuto, text)
    if match_hora:
        hora = int(match_hora.group(1))
    else:
        hora = 0
    if match_min:
        min = int(match_min.group(1))
    else:
        min = 0
    duracao = datetime.timedelta(hours=hora, minutes=min)
    return f"{round(duracao.total_seconds() / 60)}m"
