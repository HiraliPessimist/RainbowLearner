from datetime import datetime

from usecases.english.ipa_phonetics import IPA
from usecases.japanese.kana_phonetics import Furigana


class Japanese:
    def __init__(self) -> None:
        self.furigana = Furigana()

    async def post(self, req, resp) -> None:
        data = await req.media()
        resp.media["date"] = datetime.today()
        resp.media["text"] = data['raw-text']
        resp.media["html"] = self.furigana.export_html(data['raw-text'])
