import argparse
from utils.argparser_utils import update_parser
from pipelines.segmenter_pipelines import perform_full_inference_pipeline
from segmenter.main import create_from_args as create_from_args_segmenter
from segmenter.main import choice_args as choice_args_segmenter
from segmenter.main import optional_args as optional_args_segmenter
from segmenter.main import positional_args as positional_args_segmenter
from link_prediction.main import create_from_args as create_from_args_link_prediction
from link_prediction.main import choice_args as choice_args_link_prediction
from link_prediction.main import optional_args as optional_args_link_prediction
from link_prediction.main import positional_args as positional_args_link_prediction


parser = argparse.ArgumentParser()

positional_args = [
    positional_args_segmenter[0],
    positional_args_segmenter[1],
    positional_args_link_prediction[1],
]

choice_args = choice_args_segmenter + choice_args_link_prediction

optional_args = list(set(optional_args_segmenter + optional_args_link_prediction))

if __name__ == "__main__":

    update_parser(
        parser,    
        positional_args,
        choice_args,
        optional_args
    )

    args = parser.parse_args()

    segmenter = create_from_args_segmenter(args)
    link_predictor = create_from_args_link_prediction(args)

    perform_full_inference_pipeline(
        segmenter=segmenter,
        link_predictor=link_predictor,
        source_dir=args.segmenter_source_path,
        segmenter_destination_dir=args.segmenter_export_path,
        destination_dir=args.link_dest_dir,
        source_language=args.source_language,
    )