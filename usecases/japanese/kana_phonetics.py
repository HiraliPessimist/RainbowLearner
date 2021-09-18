import re

import jaconv
import spacy


class Furigana:
    """Add tags of HTML by pronunciations of Kanji."""
    _has_instance = None

    def __new__(cls):
        if not cls._has_instance:
            cls._has_instance = super(Furigana, cls).__new__(cls)
            cls.__re_compile()
            cls.nlp = spacy.load("ja_ginza")
        return cls._has_instance

    def export_html(self, text_post: str) -> str:
        """
        The text file change to HTML sentences.

        Args:
            text_post (str): Wish the text to add the ruby

        Returns:
            str: HTML format text
        """

        sentences: list = list()
        line: str = ""

        texts = "<br>\n".join(text_post.splitlines())

        for text in texts:
            for word in text:
                line += word
        sentences.append(line)

        fetch_char: list[tuple[str, str]] = self._fetch_characters(sentences)
        phonetic_list: list[tuple[str, str]] = self._remove_ascii_and_hiragana(
            fetch_char)
        converted: list[str] = self._put_on(phonetic_list)

        return "".join(converted)

    @classmethod
    def __re_compile(cls) -> None:
        """Regular expression patterns"""
        cls.re_hiragana: str = re.compile("[ぁ-ん]")
        cls.re_katakana: str = re.compile("[ァ-ン]")
        cls.re_zenkigou: str = re.compile("︰-＠")
        cls.re_kanji: str = re.compile("[一-龥]")
        cls.re_ascii: str = re.compile("[!-~]")

    def _fetch_characters(self, sentences: list[str]) -> list[tuple[str, str]]:
        """
        Convert text to list of originals and Katakana.

        Args:
            sentences List[str]: To convert a text

        Returns:
            List[Tuple[str, str]]: [(original word, katakana), ...]
        """
        tokens: list = list()
        for sentence in sentences:
            doc = self.nlp(sentence)
            for sent in doc.sents:
                for token in sent:
                    tokens.append(token)

        words: list = list()
        for i, token in enumerate(tokens):
            words.append((token.orth_, token.doc.user_data["reading_forms"][i]))

        return words

    def _remove_ascii_and_hiragana(self, words: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """
        Ascii and Hiragana aren't need pronunciation,
        So, this method are removing these.

        Args:
            words (List[Tuple[str]]): Phrases and pronunciations list
                i.e. [(original word, katakana), ...]

        Returns:
            List[Tuple[str]]: ascii and hiragana word is removing.
                    kanji -> hiragana
                    other  -> **None**
                i.e. [(word, reading), ...]]
        """
        new_words: list[tuple[str, str]] = list()
        for word, reading in words:
            if (re.search(self.re_kanji, word)
                    or re.search(self.re_zenkigou, word)):
                new_words.append((word, jaconv.kata2hira(reading)))
            else:
                new_words.append((word, ""))
        return new_words

    def _put_on(self, words_list: list[tuple[str, str]]) -> list[str]:
        """
        Putting <ruby> tags on a text.

        Args:
            words_list (List[Tuple[str, str]]): Phrases and pronunciations list
                e.g. [("囲碁", "いご"), ...]
        Returns:
            List[str]: Text with <ruby> tags
                e.g. "<ruby>囲碁<rp>(</rp><rt>いご</rt><rp>)</rp></ruby>..."
        """

        sentences: list[str] = list()
        for word, reading in words_list:
            # Extract extra ruby char from word
            extra_char: list[str] = re.findall(self.re_hiragana, word)
            for char in extra_char:
                reading = reading.replace(char, "\u3000")
            if reading != "":
                sentences.append(
                    f"<ruby>{word}<rp>(</rp><rt>{reading}</rt><rp>)</rp></ruby>"
                )
            else:
                sentences.append(word)
        return sentences
