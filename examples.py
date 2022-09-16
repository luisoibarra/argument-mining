from link_prediction.link_predictor import LinkPredictor, RandomLinkPredictor
from segmenter.segmenter import ArgumentSegmenter, RandomArgumentSegmenter
from corpus_parser.unified_parser import UnifiedParser
from sentence_aligner.sentence_aligner import SentenceAligner
from sentence_aligner.translator import GoogleDeepTranslator, SelfTranslator, FromCorpusTranslator
from corpus_parser.conll_parser import ConllParser
from pipelines.corpus_pipelines import full_corpus_processing_pipeline, make_alignemnts_pipeline, parse_corpus_pipeline
from pipelines.segmenter_pipelines import perform_link_prediction_pipeline, perform_segmentation_pipeline, perform_full_inference_pipeline
from projector.projector import PendingSourceAnnotationProjector, SelfLanguageProjector, CrossLingualAnnotationProjector
from aligner.aligner import AwesomeAlignAligner, SelfLanguageAligner, FastAlignAligner

from corpus_parser.brat_parser import BratParser
from pathlib import Path

def corpus_processing_example():
    """
    This example is the one that creates the `data/**/testing/` files, except the ones in `data/corpus/testing`
    """

    base_path = Path("data")
    dataset_name = "testing2"
    # dataset_name = "persuasive_essays_sentence"
    # dataset_name = "testing_sentence"
    # dataset_name = "testing"

    # corpus_parser = BratParser()
    # corpus_parser = ConllParser()
    corpus_parser = UnifiedParser()

    corpus_dir = Path(base_path, "corpus", dataset_name)

    exported_conll_dir = Path(base_path, "parsed_to_conll", dataset_name)
    
    projection_dir = Path(base_path, "projection", dataset_name)
    
    # translator = SelfTranslator()
    # translator = FromCorpusTranslator(
    #     Path(base_path, "translation", dataset_name, "testing_en"),
    #     Path(base_path, "translation", dataset_name, "testing_es"),
    #     "english",
    #     "spanish"
    # )
    translator = GoogleDeepTranslator()

    sentence_aligner = SentenceAligner(translator)

    # aligner = SelfLanguageAligner()
    aligner = FastAlignAligner()
    # aligner = AwesomeAlignAligner()

    sentences_alignment_dir = Path(base_path, "sentence_alignment", dataset_name)
    bidirectional_alignment_dir = Path(base_path, "bidirectional_alignment", dataset_name)

    # projector = SelfLanguageProjector()
    # projector = PendingSourceAnnotationProjector()
    projector = CrossLingualAnnotationProjector()

    # make_alignemnts_pipeline(
    #     exported_conll_dir,
    #     sentences_alignment_dir,
    #     bidirectional_alignment_dir,
    #     projection_dir,
    #     sentence_aligner,
    #     aligner,
    #     projector
    # )
    full_corpus_processing_pipeline(
        corpus_dir, 
        exported_conll_dir, 
        sentences_alignment_dir, 
        bidirectional_alignment_dir, 
        projection_dir, 
        corpus_parser,
        sentence_aligner,
        aligner, 
        projector)

def link_processing_example():
    
    base_path = Path("data")
    dataset_name = "testing"
    # dataset_name = "persuasive_essays_sentence"
    # dataset_name = "testing_sentence"
    # dataset_name = "testing"

    segmenter_dir = Path(base_path, "to_process", dataset_name)

    exported_segmenter_dir = Path(base_path, "segmenter", dataset_name)
    
    link_prediction_dir = Path(base_path, "link_prediction_processed", dataset_name)
    
    
    arg_tags = ["Claim", "MajorClaim", "Premise"]
    segmenter = RandomArgumentSegmenter(arg_tags)
    link_predictor = RandomLinkPredictor(
        arg_tags,
        ["", "support", "attack", "support_Inverse", "attack_Inverse"])
    
    perform_full_inference_pipeline(
        segmenter,
        link_predictor,
        segmenter_dir,
        exported_segmenter_dir,
        link_prediction_dir)

if __name__ == "__main__":
    # corpus_processing_example()
    link_processing_example()
    
    # parse_corpus_pipeline(Path("code", "data", "corpus", "ArgumentAnnotatedEssays-2.0", "train-test-split", "dev"),
    #                       Path("code", "data", "parsed_to_conll", "ArgumentAnnotatedEssays-2.0", "dev"),
    #                       BratParser())
    # parse_corpus_pipeline(Path("code", "data", "corpus", "ArgumentAnnotatedEssays-2.0", "train-test-split", "train"),
    #                       Path("code", "data", "parsed_to_conll", "ArgumentAnnotatedEssays-2.0", "train"),
    #                       BratParser())
    # parse_corpus_pipeline(Path("code", "data", "corpus", "ArgumentAnnotatedEssays-2.0", "train-test-split", "test"),
    #                       Path("code", "data", "parsed_to_conll", "ArgumentAnnotatedEssays-2.0", "test"),
    #                       BratParser())
