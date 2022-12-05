if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        sys.path.insert(0, path)

import argparse
from link_prediction.tf_link_predictor import TensorflowLinkPredictor
from pathlib import Path
from link_prediction.link_predictor import  LinkPredictor
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="link_source_dir",
        help="Directory with the conll files to process",
        type=Path
    ),
    PositionalArg(
        name="link_dest_dir",
        help="Directory to save the precessed files",
        type=Path
    ),
]

choice_args = [
    ChoiceArg(
        name="link_predictor",
        help="Select the projection algorithm to use",
        type=str,
        values=("tensorflow",)
    ),
]

optional_args = [
    OptionalArg(
        name="corpus_tag",
        help="Tag representing the corpus used for creating the model",
        type=str,
        default="cdcp"
    ),
    OptionalArg(
        name="source_language",
        help="Source language of the text to process",
        type=str,
        default="spanish"
    ),
]

def create_from_args(args) -> LinkPredictor:
    link_predictor = {
        "tensorflow": TensorflowLinkPredictor(args.corpus_tag, args.source_language),
    }[args.link_predictor]
    return link_predictor

def handle_from_args(args):
    link_predictor = create_from_args(args)
    link_predictor.predict_link_dir(args.link_source_dir, args.link_dest_dir, source_language=args.source_language)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    