from concurrent.futures import Future, ThreadPoolExecutor, wait
import logging

from utils.spacy_utils import get_spacy_model
from .translator import Translator
from typing import Callable, Dict, List, Optional, Tuple
from corpus_parser.conll_parser import ConllParser
from pathlib import Path
from nltk import sent_tokenize, word_tokenize

class SentenceAligner:
    
    SEPARATOR = " ||| "
    
    def __init__(self, translator: Translator) -> None:
        """
        Initialize aligner
        
        translator: Class in charge of sentence translation
        """
        self.translator = translator
        self.max_worker = 20

    def sentence_alignment_dir(self, corpus_address:Path, sentence_dest:Path, sentences_splitted=True, source_language="english", target_language="spanish", **kwargs):
        """
        Read all cropus files from `corpus_address` and write the respective sentences 
        aligned in `sentence_dest`. The written files will have .align suffix.
        
        corpus_address: Corpus address
        corpus_dest: Path to save the processed corpus
        sentence_dest: Where to save the sentence alignment
        sentences_splitted: If in the conll file the sentence are splitted by an empty line 
        """
        
        if not sentence_dest.exists(): sentence_dest.mkdir(exist_ok=True, parents=True)
        
        bio_parser = ConllParser()
        tags = bio_parser.parse_dir(corpus_address, get_tags = True)
        
        # Activating translator cache with context
        with self.translator:
            for key, annotated_tags_info in tags.items():
                text = " ".join(tok["tok"] for tok in annotated_tags_info)
                sentence_sentence_text = self.make_sentence_sentence_text(
                    text, 
                    sentences_splitted=sentences_splitted, 
                    source_word_tokenizer=lambda x, *args, **kwargs: x.split(), 
                    source_language=source_language, 
                    target_language=target_language, 
                    **kwargs)
                dest_file = sentence_dest / (Path(key).name + ".align")
                dest_file.write_text(sentence_sentence_text)

    def make_sentence_sentence_text(self, 
            text: str, 
            sentences_splitted=True, 
            source_word_tokenizer: Callable[[str,],List[str]]=word_tokenize, 
            target_word_tokenizer: Callable[[str,],List[str]]=word_tokenize, 
            sent_tokenizer: Callable[[str,],List[str]]=sent_tokenize, 
            source_language: str="english", 
            target_language: str="spanish", 
            separator: str=SEPARATOR,
            **kwargs) -> str:
        """
        Split the given `text` sentence by sentence using the given `sent_tokenizer`. The
        split is made by placing in each line the sentence in `source_language`
        followed by `separator` and then the sentence in `target_language`  
        
        text: Text to be splitted
        source_word_tokenizer: Function that receives a text and a language and returns a list with
        the tokens present in text
        target_word_tokenizer: Function that receives a text and a language and returns a list with
        the tokens present in text
        sent_tokenizer: Function that receives a text and a language and returns a list with
        the sentences present in text
        source_language: text's language
        target_language: Language to be translated
        separator: Text separating the sentences in source language and target language
        sentences_splitted: If the text is already splitted by sentences separated with newlines
        
        returns: The aligned text, tokens are separated by spaces
        """
        
        sentences = sent_tokenizer(text, language=source_language) if not sentences_splitted else text.splitlines()
        
        batch = len(sentences)//self.max_worker + 1
        def batch_work(slice: int) -> str:
            result = []
            for sentence in sentences[batch*slice:batch*(slice+1)]:
                # Result is the sentence's tokens separated by spaces
                source_sentence_with_spaces = " ".join(source_word_tokenizer(sentence, language=source_language)).strip()
                target_sentence = self.translator.translate(source_sentence_with_spaces, source_language=source_language, target_language=target_language, **kwargs)
                if target_sentence is not None:
                    target_sentence_with_spaces = " ".join(target_word_tokenizer(target_sentence, language=target_language)).strip()
                else:
                    logging.warning(f"Target sentence translation for {source_sentence_with_spaces} is None. Defaulting translation to {source_sentence_with_spaces}")
                    target_sentence_with_spaces = source_sentence_with_spaces
                result.append((source_sentence_with_spaces, target_sentence_with_spaces))
            return "\n".join(f"{source}{separator}{target}" for source, target in result)

        futures: List[Future] = []
        with ThreadPoolExecutor(max_workers=self.max_worker) as exe:
            for i in range(self.max_worker):
                futures.append(exe.submit(batch_work, i))
                # batch_work(i) # With this the result isn't returned
        wait(futures)
        exceptions = [future.exception() for future in futures if future.exception()]
        
        if exceptions:
            raise Exception(exceptions)

        return "\n".join(future.result() for future in futures if future.result())
