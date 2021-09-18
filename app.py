from datetime import date, datetime

import responder
import yaml

from controllers.input import is_limited, limit_characters
from presenters import api
from usecases.japanese.kana_phonetics import Furigana
from usecases.english.ipa_phonetics import IPA
from usecases.log import Logs


api = responder.API(
    templates_dir='static/templates',
    auto_escape=True,
    docs_route="/docs",
    title="Pronunciation in HTML",
    version="1.0.0",
    openapi="3.0.3",
    description="Add pronunciation marks to Japanese and English.",
    contact={
        "name": "GuitarBuilderClass",
        "VRChat": "key-chan",
        "Discord": "GuitarBuilderClass#5001"
    }
)


class JapaneseAPI:
    def __init__(self) -> None:
        self.furigana = Furigana()

    async def post(self, req, resp) -> None:
        data = await req.media()
        text = data['raw-text']
        phonetics = self.furigana.export_html(text)
        resp.media["date"] = datetime.today()
        resp.media["is-limited"] = is_limited(text)
        if is_limited(text):
            text = limit_characters(text)
        resp.media["text"] = text
        resp.media["html"] = phonetics

        Logs.create(text, phonetics, req.client.host)


class EnglishAPI:
    def __init__(self) -> None:
        self.ipa = IPA()

    async def on_post(self, req, resp) -> None:
        data = await req.media()
        text = data["raw-text"]
        resp.media["date"] = datetime.today()
        resp.media["is-limited"] = is_limited(text)
        if is_limited(text):
            text = limit_characters(text)
        phonetics = self.ipa.export_html(text)
        resp.media["text"] = text
        resp.media["html"] = phonetics

        Logs.create(text, phonetics, req.client.host)


class Root:
    def on_get(self, req, resp) -> None:
        resp.html = api.template("root.html")


class JapaneseWeb:
    def __init__(self) -> None:
        self.furigana = Furigana()

    def on_get(self, req, resp) -> None:
        raw_text = "樹木希林はFUJIカラーで写せない遠いお正月へ旅立ったよ。"
        converted_text = self.furigana.export_html(raw_text)
        resp.html = api.template('japanese.html',
                                 raw_text=raw_text,
                                 converted_text=converted_text)

    async def on_post(self, req, resp) -> None:
        data = await req.media(format='form')
        text = data["raw-text"]
        text = limit_characters(text).replace("<", "&lt").replace(">", "&gt")
        converted_text = self.furigana.export_html(text)

        resp.content = api.template('japanese.html',
                                    raw_text=text,
                                    converted_text=converted_text)

        Logs.create(text, converted_text, req.client.host)


class EnglishWeb:
    def __init__(self) -> None:
        self.ipa = IPA()

    def on_get(self, req, resp) -> None:
        raw_text = "I just read the article on the newspaper."
        converted_text = self.ipa.export_html(raw_text)
        resp.html = api.template('english.html',
                                 raw_text=raw_text,
                                 converted_text=converted_text)

    async def on_post(self, req, resp) -> None:
        data: object = await req.media(format='form')
        text: str = data["raw-text"]
        text = limit_characters(text).replace("<", "&lt").replace(">", "&gt")
        converted_text = self.ipa.export_html(text)

        resp.content = api.template('english.html',
                                    raw_text=text,
                                    converted_text=converted_text)

        Logs.create(text, converted_text, req.client.host)


api.add_route('/', Root)
api.add_route('/japanese', JapaneseWeb)
api.add_route('/english', EnglishWeb)


if __name__ == '__main__':
    from config import setting
    with open(f'./config/{setting.MODE}.yaml') as settings:
        mode = yaml.load(settings, Loader=yaml.FullLoader)
        ENV = mode['ENV']
        SERVER = mode['SERVER']
        PORT = mode['PORT']

    print(f"Start in {ENV} mode...")
    api.run(address=SERVER, port=PORT)
