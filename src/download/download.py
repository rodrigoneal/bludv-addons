from itertools import count

from src import limpar_dados
from src.pages.pages import DadosFilme
from src.schemas.movie_schema import LinkTorrent, VersaoFilme

versoes_filme = []
def download_filme(dados: list[str]) -> list:
    contador = count()
    for dado in dados:
        if dado.startswith("VERSÃO"):
            versao = limpar_dados.limpar_versao(dado)
            versao_filme = VersaoFilme(versao=versao)
            versoes_filme.append(versao_filme)
        elif dado.startswith("SERVIDOR"):
            num = next(contador)
            qualidade = limpar_dados.limpar_qualidade_torrent(dado)
            _magnet = DadosFilme.pegar_dados.pegar_link_torrent(num)
            magnet_torrent = limpar_dados.limpar_link_torrent(_magnet)
            link_torrent = LinkTorrent(
                qualidade_torrent=qualidade, link_torrent=magnet_torrent)
            versao_filme.links.append(link_torrent)
    return versao_filme