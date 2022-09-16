if __name__ == "__main__":
    import sys
    from pathlib import Path
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        sys.path.insert(0, path)

import argparse
from utils.console_utils import make_command, run_bash_command
from datetime import date
from utils.argparser_utils import ChoiceArg, OptionalArg, PositionalArg, update_parser

choose_spider_params = [
    ChoiceArg(
        name="spiders_to_run",
        help="Choose the spiders to run",
        type=str,
        values=('letter', 'printed', 'all')
    )
]

letter_params = [
    OptionalArg(
        name="initial_page",
        help="Initial page to look at https://www.granma.cu/archivo?page=[INITIAL_PAGE]&q=&s=14",
        default=1,
        type=int
    ),
    OptionalArg(
        name="final_page",
        help="Final page to look at https://www.granma.cu/archivo?page=[FINAL_PAGE]&q=&s=14.\nTo get a good value visit the page and look for the last page number",
        default=144,
        type=int
    )
]

printed_params = [
    OptionalArg(
        name="start_date",
        help="Initial date to fetch the printed version. Must have the format: YYYY-MM-DD. Default: 2020-01-01",
        type=str,
        default="2020-01-01"
    ),
    OptionalArg(
        name="end_date",
        help="Final date to fetch the printed version. Must have the format: YYYY-MM-DD. Default: Current date",
        type=str,
        default=str(date.today())
    ),
]

def handle_from_args(args):
    commands = []
    if args.spiders_to_run in ["letter", "all"]:
        # Run letter spider
        commands.append(make_command(
            'cd',
            'granma',
            '&&',
            'scrapy',
            'crawl',
            'letters_to_direction',
            '-a',
            f'initial_page={args.initial_page}',
            '-a',
            f'max_page={args.final_page}',
        ))
    if args.spiders_to_run in ["printed", "all"]:
        # Run printed spider
        commands.append(make_command(
            'cd',
            'granma',
            '&&',
            'scrapy',
            'crawl',
            'print_edition',
            '-a',
            f'start_date={args.start_date}',
            '-a',
            f'end_date={args.end_date}',
        ))
        
    for command in commands:
        run_bash_command(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    optional_args = letter_params + printed_params
    update_parser(parser, [], choose_spider_params, optional_args)
    
    args = parser.parse_args()
    
    handle_from_args(args)
    