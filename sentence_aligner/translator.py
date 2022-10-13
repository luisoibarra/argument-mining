import logging
import re
from typing import Callable, Dict, Optional, Tuple
from corpus_parser.conll_parser import ConllParser
from pathlib import Path
from nltk import sent_tokenize
from deep_translator import GoogleTranslator
import json

class Translator:

    def translate(self, source_sentence: str, source_language:str, target_language: str, middle_language: Optional[str] = None, **kwargs) -> str:
        """
        Translate given `sentence` in `source_language` into `target_language`
        
        sentence: Sentence to translate
        source_language: Language of given sentence
        target_language: Language to translate the sentence
        middle_language: If defined the translation process will be: source_language -> middle_language -> target_language

        returns: The translated sentence
        """
        raise NotImplementedError()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class SelfTranslator(Translator):
    
    def translate(self, source_sentence: str, source_language:str, target_language: str, middle_language: Optional[str] = None, **kwargs) -> str:
        return source_sentence
    
class FromCorpusTranslator(Translator):
    """
    Translator that maps the sentences in source_dir with target_dir,
    the files must be named in a way that when sorting them by name 
    the order is the same in both directories. The sentences in the
    files must be in the same order and separated by a new line
    """
    
    SEP_REGEX = r"(?P<letter>)\w\n[\n]+"
    
    def __init__(self, source_dir: Path, target_dir: Path, 
                 source_language: str, target_language: str) -> None:
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        # __translation_dict: 
        #   key=source_lang, dest_lang, source_sentence
        #   value=target_sentence
        self.__translation_dict: Dict[Tuple[str,str,str],str] = {}
        self.__sep_regex = re.compile(self.SEP_REGEX)
        self.__initialize(source_language, target_language)
        
    def translate(self, source_sentence: str, source_language: str, target_language: str, middle_language: Optional[str] = None, **kwargs) -> str:
        try:
            return self.__translation_dict[source_language, target_language, source_sentence]
        except KeyError:
            
            # Replace the \w\n\n match with \w.\n\n
            for match in self.__sep_regex.finditer(source_sentence):
                source_sentence = source_sentence[:match.start()] + \
                                  match.groupdict()["letter"] + ".\n\n" + \
                                  source_sentence[match.end():]
            
            sentences = sent_tokenize(source_sentence, source_language)
            transl = ""
            for sentence in sentences:
                try:
                    transl += \
                        self.__translation_dict[source_language, target_language, sentence] + \
                        " "
                except KeyError:
                    logging.warn(f"Sentence {source_sentence} couldn't be translated")
                    return ""
            return transl[:-1] # Remove the space
    
    def __initialize(self, source_language: str, target_language: str):
        """
        Builds the corpus from the `source_dir` sentences and `target_dir` sentences.
        Both files must be named in a way that by sorting them will yield the 
        corresponding source and target file. 
        
        source_dir: Directory that contains the source target annotation
        target_dir: Directory that contains the source target annotation
        """
        
        source_texts = [(file, file.read_text()) for file in self.source_dir.iterdir()]
        target_texts = [(file, file.read_text()) for file in self.target_dir.iterdir()]
        
        source_texts.sort(key=lambda x: x[0].name)
        target_texts.sort(key=lambda x: x[0].name)

        if len(source_texts) != len(target_texts):
            raise Exception("source_dir and target_dir must have only the source language files with the corresponding target lanuguage files")
        
        for (source_file, source_text), (target_file, target_text) in zip(source_texts, target_texts):
            source_sentences = source_text.split("\n")
            target_sentences = target_text.split("\n")

            if len(source_sentences) != len(target_sentences):
                raise Exception(f"{source_file.name} and {target_file.name} must have the same amount of sentences")

            for source_sentence, target_sentence in zip(source_sentences, target_sentences):
                self.__translation_dict[source_language, target_language, source_sentence] = target_sentence
            
            # Making sentence bigrams
            source_bigrs = [(sentence, source_sentences[i+1]) for i, sentence in enumerate(source_sentences[:-1])]
            target_bigrs = [(sentence, target_sentences[i+1]) for i, sentence in enumerate(target_sentences[:-1])]

            for source_bigr, target_bigr in zip(source_bigrs, target_bigrs):
                self.__translation_dict[source_language, target_language, " ".join(source_bigr)] = " ".join(target_bigr)


class BaseDeepTranslator(Translator):
    """
    Translator based on https://github.com/nidhaloff/deep-translator.
    """
    
    def __init__(self, cache_file: Optional[Path]=None) -> None:
        super().__init__()
        self.cache_file = cache_file
        if not cache_file:
            self.cache_file = Path(__file__, "..", "..", "data", "translation", "translation_cache.json").resolve()
            if not self.cache_file.exists():
                (self.cache_file / "..").resolve().mkdir(parents=True, exist_ok=True)
                self.cache_file.touch()
        # target_sentence = self.cache_dict[source_language][source_sentence][target_language]
        self.cache_dict: Dict[str, Dict[str, Dict[str, str]]] = {}
    
    def __enter__(self):
        # Setup cache dictionary
        if not self.cache_file.exists():
            self.cache_file.touch()
            with self.cache_file.open("w") as file:
                json.dump({}, file)
        try:
            with self.cache_file.open("r") as file:
                self.cache_dict = json.load(file)
        except json.JSONDecodeError:
            with self.cache_file.open("w") as file:
                json.dump({}, file)
            with self.cache_file.open("r") as file:
                self.cache_dict = json.load(file)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Save cache
        self.__save_cache_into_file()

    
    def __save_cache_into_file(self):
        try:
            if self.cache_file and self.cache_dict:
                with self.cache_file.open("w") as file:
                    json.dump(self.cache_dict, file)
        except Exception as e:
            logging.warning(f"Error saving the translation cache: {e}")
    
    def __check_cache(self, source_sentence: str, source_language:str, target_language: str) -> Optional[str]:
        """
        Return the value for source_sentence if exist else return None
        """
        if self.cache_dict is None:
            return None
        current = self.cache_dict
        for key in [source_language, source_sentence, target_language]:
            current = current.get(key)
            if current is None:
                return None
        return current

    def __save_cache(self, source_sentence: str, target_sentence: str, source_language:str, target_language: str):
        """
        Save the translated value for source_sentence with given language
        """
        if self.cache_dict is None:
            return
        current = self.cache_dict
        for key in [source_language, source_sentence]:
            now = current.get(key, {})
            if len(now) == 0:
                current[key] = now
            current = now
        current[target_language] = target_sentence
    
    def get_translator(self, source_language:str, target_language: str):
        """
        Returns the translator to be used
        """
        raise NotImplementedError()
    
    def translate(self, source_sentence: str, source_language:str, target_language: str, middle_language: Optional[str] = None, **kwargs) -> str:
        if middle_language is not None:
            source_sentence = self.translate(source_sentence, source_language, middle_language)
            source_language = middle_language
        cached_translated = self.__check_cache(source_sentence, source_language, target_language)
        if cached_translated is not None:
            return cached_translated
        translator = self.get_translator(source_language, target_language)
        target_sentence = translator.translate(source_sentence)
        self.__save_cache(source_sentence, target_sentence, source_language, target_language)
        return target_sentence

class GoogleDeepTranslator(BaseDeepTranslator):
    """
    Translator based on https://github.com/nidhaloff/deep-translator
    
    Uses the GoogleTranslator
    """
    
    def get_translator(self, source_language:str, target_language: str):
        """
        Returns the translator to be used
        """
        return GoogleTranslator(source=source_language, target=target_language)
