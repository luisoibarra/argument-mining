import spacy
from spacy.tokens import Doc

SPACY_LANGUAGE_MODEL_DICT = {
    "english": "en_core_web_trf",
    "spanish": "es_dep_news_trf",
}

SPACY_DICT = {

}

def get_spacy_model(language: str, whitespace_tokenizer = False) -> spacy.language.Language:
    """
    Provides an efficient way to get spacy's languages models.

    language: Language of the model to get
    """
    try:
        model = SPACY_LANGUAGE_MODEL_DICT[language]
    except KeyError:
        raise KeyError(f"{language} not supported. Supported lanugages: {', '.join(SPACY_LANGUAGE_MODEL_DICT)}")
    if model not in SPACY_DICT:
        nlp = spacy.load(model)
        if whitespace_tokenizer:
            nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)
        SPACY_DICT[model] = nlp
    return SPACY_DICT[model]


class WhitespaceTokenizer:
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text: str):
        words = text.split(' ')
        # All tokens 'own' a subsequent space character in this tokenizer
        spaces = [True] * len(words)
        return Doc(self.vocab, words=words, spaces=spaces)
