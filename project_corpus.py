import argparse
from utils.argparser_utils import update_parser
from pipelines.corpus_pipelines import full_corpus_processing_pipeline
from aligner.main import create_from_args as create_from_args_aligner
from aligner.main import choice_args as choice_args_alginer
from aligner.main import optional_args as optional_args_alginer
from aligner.main import positional_args as positional_args_alginer
from corpus_parser.main import create_from_args as create_from_args_corpus_parser
from corpus_parser.main import choice_args as choice_args_corpus_parser
from corpus_parser.main import optional_args as optional_args_corpus_parser
from corpus_parser.main import positional_args as positional_args_corpus_parser
from projector.main import create_from_args as create_from_args_projector
from projector.main import choice_args as choice_args_projector
from projector.main import optional_args as optional_args_projector
from projector.main import positional_args as positional_args_projector
from sentence_aligner.main import create_from_args as create_from_args_sentence_aligner
from sentence_aligner.main import choice_args as choice_args_sentence_aligner
from sentence_aligner.main import optional_args as optional_args_sentence_aligner
from sentence_aligner.main import positional_args as positional_args_sentence_aligner

from pathlib import Path

parser = argparse.ArgumentParser()

positional_args = [
    positional_args_corpus_parser[0],
    positional_args_corpus_parser[1],
    positional_args_sentence_aligner[1],
    positional_args_alginer[1],
    positional_args_projector[3]
]

choice_args = choice_args_corpus_parser + choice_args_sentence_aligner + choice_args_alginer + choice_args_projector

optional_args = list(set(optional_args_corpus_parser + optional_args_sentence_aligner + optional_args_alginer + optional_args_projector))

if __name__ == "__main__":

    update_parser(
        parser,    
        positional_args,
        choice_args,
        optional_args
    )

    args = parser.parse_args()

    parser = create_from_args_corpus_parser(args)
    sentence_aligner = create_from_args_sentence_aligner(args)
    aligner = create_from_args_aligner(args)
    projector = create_from_args_projector(args)

    full_corpus_processing_pipeline(
        args.source_path,
        args.conll_parsed_path,
        args.sentence_alignment_path,
        args.bidirectional_path,
        args.projection_path,
        parser,
        sentence_aligner,
        aligner,
        projector,
        source_language = args.source_language,
        target_language = args.target_language,
    )