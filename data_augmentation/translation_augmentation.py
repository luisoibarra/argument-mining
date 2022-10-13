from pathlib import Path
if __name__ == "__main__":
    import sys
    path = str(Path(__file__, "..", "..").resolve())
    if path not in sys.path:
        print(path)
        sys.path.insert(0, path)

from aligner.aligner import Aligner
from sentence_aligner.sentence_aligner import SentenceAligner
from projector.projector import Projector
from corpus_parser.parser import Parser

class DataAugmentator:

    def augment_data_by_translation(
        self,
        corpus_path: Path, 
        destination_path: Path, 
        parser: Parser, 
        sentence_aligner: SentenceAligner,
        aligner: Aligner,
        projector: Projector, 
        source_language: str = "english", 
        middle_language: str = "spanish",
        **kwargs):
        raise NotImplementedError()

class TranslateDataAugmentator(DataAugmentator):

    def __init__(self) -> None:
        self.BASE_DIR = Path(__file__, "..").resolve()

    def __delete_directory(self, path: Path):
        try:
            [file.unlink() for file in path.iterdir()]
            path.rmdir()
        except FileNotFoundError:
            pass

    def augment_data_by_translation(
        self,
        corpus_path: Path, 
        destination_path: Path, 
        parser: Parser, 
        sentence_aligner: SentenceAligner,
        aligner: Aligner,
        projector: Projector, 
        source_language: str = "english", 
        middle_language: str = "spanish",
        **kwargs):
        """
        Read the corpus and augment it by translating from source_language
        to middle_language and back to source_language, then project the tags
        to the new translated text.

        `corpus_path`: Path that contains the corpus files
        `destination_path`: Path to save the augmented corpus
        `source_language`: Corpus language
        `middle_language`: Middle languaga to use for augmentation
        """

        # Circular dependency if is placed on the top
        from pipelines.corpus_pipelines import full_corpus_processing_pipeline

        standard_corpus_path = self.BASE_DIR / "temp_parsed_to_conll"
        sentence_alignment_dir = self.BASE_DIR / "temp_sentence_aligment"
        bidirectional_alignment_dir = self.BASE_DIR / "temp_bidirectional_alignment"
        projection_dir = self.BASE_DIR / "temp_projection"
        
        try:
            kwargs.pop('target_language') if 'target_language' in kwargs else ""
            full_corpus_processing_pipeline(
                corpus_path, 
                standard_corpus_path, 
                sentence_alignment_dir,
                bidirectional_alignment_dir,
                projection_dir,
                parser,
                sentence_aligner,
                aligner,
                projector,
                source_language=source_language,
                target_language=source_language,
                middle_language=middle_language,
                **kwargs
            )

            destination_path.mkdir(parents=True, exist_ok=True)

            for file in projection_dir.iterdir():
                if file.is_file():
                    dest_file = destination_path / (f"from_{middle_language}_augmented_" + file.name)
                    dest_file.touch(exist_ok=True)
                    dest_file.write_text(file.read_text())
        finally:
            self.__delete_directory(standard_corpus_path)
            self.__delete_directory(sentence_alignment_dir)
            self.__delete_directory(bidirectional_alignment_dir)
            self.__delete_directory(projection_dir)

    