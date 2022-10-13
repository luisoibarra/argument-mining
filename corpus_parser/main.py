if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

import argparse
from corpus_parser.parser import Parser
from corpus_parser.conll_parser import ConllParser
from corpus_parser.brat_parser import BratParser
from corpus_parser.unified_parser import UnifiedParser
from pathlib import Path
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="source_path",
        help="Path that contains the files to be parsed",
        type=Path
    ),
    PositionalArg(
        name="conll_parsed_path",
        help="Destination path to save the conll parsed files",
        type=Path
    ),
]

choice_args = [
    ChoiceArg(
        name="parser",
        help="Select the type of parser to use",
        type=str,
        values=("unified", "brat", "conll")
    ),
    ChoiceArg(
        name="use_spacy",
        help="If spacy is used to perform word and sentence segmentation.",
        type=str,
        values=("True", "False")
    )
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

def create_from_args(args) -> Parser:
    
    args.use_spacy = True if args.use_spacy.lower() == "true" else False
    
    # Get values
    parser = {
        "unified": UnifiedParser(use_spacy=args.use_spacy),
        "brat": BratParser(),
        "conll": ConllParser(use_spacy=args.use_spacy),
    }[args.parser]
    
    return parser

def handle_from_args(args):
    parser = create_from_args(args)
    df = parser.parse_dir(args.source_path, 
                     source_language=args.source_language, 
                     target_language=args.target_language)

    conll = ConllParser(use_spacy=args.use_spacy) 

    conll.export_from_dataframes(args.conll_parsed_path, 
                                 df, 
                                 source_language=args.source_language, 
                                 target_language=args.target_language)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    