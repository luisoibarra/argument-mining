import base64
from utils.console_utils import make_command, run_bash_command
import zipfile
from corpus_parser.brat_parser import BratParser
from pathlib import Path
from typing import Dict, List, Optional
from segmenter.segmenter import ArgumentSegmenter
from link_prediction.link_predictor import LinkPredictor
from pipelines.segmenter_pipelines import perform_full_inference_pipeline, perform_link_prediction_pipeline, perform_segmentation_pipeline
from corpus_parser.conll_parser import ConllParser
from concurrent.futures import Future, ThreadPoolExecutor, wait
import shutil
import io

def process_texts_console(
    corpus_name: str,
    source_language: str, 
    zip_file: zipfile.ZipFile):



    base_path = Path(__file__, "..", "..").resolve()
    data_path = base_path / "streamlit_app" / "data"
    text_path = data_path / corpus_name / "texts"
    segmenter_processed_text_path = data_path / corpus_name / "segmenter"
    processed_text_path = data_path / corpus_name / "result"
    brat_path = data_path / corpus_name / "brat"
    
    for path in [text_path, segmenter_processed_text_path, processed_text_path, brat_path]:
        if path.exists():
            shutil.rmtree(str(path))

    if not text_path.exists():
        text_path.mkdir(parents=True)

    zip_file.extractall(text_path)

    command = make_command(
        "cd",
        str(base_path / 'segmenter'),
        "&&",
        "python3",
        "main.py",
        "--source_language",
        source_language,
        "--corpus_tag",
        corpus_name,
        str(text_path),
        str(segmenter_processed_text_path),
    )
    run_bash_command(command)
    command = make_command(
        "cd",
        str(base_path / 'link_prediction'),
        "&&",
        "python3",
        "main.py",
        "--source_language",
        source_language,
        "--corpus_tag",
        corpus_name,
        str(segmenter_processed_text_path),
        str(processed_text_path)
    )
    run_bash_command(command)

    file_response = ConllParser(bioes=True).parse_dir(processed_text_path, source_language=source_language)
    BratParser().export_from_dataframes(brat_path, file_response)
    return brat_path

def process_texts(
    texts: Dict[str, str],
    source_language: str,
    corpus_name: str, 
    segmenter: ArgumentSegmenter = None, 
    link_predictor: LinkPredictor = None, 
    zip_file: zipfile.ZipFile = None
    ):
    
    data_path = Path(__file__, "..", "data").resolve()
    
    corpus_path = data_path / corpus_name / "texts"
    brat_path = data_path / corpus_name / "brat"
    segmenter_path = data_path / corpus_name / "segmenter"
    destination_path = data_path / corpus_name / "result"
    
    # Delete existing corpus
    if data_path.exists():
        shutil.rmtree(str(data_path))

    corpus_path.mkdir(parents=True, exist_ok=True)

    # Create files
    if zip_file:
        zip_file.extractall(corpus_path)
    elif texts:
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
    BratParser().export_from_dataframes(brat_path, file_response)
    return file_response, text_brat, brat_path

def create_zip_str(info: Dict[str, str]) -> bytes:
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as file_zip:
        for key, txt in info.items():
            file_zip.writestr(key, txt)
    zip_buf.seek(0)
    result = zip_buf.read()
    del zip_buf
    return result

def create_zip(path: Path) -> bytes:
    shutil.make_archive((path / ".." / "brat").resolve(), 'zip', path)
    with open((path / ".." / "brat.zip").resolve()) as file:
        return file.buffer.read()

def start_brat(port: Optional[int] = None):
    brat_path = Path(__file__, "..", "..", "brat").resolve()
    command = make_command(
        "cd",
        str(brat_path),
        "&&",
        "python3",
        "standalone.py"
    )
    if port is not None:
        command += f" {port}"
    
    ex = ThreadPoolExecutor()
    ex.submit(lambda: run_bash_command(command)) 
        

def is_brat_alive(port: int = 8001) -> True:
    import urllib
    try:
        r = urllib.request.urlopen(f"http://localhost:{port}")
        r.read()
        return True
    except:
        return False