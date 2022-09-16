if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

import argparse
from pathlib import Path
from sentence_aligner.translator import FromCorpusTranslator, GoogleDeepTranslator
from sentence_aligner.sentence_aligner import SentenceAligner
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="conll_parsed_path",
        help="Destination path to save the parsed files",
        type=Path
    ),
    PositionalArg(
        name="sentence_alignment_path",
        help="Destination path to save the aligned sentences",
        type=Path
    ),
]

choice_args = [
    ChoiceArg(
        name="translator",
        help="Select the translation process",
        type=str,
        values=("google", "corpus")
    ),
]

optional_args = [
    OptionalArg(
        name="source_language",
        help="Source language",
        type=str,
        default="english"
    ),
    OptionalArg(
        name="target_language",
        help="Target language",
        type=str,
        default="spanish"
    ),
]

def create_from_args(args) -> SentenceAligner:
    translator = {
        "google": GoogleDeepTranslator(),
    }
    translator = translator[args.translator]
    return SentenceAligner(translator)

def handle_from_args(args):
    sentence_aligner = create_from_args(args)
    sentence_aligner.sentence_alignment_dir(
        args.conll_parsed_path,
        args.sentence_alignment_path,
        source_language=args.source_language,
        target_language=args.target_language
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    