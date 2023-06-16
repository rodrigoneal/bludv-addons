from pydantic import BaseModel


class LinkTorrent(BaseModel):
    qualidade_torrent: str
    link_torrent: str


class VersaoFilme(BaseModel):
    versao: str
    links: list[LinkTorrent] = []


class Filme(BaseModel):
    titulo: str
    genero: list[str] = []
    qualidade_audio: int
    qualidade_video: int
    versao_filme: list[VersaoFilme] = []

class Filmes(BaseModel):
    filme: list[Filme] = []

