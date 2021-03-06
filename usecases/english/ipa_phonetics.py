import csv
import re
from typing import Optional


class IPA:
    """Add tags of HTML by pronunciations of English"""

    _has_instance = None

    def __new__(cls):
        if not cls._has_instance:
            cls._has_instance = super(IPA, cls).__new__(cls)
            cls.__re_compile()
        return cls._has_instance

    def __init__(self) -> None:
        # Load words dictionary
        with open('./domains/english/dict/cmudict', mode='r', newline='', encoding='utf-8') as f:
            tsv_reader = csv.reader(f, delimiter=' ')
            # read_data[i][0]: word
            # read_data[i][1:]: phonetics
            read_data = [row for row in tsv_reader]
            self.dict_data: dict[str, list[str]] = {read_data[i][0]: read_data[i][1:] for i in range(len(read_data))}

        # Load IPA symbols
        with open('./domains/english/dict/symbols', mode='r', newline='', encoding='utf-8') as f:
            tsv_reader = csv.reader(f, delimiter=' ')
            # symbols[i][0]: Alphabet
            # symbols[i][1:]: IPA symbol
            symbols = [row for row in tsv_reader]
            self.symbols: dict[str, str] = {symbols[i][0]: symbols[i][1:] for i in range(len(symbols))}

        # Vowel's symbols for using to change phonetics of "the" before vowels
        with open('./domains/english/dict/vowels', mode='r', newline='', encoding='utf-8') as f:
            tsv_reader = csv.reader(f, delimiter=' ')
            self.vowels: tuple[str] = [tuple(vowels) for vowels in tsv_reader][0]

        # In sentence, when after word is vowel, this value is True.
        self.is_after_vowel = False

    @classmethod
    def __re_compile(cls) -> None:
        """Regular expression patterns"""
        cls.re_non_ascii = re.compile("[^a-zA-Z0-9\']")

    def export_html(self, text_post: str) -> str:
        """
        The text file change to HTML sentences.
        Args:
            text_post(str): Wish the text to add phonetics.
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

        phonetics = self._fetch_phonetics(sentences)
        converted: list[Optional[str]] = self._put_on(phonetics)

        return "".join(converted)

    def _fetch_phonetics(self, sentences: list[str]) -> list[tuple[str, str]]:
        """
        Convert text to list of originals and IPAs.
        Args:
            sentences (List[str]): To convert a text
        Returns:
            List[Tuple[str, str]: [(original word, IPA), ...]
        """
        word_list: list[tuple[str, str]] = list()

        for sentence in sentences:
            # To check the vowels behind ???The???, it processes from the reverse of sentence
            for word in reversed(sentence.split()):
                word_list.append(self._distinguish_the(word))
            word_list.reverse()
        return word_list

    def _distinguish_the(self, word: str) -> tuple[str, str]:
        """
        The word after "the" distinguished vowel or not vowel
        If the word is vowel, the "the" phonetic's is "??i??"
        Args:
            word (str): target word

        Returns:
            Tuple[str, str]: (word, phonetic)
        """
        target = word.replace("<br>", "")
        target = re.sub(self.re_non_ascii, "", target)

        if target == "":
            ipa = ""
        elif target.lower() == "the" and self.is_after_vowel:
            ipa = "??i??"
            self.is_after_vowel = False
        else:
            try:
                ipa = self._convert_ipa(self.dict_data[target.lower()])
                if ipa.startswith(self.vowels):
                    self.is_after_vowel = True
                else:
                    self.is_after_vowel = False
            except KeyError as key:
                print(f"{key} is nothing in the CMU dictionary.")
                ipa = ""
        return word, ipa

    def _convert_ipa(self, alphabets: list[str]) -> str:
        """
        Convert from Alphabet to IPA.
        Args:
            alphabets(List[str]): target word's Arpabet
        Returns:
            (str): IPA symbols
        """
        phonetics: str = ""
        for alphabet in alphabets:
            phonetics += self.symbols[alphabet][0]

        return phonetics

    @classmethod
    def _put_on(cls, words_list: list[tuple[str, str]]) -> list[str]:
        """
        Putting <ruby> tags on a text.

        Args:
            words_list (List[Tuple[str, str]]): Phrases and pronunciations list
                e.g. [("This", "??????s"), ...]

        Returns:
            List[str]: Text with <ruby> tags
                e.g. "<ruby>This<rp>[</rp><rt>??????s</rt><rp>]</rp></ruby> ..."
        """
        sentences: list[Optional[str]] = list()

        for word, phonetics in words_list:
            if "<br>" in word:
                sentences.append(f'<ruby class="under">{word.replace("<br>", "")}'
                                 f'<rp>[</rp><rt>{phonetics}</rt><rp>]</rp></ruby><br>\n')
            elif phonetics != "":
                sentences.append(f'<ruby class="under">{word}'
                                 f'<rp>[</rp><rt>{phonetics}</rt><rp>]</rp></ruby> ')
            else:
                sentences.append(f"{word} ")
        return sentences
