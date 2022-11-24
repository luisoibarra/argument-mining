if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..", "..").resolve())
    if path not in sys.path:
        sys.path.insert(0, path)
    NOTEBOOK_PATH = Path(__file__, "..", "link_prediction.ipynb").resolve()
    from utils.notebook_utils import export_notebook_as_module
    export_notebook_as_module(NOTEBOOK_PATH)


import argparse
from pathlib import Path
import link_prediction.models.link_prediction as link_prediction_model
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

positional_args = [
    PositionalArg(
        name="corpus_tag",
        help="Corpus tag. Example: persuasive_essays_paragraph",
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
]

optional_args = [
    OptionalArg(
        name=key,
        help=f"Default: {value}",
        type=type(value),
        default=value
    ) for key, value in link_prediction_model.params.items() if "path" not in key
]

def handle_from_args(args: argparse.Namespace):
    arg_dict = vars(args)
    export_notebook_as_module(NOTEBOOK_PATH, 
        new_params={
            arg.name: (f'"{arg_dict[arg.name]}"' if isinstance(arg_dict[arg.name], str) else arg_dict[arg.name]) for arg in optional_args
        },
        new_cap_variables={
            "INFO_TAG": f'"{args.corpus_tag}"',
            "LANGUAGE": f'"{args.language}"'
        })
    import importlib
    importlib.reload(link_prediction_model)
    link_prediction_model.train_pipeline(link_prediction_model.params)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    update_parser(parser, positional_args, choice_args, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
