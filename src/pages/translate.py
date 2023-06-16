from deep_translator import GoogleTranslator


def translate_gen(text: str) -> str:
    google_translator = GoogleTranslator(source='pt', target='en')
    return google_translator.translate(text)