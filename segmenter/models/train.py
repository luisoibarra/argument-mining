if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..", "..").resolve())
    if path not in sys.path:
        sys.path.insert(0, path)

from pathlib import Path
from utils.notebook_utils import export_notebook_as_module
NOTEBOOK_PATH = Path(__file__, "..", "segmenter.ipynb").resolve()
try:
    import segmenter.models.segmenter as segmenter_model
except ImportError:
    export_notebook_as_module(NOTEBOOK_PATH)
    import segmenter.models.segmenter as segmenter_model

import argparse
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="corpus_tag",
        help="Corpus tag. Example: cdcp",
        type=str
    ),
    PositionalArg(
        name="language",
        help="Corpus language. Example: spanish",
        type=str
    ),
]

choice_args = [
    # ChoiceArg(
    #     name="aligner",
    #     help="Select the alignment algorithm to use",
    #     type=str,
    #     values=("awesome_align", "fast_align")
    # ),
    ChoiceArg(
        name="create_corpus",
        help="If the corpus must be created",
        type=str,
        values=("no", "yes")
    ),
]

optional_args = [
    OptionalArg(
        name=key,
        help=f"Default: {value}",
        type=type(value) if type(value) != bool else lambda x: True if x.lower() == "true" else False,
        default=value
    ) for key, value in segmenter_model.params.items() if "path" not in key
]

def handle_from_args(args: argparse.Namespace):
    arg_dict = vars(args)
    train(**arg_dict)

def train(**kwargs):
    """
    required tags.

    corpus_tag: Tag that identifies the corpus
    language: Language of the corpus

    optional tags.
    Many tags more. See optional_args
    """
    corpus_tag = kwargs['corpus_tag']
    language = kwargs['language']
    export_notebook_as_module(NOTEBOOK_PATH, 
        new_params={
            arg.name: (f'"{kwargs[arg.name]}"' if isinstance(kwargs[arg.name], str) else kwargs[arg.name]) for arg in optional_args if arg.name in kwargs
        },
        new_cap_variables={
            "INFO_TAG": f'"{corpus_tag}"',
            "LANGUAGE": f'"{language}"'
        })
    import importlib
    importlib.reload(segmenter_model)
    create_corpus = kwargs['create_corpus'] == "yes" if "create_corpus" in kwargs else False
    segmenter_model.train_pipeline(segmenter_model.params, create_corpus)
    segmenter_model.params.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
