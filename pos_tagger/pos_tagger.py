from pos_tagger.spanish_tagger.perceptron_tagger import CESSPerceptronTagger
from typing import List
from pos_tagger.spanish_tagger.spanish_spaghetti_tagger import CESSSpaghettiTagger
from utils.spacy_utils import get_spacy_model
import nltk

class POSTagger:
    
    def __init__(self, name: str) -> None:
        self.name = name
    
    def pos_tags(self, tokens: List[str], language: str) -> List[str]:
        """
        Return the POS tags from `tokens`.
        
        tokens: Tokens of the sentence.
        language: Token's language
        
        return: List of POS tags
        """
        raise NotImplementedError()
    
    def pos_tags_sents(self, sentences: List[List[str]], language: str) -> List[List[str]]:
        """
        Return the POS tags from `tokens`.
        
        sentences: Tokens of the sentences.
        language: Sentence's language
        
        return: List of POS tags of the sentences
        """
        raise NotImplementedError()
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return str(self)
    
class SpacyPOSTagger(POSTagger):
    
    def __init__(self) -> None:
        super().__init__("spacy")
        self._spacy_to_universal = {
            "ADJ": "ADJ",
            "ADP": "ADP",
            "ADV": "ADV",
            "AUX": "VERB",
            "CONJ": "CONJ",
            "CCONJ": "CONJ",
            "DET": "DET",
            "INTJ": "NOUN", # Not sure about this one
            "NOUN": "NOUN",
            "NUM": "NUM",
            "PART": "PRT",
            "PRON": "PRON",
            "PROPN": "NOUN",
            "PUNCT": ".",
            "SCONJ": "CONJ",
            "SYM": "X",
            "VERB": "VERB",
            "X": "X",
        }
    
    def pos_tags(self, tokens: List[str], language: str) -> List[str]:
        tokens = " ".split(tokens)
        nlp = get_spacy_model(language, True)
        pos = [self._spacy_to_universal[x.pos_] for x in nlp(tokens)]
        return pos

    def pos_tags_sents(self, sentences: List[List[str]], language: str) -> List[List[str]]:
        nlp = get_spacy_model(language, True)
        sentences = [" ".join(x for x in sentence) for sentence in sentences]
        sentences = [[self._spacy_to_universal[x.pos_] for x in nlp(sentence)] for sentence in sentences]
        return sentences
    
class NLTKPOSTagger(POSTagger):
    
    def __init__(self, spanish_tagger="perceptron") -> None:
        """
        spanish_tagger: Wich type of tagger will be used in spanish. Can be
        `perceptron` or `spaghetti`
        """
        super().__init__("nltk")
        if spanish_tagger == "perceptron":
            self.spanish_tagger = CESSPerceptronTagger()
        elif spanish_tagger == "spaghetti":
            self.spanish_tagger = CESSSpaghettiTagger()
    
    def pos_tags(self, tokens: List[str], language: str) -> List[str]:
        if language in ["english", "russian"]:
            return [x[1] for x in nltk.pos_tag(tokens, tagset="universal", lang=language[:3])]
        elif language in ["spanish"]:
            return self.spanish_tagger.pos_tag(tokens)
        
    def pos_tags_sents(self, sentences: List[List[str]], language: str) -> List[List[str]]:
        if language in ["english", "russian"]:
            return [[tok[1] for tok in sentence] for sentence in nltk.pos_tag_sents(sentences, tagset="universal", lang=language[:3])]
        elif language in ["spanish"]:
            return self.spanish_tagger.pos_tag_sents(sentences)
