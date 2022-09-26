from link_prediction.link_predictor import LinkPredictor
from pathlib import Path
from segmenter.segmenter import ArgumentSegmenter


def perform_segmentation_pipeline(
    segmenter: ArgumentSegmenter, 
    source_dir: Path,
    destination_dir: Path,
    language: str = "spanish"):
    """
    Apply the `segmenter` to the files in `source_dir` saving the resutls
    in `destination_dir`
    
    segmenter: Segmenter to apply
    source_dir: Directory that stores the files to apply the segmenter
    destination_dir: Directory to save the processed files
    """
    
    segmenter.extract_arguments_dir(source_dir, destination_dir, language=language)
    
def perform_link_prediction_pipeline(
    link_predictor: LinkPredictor,
    source_dir: Path,
    destination_dir: Path,
    source_language: str = 'spanish'):
    """
    Apply the `link_predictor` to the files in `source_dir` saving the resutls
    in `destination_dir`
    
    link_predictor: Link Predictor to apply
    source_dir: Directory that stores the files to apply the link predictor
    destination_dir: Directory to save the processed files
    """
    
    link_predictor.predict_link_dir(source_dir, destination_dir, source_language=source_language)
    
def perform_full_inference_pipeline(
    segmenter: ArgumentSegmenter,
    link_predictor: LinkPredictor,
    source_dir: Path,
    segmenter_destination_dir: Path,
    destination_dir: Path,
    source_language: str = 'spanish'):
    """
    Apply the `segmenter` and `link_predictor` to the files in `source_dir` saving the resutls
    in `destination_dir`
    
    segmenter: Segmenter to apply
    link_predictor: Link Predictor to apply
    source_dir: Directory that stores the files to apply the procedure
    segmenter_destination_dir: Directory to save the files processed by the segmenter
    destination_dir: Directory to save the processed files
    """
    
    perform_segmentation_pipeline(segmenter, source_dir, segmenter_destination_dir)
    perform_link_prediction_pipeline(link_predictor, segmenter_destination_dir, destination_dir, source_language=source_language)
    
    