import argparse
from typing import List, Tuple, NamedTuple

class PositionalArg(NamedTuple):
    name: str
    help: str
    type: type
class ChoiceArg(NamedTuple):
    name: str
    help: str
    type: type
    values: Tuple[str]
class OptionalArg(NamedTuple):
    name: str
    help: str
    type: type
    default: str

def update_parser(
    parser: argparse.ArgumentParser,
    positional_arguments: List[PositionalArg],
    choice_arguments: List[ChoiceArg],
    optional_arguments: List[OptionalArg]):
    """
    Adds to `parser` the given arguments.
    
    parser: Parser to update
    positional_arguments: Positional arguments to add
    choice_arguments: Choice arguments to add. Defaults to the first element in values.
    optional_arguments: Optional arguments to add
    """

    for positional in positional_arguments:
        parser.add_argument(positional.name, help=positional.help, type=positional.type)
    
    for choice in choice_arguments:
        name = choice.name if choice.name.startswith("--") else "--" + choice.name
        parser.add_argument(name, 
                            help=choice.help, 
                            type=choice.type, 
                            choices=choice.values, 
                            default=choice.values[0])

    for optional in optional_arguments:
        name = optional.name if optional.name.startswith("--") else "--" + optional.name
        parser.add_argument(name, 
                            help=optional.help, 
                            type=optional.type, 
                            default=optional.default)
