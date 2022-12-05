import shutil
from zipfile import ZipFile
from data_augmentation.translation_augmentation import TranslateDataAugmentator
from projector.projector import CrossLingualAnnotationProjector
from aligner.aligner import AwesomeAlignAligner, FastAlignAligner
from sentence_aligner.sentence_aligner import SentenceAligner
from sentence_aligner.translator import GoogleDeepTranslator
from corpus_parser.cdcp_parser import CDCPParser
from corpus_parser.brat_parser import BratParser
from corpus_parser.conll_parser import ConllParser
from corpus_parser.unified_parser import UnifiedParser
from pathlib import Path
from pipelines.corpus_pipelines import full_corpus_processing_pipeline
import streamlit as st

st.title("Projection")

data_path = Path(__file__, "../../../data").resolve()

ex = st.expander("Upload corpus")
to_projection = ex.checkbox("Is in target language.", help="If this box is checked then the submited corpus it is assumed to be in target language and will be direcly copied to the projection corpus folder else will be copied to the initial corpus folder.")
file = ex.file_uploader("Upload corpus", "zip", help="Upload a zip file containing the corpus. The file must contain dev, test and train folders.")
if file is not None:
    must_have = ["dev", "train", "test"]
    zip_file = ZipFile(file)
    errors = False
    for info in zip_file.infolist():
        if info.is_dir():
            name = Path(info.filename).name
            if name in must_have:
                must_have.remove(name)
            else:
                ex.error(f"The zip file must only directories with names dev, train or test. Invalid directory name {name} found.")
                errors = True
    for missing_dir in must_have:
        ex.error(f"The zip file doesn't contain a folder called {missing_dir}.")
        errors = True

    if not errors and ex.button(f"Upload corpus"):
        name = Path(zip_file.filename).stem
        corpus_path = (data_path / "projection" / name) if to_projection else (data_path / "corpus" / name)
        if corpus_path.exists():
            shutil.rmtree(corpus_path)
        corpus_path.mkdir(exist_ok=True, parents=True)
        zip_file.extractall(corpus_path)
        st.info("Corpus uploaded.")
else:
    ex.error(f"File not uploaded.")



# Select corpus
corpus_dir = data_path / "corpus"
options = [path.name for path in corpus_dir.iterdir() if path.is_dir() and path.name[0] != "_"]
corpus_name = st.selectbox("Corpus selection:", options, help="Select the corpus to project. The folder should be at data/corpus and contain dev, test and train folders")

options = ["english"]
source_language = st.selectbox("Corpus language:", options)

options = ["spanish"]
target_language = st.selectbox("Target language:", options)

options = [True, False]
use_spacy = st.selectbox("Use spacy:", options, help="If spacy is used to process the text. NLTK is used by default.")

parser_selection = {
    "infer_parser": lambda: UnifiedParser(),
    "conll": lambda: ConllParser(),
    "conll_bioes": lambda: ConllParser(bioes=True),
    "brat": lambda: BratParser(),
    "cdcp": lambda: CDCPParser()
}
options = list(parser_selection.keys())
parser_selected = st.selectbox("Select parser:", options, help="Parser used to process the corpus")

translator_selection = {
    "google_translator": lambda: GoogleDeepTranslator(),
}
options = list(translator_selection.keys())
translator_selected = st.selectbox("Select translator:", options)

aligner_selection = {
    "awesome_align": lambda: AwesomeAlignAligner(),
    "fast_align": lambda: FastAlignAligner(),
}
options = list(aligner_selection.keys())
aligner_selected = st.selectbox("Select aligner:", options, help="Fast align is fast but not accurate, AwesomeAlign is slow but more accurate.")

projector_selection = {
    "default": lambda: CrossLingualAnnotationProjector(),
}
options = list(projector_selection.keys())
projector_selected = st.selectbox("Select projector:", options)

data_augmentator_selection = {
    "backtranslation": lambda: TranslateDataAugmentator(),
    "None": lambda: None,
}
options = list(data_augmentator_selection.keys())
data_augmentator_selected = st.selectbox("Select data augmentator:", options, help="Data agumentation to perform.")

if st.button("Project corpus"):
    with st.spinner("Projecting corpus ..."):
        corpus_dir = data_path / "corpus" / corpus_name
        standard_corpus_dest_dir = data_path / "parsed_to_conll" / corpus_name
        sentence_alignment_dest_dir = data_path / "sentence_alignment" / corpus_name
        bidirectional_alignment_dest_dir = data_path / "bidirectional_alignment" / corpus_name
        projection_dest_dir = data_path / "projection" / corpus_name
        corpus_parser = parser_selection[parser_selected]()
        sentence_aligner = SentenceAligner(translator_selection[translator_selected]())
        aligner = aligner_selection[aligner_selected]()
        projector = projector_selection[projector_selected]()
        data_augmentator = data_augmentator_selection[data_augmentator_selected]()

        for split in ["dev", "test", "train"]:
            st.text(split)
            final_corpus_dir = corpus_dir / split

            if final_corpus_dir.exists():
                full_corpus_processing_pipeline(
                    corpus_dir=final_corpus_dir,
                    standard_corpus_dest_dir=standard_corpus_dest_dir / split,
                    sentence_alignment_dest_dir=sentence_alignment_dest_dir / split,
                    bidirectional_alignment_dest_dir=bidirectional_alignment_dest_dir / split,
                    projection_dest_dir=projection_dest_dir / split,
                    corpus_parser=corpus_parser,
                    sentence_aligner=sentence_aligner,
                    aligner=aligner,
                    projector=projector,
                    data_augmentator=data_augmentator,
                    source_language=source_language,
                    target_language=target_language,
                    middle_language=target_language,
                    use_spacy=use_spacy
                )
            else:
                st.error(f"Missing folder {split}")
    st.info("Done")