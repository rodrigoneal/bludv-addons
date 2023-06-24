from typing import Any

from pydantic import BaseModel, Field


class Catalog(BaseModel):
    id: str
    name: str
    type: str


class Meta(BaseModel):
    id: Any
    name: str
    type: str = Field(default="movie")
    poster: str


class Movie(BaseModel):
    metas: list[Meta] | None = []


class Stream(BaseModel):
    name: str | None
    infoHash: str
    description: str



class Streams(BaseModel):
    streams: list[Stream] | None = []