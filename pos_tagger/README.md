# POS Tagger

Package in charge of performing the Part of Speech (POS) tagging.

## Problem

The text is formed by words and each word have a role on the semantic of it. This roles can be
primarly classified into noun, verb, article, adjetive, pronoun, adverb, conjunction and interjection.

This problem can be solved with NLTK for english and russian, but spanish isn't available for default. A new 
tagger was trained with cess corpus.
Spacy also provides support for many languages.

## POSTagger

POSTagger is the base clase in charge of handling the POS tagging. It is implemented with:

- NLTKPOSTagger. The language are restricted to english, russian and spanish. Although is possible to train a new tagger as it was done with the spanish tagger.
- SpacyPOSTagger. The language are restricted to the ones provided by spacy (which are many).

### Usage

```python
from pos_tagger.pos_tagger import SpacyPOSTagger

tagger = SpacyPOSTagger()
sentence = "The POS tags will be extracted From this sentence".split()
pos_tags = tagger.pos_tags(sentence, "english")
```

## Testing Taggers

The `testing_taggers.py` can be run to evaluate the different taggers performace.
