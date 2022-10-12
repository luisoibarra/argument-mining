#-*- coding: utf8 -*-

# From https://github.com/alvations/spaghetti-tagger/blob/master/spaghetti.py

from __future__ import print_function
import sys

from pathlib import Path
from typing import List

from nltk import DefaultTagger, UnigramTagger, BigramTagger, NgramTagger
from nltk.corpus import cess_esp as cess

while cess._tagset != 'es-ancora':
    cess._tagset = 'es-ancora'

try:
    import cPickle as pickle
except ImportError:
    import pickle

def load_tagger(filename) -> NgramTagger:
    """ Function to load tagger. """
    with open(filename,'rb') as fin:
        tagger = pickle.load(fin)
    return tagger

def save_tagger(filename, tagger):
    """ Function to save tagger. """
    with open(filename, 'wb') as fout:
        pickle.dump(tagger, fout)

def train_tagger(corpus_name, corpus, test_split):
    """ Function to train tagger. """
    base_path = Path(__file__, "..").resolve()

    # Default tag is NOUN
    defaultTagger = DefaultTagger('NOUN')
    
    # Training UnigramTagger.
    uni_tag = UnigramTagger(corpus, backoff=defaultTagger)
    save_tagger(base_path / '{}_unigram.tagger'.format(corpus_name), uni_tag)
    print(f"UnigramTagger {corpus_name} evaluation", uni_tag.evaluate(test_split))
    
    # Training BigramTagger.
    bi_tag = BigramTagger(corpus, backoff=uni_tag)
    save_tagger(base_path / '{}_bigram.tagger'.format(corpus_name), bi_tag)
    print(f"BigramTagger {corpus_name} evaluation", bi_tag.evaluate(test_split))
    
    _msg = str("Tagger trained with {} using "
            "UnigramTagger and BigramTagger.").format(corpus_name)
    print (_msg, file=sys.stderr)

def unchunk(corpus): 
    """ Function to unchunk corpus. """
    nomwe_corpus = []
    for i in corpus:
        nomwe = " ".join([j[0].replace("_"," ") for j in i])
        nomwe_corpus.append(nomwe.split())
    return nomwe_corpus


class CESSSpaghettiTagger():
    def __init__(self,use_mwe=False):
        self.use_mwe = use_mwe
        # Train tagger if it's used for the first time.
        base_path = Path(__file__, "..").resolve()
        try:
            load_tagger(base_path / 'cess_unigram.tagger').tag(['estoy'])
            load_tagger(base_path / 'cess_bigram.tagger').tag(['estoy'])
        except IOError:
            print ("*** First-time use of cess tagger ***", file=sys.stderr)
            print ("Training tagger ...", file=sys.stderr)
            
            train_test_split = 0.9
            
            # Load CESS corpus.
            cess_sents = cess.tagged_sents(tagset='universal')
            train = int(len(cess_sents) * train_test_split)
            
            # Trains the tagger MWE.
            train_cess_sents, test_cess_sents = cess_sents[:train], cess_sents[train:]
            train_tagger('cess', train_cess_sents, test_cess_sents)
            
            # Trains the tagger with no MWE.
            cess_nomwe = unchunk(cess.tagged_sents(tagset='universal'))
            train = int(len(cess_nomwe) * train_test_split)
            
            train_cess_nomwe, test_cess_nomwe = cess_nomwe[:train], cess_nomwe[train:]
            train_tagged_cess_nomwe = pos_tag_sents(train_cess_nomwe, False)
            test_tagged_cess_nomwe = pos_tag_sents(test_cess_nomwe, False)
            train_tagger('cess_nomwe', train_tagged_cess_nomwe, test_tagged_cess_nomwe)
            
            
        # Load tagger.
        _mwe_option_name = "_nomwe_" if self.use_mwe == True else "_"
        self.uni = load_tagger(base_path / 'cess{}unigram.tagger'.format(_mwe_option_name))
        self.bi = load_tagger(base_path / 'cess{}bigram.tagger'.format(_mwe_option_name))

    def pos_tag(self, tokens: List[str]) -> List[str]:
        return [x[1] for x in self.bi.tag(tokens)]
        
    def pos_tag_sents(self, sentences: List[List[str]]) -> List[str]:
        return [[x[1] for x in sentence] for sentence in self.bi.tag_sents(sentences)]

        
def pos_tag(tokens: List[str], use_mwe=False) -> List[str]:
    tagger = CESSSpaghettiTagger(use_mwe)
    return tagger.bi.tag(tokens)
    
def pos_tag_sents(sentences: List[List[str]], use_mwe=False) -> List[str]:
    tagger = CESSSpaghettiTagger(use_mwe)
    return tagger.bi.tag_sents(sentences)
