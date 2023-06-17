movies = []
series = []

urls = open("links.txt").readlines()

def urls_filmes() -> list[str]:
    for url in urls:
        url = url.replace("\n", "")
        if "temporada" not in url:
            if url not in movies:
                movies.append(url)
    return movies

def urls_serie() -> list[str]:
    for url in urls:
        url = url.replace("\n", "")
        if "temporada" in url:
            if url not in series:
                series.append(url)
    return series