from pathlib import Path
from typing import List
import tensorflow as tf
from utils.notebook_utils import export_notebook_as_module
from nltk.tokenize import word_tokenize, sent_tokenize
from utils.spacy_utils import get_spacy_model
from .segmenter import ArgumentSegmenter, SplittedArgumentInfo
import importlib
import sys
import logging as log

class TensorflowArgumentSegmenter(ArgumentSegmenter):
    
    def __init__(self, info_tag: str, source_language: str, **kwargs) -> None:
        super().__init__(max_worker=1)

        export_notebook_as_module(
            Path(__file__, "..", "models", "segmenter.ipynb").resolve(),
            new_params={
                **kwargs
            },
            new_cap_variables={
                "INFO_TAG": f'"{info_tag}"',
                "LANGUAGE": f'"{source_language}"'
            })

        import segmenter.models.segmenter as segmenter_model
        if "segmenter.models.segmenter" in sys.modules:
            importlib.reload(segmenter_model)

        self._params = segmenter_model.params.copy()
        self.model = segmenter_model.load_and_build_model_from_params(self._params)
        self.source_language = source_language
        self.max_sequence_size = self._params['max_seq_size']
        self.use_spacy = kwargs.get("use_spacy", False)

    def __split_sents(self, text: str) -> List[str]:
        if self.use_spacy:
            nlp = get_spacy_model(self.source_language)
            sentences = [x.text for x in nlp(text).sents]
        else:
            sentences = sent_tokenize(text, language=self.source_language)
        return sentences

    def __word_tokenize(self, text: str) -> List[str]:
        if self.use_spacy:
            nlp = get_spacy_model(self.source_language)
            doc = nlp(text)
            tokens = [x.text for x in doc if "\n" not in x.text and x.text.strip()]
        else:
            tokens = word_tokenize(text, language=self.source_language)
        return tokens

    def extract_arguments_from_text(self, text: str) -> List[SplittedArgumentInfo]:
        
        chunks = []

        sentences = self.__split_sents(text)
        sentences_tokens = [self.__word_tokenize(sentence) for sentence in sentences]

        chunk_len = self.max_sequence_size # Always activate first if
        for sentence_tokens in sentences_tokens:
            if len(sentence_tokens) >= self.max_sequence_size:
                log.warning("A sentence is greater than the model sequence max length. This will cause information loss")
            if len(sentence_tokens) + chunk_len >= self.max_sequence_size:
                chunks.append("")
                chunk_len = 0
            chunks[-1] += " " + " ".join(sentence_tokens)
            chunk_len += len(sentence_tokens)

        data = tf.constant(chunks)
        encoded_tags = self.model(data)
        return [x for chunk, tags in zip(chunks, encoded_tags) for x in zip(chunk.split(), tags)]
