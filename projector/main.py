if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

import argparse
from pathlib import Path
from projector.projector import CrossLingualAnnotationProjector, Projector
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="conll_parsed_path",
        help="Destination path to save the conll parsed files",
        type=Path
    ),
    PositionalArg(
        name="sentence_alignment_path",
        help="Destination path to save the aligned sentences",
        type=Path
    ),
    PositionalArg(
        name="bidirectional_path",
        help="Destination path to save the sentence's bidirectional alignments",
        type=Path
    ),
    PositionalArg(
        name="projection_path",
        help="Destination path to save the projected sentences",
        type=Path
    ),
]

choice_args = [
    ChoiceArg(
        name="projector",
        help="Select the projection algorithm to use",
        type=str,
        values=("cross",)
    ),
]

optional_args = [

]

def create_from_args(args) -> Projector:
    projector = {
        "cross": CrossLingualAnnotationProjector(),
    }[args.projector]
    return projector

def handle_from_args(args):
    
    projector = create_from_args(args)
    projector.project_dir(
        args.conll_parsed_path,
        args.sentence_alignment_path,
        args.bidirectional_path,
        args.projection_path,
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    