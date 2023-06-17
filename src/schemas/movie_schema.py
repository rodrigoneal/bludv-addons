from pydantic import BaseModel


class LinkTorrent(BaseModel):
    qualidade_torrent: str
    link_torrent: str | None


class VersaoFilme(BaseModel):
    versao: str
    links: list[LinkTorrent] = []

class Genero(BaseModel):
    genero: list[str] = []

class Filme(BaseModel):
    titulo: str
    generos: Genero = []
    qualidade_audio: int
    qualidade_video: int
    id_imdb: str | None
    nota_imbd: float | None
    sinopse: str | None
    poster: str
    lancamento: int
    versao_filme: list[VersaoFilme] = []

class Filmes(BaseModel):
    filme: list[Filme] = []

