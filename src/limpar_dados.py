import re

from src.pages.translate import translate_gen


def remover_texto_titulo(text: str)-> str:
    return text.replace("Título Original: ", "")

def _remover_texto_genero(text: str) -> str:
    return text.replace("Gênero: ", "").strip()

def _genero_pt_p_en(text: str) -> str:
    return translate_gen(text)

def transformar_genero(text: str) -> list[str]:
    _texto =_remover_texto_genero(text)
    traduzido = _genero_pt_p_en(_texto)
    return [t.strip() for t in traduzido.split("|")]

def limpar_video_e_audio(text: str) -> int:
    qualidade = re.search(r"(\d+)", text).group()
    return int(qualidade)

def limpar_versao(text: str) -> str:
    return text.replace("VERSÃO ", "")

def limpar_qualidade_torrent(text: str) -> str:
    _dado = text.replace("\nMAGNET-LINK", "").replace("SERVIDOR PARA DOWNLOAD ", "")
    return re.sub(r"\(\d+\.\d+\s*[GgMm][Bb]\)", "", _dado)

def limpar_link_torrent(text: str) -> str:
    magnet = re.match(r"magnet:\?xt=urn:btih:[a-zA-Z0-9]+", text)
    return magnet.group()