from pathlib import Path
if __name__ == "__main__":
    import sys
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

from typing import List, Tuple
from pos_tagger.pos_tagger import POSTagger, SpacyPOSTagger, NLTKPOSTagger
from sklearn.metrics import precision_recall_fscore_support
from nltk.corpus import cess_esp as cess
import pickle

while cess._tagset != 'es-ancora':
    cess._tagset = 'es-ancora'

def unchunck(sentences):
    final_sentences = []
    
    for sentence in sentences:
        final_tokens = []
        for tok, _ in sentence:
            if not tok:
                continue
            tokens = tok.split("_")
            final_tokens.extend([tok for tok in tokens if tok])
        final_sentences.append(final_tokens)
    
    return final_sentences

def test_taggers(tagger: POSTagger, sentences: List[List[str]], tags: List[List[str]]):
    """
    Calculate some statistics about the taggers.
    
    tagger: Tagger to evaluate
    sentences: Sentences to compare the results
    tags: Sentences to compare the results
    
    return precision, recall, f1_macro
    """
    
    tags_result = tagger.pos_tags_sents(sentences, "spanish")

    y_true = [tag for sentence in tags for tag in sentence]
    y_pred = [tag for sentence in tags_result for tag in sentence]

    precision, recall, _, _ = precision_recall_fscore_support(y_true, y_pred, average="micro", zero_division=1)
    _, _, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=1)

    return precision, recall, f1_macro

def compare_taggers():
    
    cess_sents = cess.tagged_sents(tagset='universal')
    
    cess_sents = unchunck(cess_sents)
    # cess_tags = pickle.load(open("delete.pickle", "rb"))

    spacy_tagger = SpacyPOSTagger()
    # Assumes that spacy tagger are 100% correct. This is almost true.
    cess_tags = spacy_tagger.pos_tags_sents(cess_sents, "spanish")
    # pickle.dump(cess_tags, open("delete.pickle", "wb"))

    spa = NLTKPOSTagger(spanish_tagger="spaghetti")
    perc = NLTKPOSTagger(spanish_tagger="perceptron")
    
    print("Spaghetti:")
    precision, recall, f1_macro = test_taggers(spa, cess_sents, cess_tags)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1-Macro:", f1_macro)
    
    print("Perceptron:")
    precision, recall, f1_macro = test_taggers(perc, cess_sents, cess_tags)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1-Macro:", f1_macro)
    

if __name__ == "__main__":
    compare_taggers()

#   Spaghetti:
#   Precision: 0.9256480688385464
#   Recall: 0.9256480688385464
#   F1-Macro: 0.7092727834608811
#   Perceptron:
#   Precision: 0.9276614387965069
#   Recall: 0.9276614387965069
#   F1-Macro: 0.3069507469443802
