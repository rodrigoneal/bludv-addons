import httpx
from bs4 import BeautifulSoup

base_url: str = "https://bludvfilmes.tv/lancamento/2023/{}"


def _parser_url(page: int) -> str:
    if page == 0:
        return base_url.format("")
    else:
        return base_url.format(f"page/{page}")
    
def posts_passados(client: httpx.Client, url: str) -> list[str]:
    response = client.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [loc.text for loc in soup.find_all("loc")]

def pegar_informacoes(html_page: str, buscar_texto: str):
    soup = BeautifulSoup(html_page, 'html.parser')
    strong_tag = soup.find('strong', string=buscar_texto)
    return strong_tag.next_sibling.strip()
