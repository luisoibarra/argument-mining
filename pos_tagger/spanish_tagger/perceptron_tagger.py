from pathlib import Path
from typing import List
from nltk.tag.perceptron import PerceptronTagger
from nltk.corpus import cess_esp as cess

while cess._tagset != 'es-ancora':
    cess._tagset = 'es-ancora'

_PICKLE = str(Path(__file__, "..", "cess_averaged_perceptron.pickle").resolve())

def _unchunck(sentences):
    final_sentences = []
    
    for sentence in sentences:
        final_tokens = []
        for tok,label in sentence:
            tokens = tok.split("_")
            final_tokens.extend((tok, label) for tok in tokens)
        final_sentences.append(final_tokens)
    
    return final_sentences

def _train_model():
    tagger = PerceptronTagger()
    train_test_split = 0.9
            
    # Load CESS corpus.
    cess_sents = cess.tagged_sents(tagset='universal')
    train = int(len(cess_sents) * train_test_split)
    
    train_cess_sents, test_cess_sents = cess_sents[:train], cess_sents[train:]
    
    print("Training Perceptron Tagger...")
    tagger.train(train_cess_sents, save_loc=_PICKLE)
    
    test_cess_sents = _unchunck(test_cess_sents)
    print("Accuracy: ", tagger.evaluate(test_cess_sents))
    
    return tagger

def _get_pretrain_model():
    tagger = PerceptronTagger(False)
    tagger.load(_PICKLE)
    return tagger

class CESSPerceptronTagger:
    
    def __init__(self) -> None:
        try:
            self.tagger = _get_pretrain_model()
        except:
            self.tagger = _train_model()
        
    def pos_tag(self, tokens: List[str]) -> List[str]:
        return [x[1] for x in self.tagger.tag(tokens)]
    
    def pos_tag_sents(self, sentences: List[List[str]]) -> List[List[str]]:
        return [self.pos_tag(sentence) for sentence in sentences]
                

if __name__ == "__main__":
    _train_model()
    _get_pretrain_model()