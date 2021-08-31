from datetime import date, datetime
from pathlib import Path

import responder
import yaml

from controllers.input import is_limited, limit_characters
from presenters import api
from usecases.japanese.kana_phonetics import Furigana
from usecases.english.ipa_phonetics import IPA


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
        resp.media["date"] = datetime.today()
        resp.media["is-limited"] = is_limited(text)
        if is_limited(text):
            text = limit_characters(text)
        resp.media["text"] = text
        resp.media["html"] = self.furigana.export_html(text)


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
        resp.media["text"] = text
        resp.media["html"] = self.ipa.export_html(text)


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

        # @api.background.task
        # def log():
        #     today = date.today()
        #     exec_time = datetime.today()
        #     raw = '-'.join(raw_text.splitlines())
        #     converted = '-'.join(converted_text.splitlines())
        #     with open(f'./logs/{today}.tsv', mode='a',
        #               encoding='utf-8') as log:
        #         log.write(f"{exec_time}\t{raw}\t{converted}\n")
        #
        # log()
        resp.content = api.template('japanese.html',
                                    raw_text=text,
                                    converted_text=converted_text)


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

        # @api.background.task
        # def log():
        #     today = date.today()
        #     exec_time = datetime.today()
        #     raw = '-'.join(raw_text.splitlines())
        #     converted = '-'.join(converted_text.splitlines())
        #     with open(f'./logs/{today}.tsv', mode='a',
        #               encoding='utf-8') as log:
        #         log.write(f"{exec_time}\t{raw}\t{converted}\n")
        #
        # log()
        resp.content = api.template('english.html',
                                    raw_text=text,
                                    converted_text=converted_text)


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

    logs = Path('./logs')
    if not logs.exists():
        logs.mkdir(mode=0o644)

    print(f"Start in {ENV} mode...")
    api.run(address=SERVER, port=PORT)
