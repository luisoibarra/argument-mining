import logging as log
from typing import Optional
from data_augmentation.translation_augmentation import DataAugmentator, TranslateDataAugmentator
from sentence_aligner.sentence_aligner import SentenceAligner
from projector.projector import Projector
from aligner.aligner import Aligner
from corpus_parser.parser import Parser
from corpus_parser.conll_parser import ConllParser
from pathlib import Path


def parse_corpus_pipeline(corpus_dir: Path, parsed_corpus_dest_dir: Path, corpus_parser: Parser, **kwargs):
    """
    Parse the corpus in `corpus_dir` with `corpus_parser` and convert to standard corpus 
    (.conll with .txt) saving the results in `parsed_corpus_dest_dir`.
    
    corpus_dir: Corpus directory. The files within must be parseable by `corpus_parser`
    parsed_corpus_dest_dir: Destination of the parsed files
    corpus_parser: Parser used to parse the files in `corpus_dir`
    """
    
    log.info(f"Parsing directory {str(corpus_dir)}")
    dataframe_representation = corpus_parser.parse_dir(corpus_dir, **kwargs)

    conll = ConllParser(**kwargs)

    log.info(f"Exporting to {str(parsed_corpus_dest_dir)}")
    conll.export_from_dataframes(parsed_corpus_dest_dir, dataframe_representation)

def make_alignemnts_pipeline(
    standard_corpus_dir: Path, 
    sentence_alignment_dest_dir: Path, 
    bidirectional_alignment_dest_dir: Path, 
    projection_dest_dir: Path,
    sentence_aligner: SentenceAligner,
    aligner: Aligner, 
    projector: Projector, 
    **kwargs):
    """
    Make the sentences alignment with `aligner` saving the results in `sentence_alignment_dest_dir`.
    Make the bidirectional alignment with `aligner` saving the results in `bidirectional_alignment_dest_dir`.
    Make the projections with `projector` saving the results in `projector_dest_dir`
    
    standard_corpus_dir: Address of the corpus in the standard form (.conll with .txt)
    sentence_alignment_dest_dir: Directory to save the sentence alignments
    bidirectional_alignment_dest_dir: Directory to save the bidirectional alignments
    projection_dest_dir: Directory to save the projections
    sentence_aligner: Aligner used to create the source sentence and target sentence alignment
    aligner: Aligner used to create the bidirectional alignments
    projector: Projector used to make the projections
    """
    
    log.info(f"Creating sentence alignment {str(standard_corpus_dir)}")
    sentence_aligner.sentence_alignment_dir(standard_corpus_dir, sentence_alignment_dest_dir, **kwargs)
    
    log.info(f"Creating bidirectional alignment {str(sentence_alignment_dest_dir)}")
    aligner.bidirectional_align_dir(sentence_alignment_dest_dir, bidirectional_alignment_dest_dir, **kwargs)

    log.info(f"Creating projection {str(projection_dest_dir)}")
    projector.project_dir(standard_corpus_dir, sentence_alignment_dest_dir, 
                          bidirectional_alignment_dest_dir, projection_dest_dir, **kwargs)

def full_corpus_processing_pipeline(
    corpus_dir: Path, 
    standard_corpus_dest_dir: Path, 
    sentence_alignment_dest_dir: Path, 
    bidirectional_alignment_dest_dir: Path, 
    projection_dest_dir: Path, 
    corpus_parser: Parser,
    sentence_aligner: SentenceAligner,
    aligner: Aligner, 
    projector: Projector,
    data_augmentator: Optional[DataAugmentator] = None,
    **kwargs):
    
    if data_augmentator:
        if 'middle_language' in kwargs:
            middle_language = kwargs.pop('middle_language')
        else:
            middle_language = kwargs.get('target_language', 'spanish')
            log.warning(f"Data Augmentator was given without a middle_language key arg. Defaulting to {middle_language}")
        data_augmentator.augment_data_by_translation(
            corpus_dir,
            standard_corpus_dest_dir,
            corpus_parser,
            sentence_aligner,
            aligner,
            projector,
            middle_language=middle_language,
            **kwargs
        )

    parse_corpus_pipeline(corpus_dir, standard_corpus_dest_dir, corpus_parser, **kwargs)
    
    make_alignemnts_pipeline(standard_corpus_dest_dir, sentence_alignment_dest_dir, bidirectional_alignment_dest_dir, 
                    projection_dest_dir, sentence_aligner, aligner, projector, **kwargs)