import base64
import zipfile
from corpus_parser.brat_parser import BratParser
from pathlib import Path
from typing import Dict, List
from segmenter.segmenter import ArgumentSegmenter
from link_prediction.link_predictor import LinkPredictor
from pipelines.segmenter_pipelines import perform_full_inference_pipeline, perform_link_prediction_pipeline, perform_segmentation_pipeline
from corpus_parser.conll_parser import ConllParser
import shutil
import io

def process_texts(
    texts: Dict[str, str],
    source_language: str,
    corpus_name: str, 
    segmenter: ArgumentSegmenter = None, 
    link_predictor: LinkPredictor = None, 
    ):
    
    data_path = Path(__file__, "..", "data").resolve()
    
    corpus_path = data_path / corpus_name / "texts"
    segmenter_path = data_path / corpus_name / "segmenter"
    destination_path = data_path / corpus_name / "result"
    
    # Delete existing corpus
    if data_path.exists():
        shutil.rmtree(str(data_path))

    corpus_path.mkdir(parents=True, exist_ok=True)
    
    # Create files
    for key, text in texts.items():
        file_path = corpus_path / key 
        file_path.write_text(text)
    
    if segmenter is not None and link_predictor is not None:
        # Inference
        perform_full_inference_pipeline(
            segmenter=segmenter, 
            link_predictor=link_predictor, 
            source_dir=corpus_path, 
            segmenter_destination_dir=segmenter_path, 
            destination_dir=destination_path,
            source_language=source_language
        )
    
    elif segmenter is not None:
        perform_segmentation_pipeline(
            segmenter=segmenter,
            source_dir=corpus_path,
            destination_dir=segmenter_path,
            language=source_language
        )
        destination_path = segmenter_path
    elif link_predictor is not None:
        perform_link_prediction_pipeline(
            link_predictor=link_predictor,
            source_dir=segmenter_path,
            destination_dir=destination_path,            
            source_language=source_language,
        )

    file_response = ConllParser(bioes=True).parse_dir(destination_path, source_language=source_language)
    text_brat = BratParser().from_dataframes(file_response)
    return file_response, text_brat

def create_zip_str(info: Dict[str, str]) -> bytes:
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as file_zip:
        for key, txt in info.items():
            file_zip.writestr(key, txt)
    zip_buf.seek(0)
    result = zip_buf.read()
    del zip_buf
    return result
