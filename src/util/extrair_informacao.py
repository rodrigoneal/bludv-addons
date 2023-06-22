import re


def é_dublado(text: str) -> bool:
    padrao = re.compile(r"\b(DUAL|DUBLADO|PT-BR)\b",
                        re.IGNORECASE)
    match = re.search(padrao, text)
    if match:
        return True
    return False


def informacao_video(*, name: str, idioma: str) -> str:
    return " - ".join([idioma, name])
