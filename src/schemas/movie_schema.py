from pydantic import BaseModel


class LinkTorrent(BaseModel):
    title: str
    infoHash: str | None


class Filme(BaseModel):
    name: str
    genres: list[str] = []
    qualidade_audio: int
    qualidade_video: int
    id: str | None
    imdbRating: str | None
    description: str | None
    logo: str | None
    releaseInfo: int
    runtime: str | None
    versao_filme: list[LinkTorrent] = []

class Filmes(BaseModel):
    filme: list[Filme] = []

