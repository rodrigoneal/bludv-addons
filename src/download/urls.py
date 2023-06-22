from typing import Generator


movies = []
series = []

urls = open("links.txt").readlines()

def urls_filmes() -> Generator:
    for url in urls:
        if "temporada" not in url:
            url = url.replace("\n", "") 
            if url not in movies:
                yield url

def urls_serie() -> list[str]:
    for url in urls:
        url = url.replace("\n", "")
        if "temporada" in url:
            if url not in series:
                series.append(url)
    return series