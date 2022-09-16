from concurrent.futures import Future, ThreadPoolExecutor, wait
import logging
from utils.console_utils import make_command, run_bash_command
from typing import List, Optional

from pathlib import Path

class Aligner:
    """
    Abstract class that makes the bidirectional alignment.
    """
    
    def __init__(self, max_worker: Optional[int] = 20) -> None:
        self.max_worker = max_worker
    
    def bidirectional_align_dir(self, sentence_alignment_dir: Path, align_dest: Path, **kwargs):
        """
        Read the `.align` files in `sentence_alignment_dir` and write in `align_dest` the
        bidirectional alignments. The files have the suffix `.bidirectional`
        
        sentence_alignment_dir: Address of the aligned sentences
        align_dest: Destination directory for the bidirectional alignments
        """
        
        if not align_dest.exists(): align_dest.mkdir(exist_ok=True, parents=True)
        
        sentences_aligned = [x for x in sentence_alignment_dir.iterdir()]

        batch = len(sentences_aligned)//self.max_worker + 1
        
        def batch_work(slice: int) -> str:
            for file in sentences_aligned[batch*slice:batch*(slice+1)]:
                if file.is_file() and file.name.endswith(".align"):
                    dest_file = align_dest / (file.name + ".bidirectional")
                    self.do_bidirectional_align_file(file, dest_file, **kwargs)
        
        futures: List[Future] = []
        with ThreadPoolExecutor(max_workers=self.max_worker) as exe:
            for i in range(self.max_worker):
                futures.append(exe.submit(batch_work, i))
        wait(futures)
        exceptions = [future.exception() for future in futures if future.exception()]
        
        if exceptions:
            raise Exception(exceptions)

    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, **kwargs):
        """
        Get the alignment from the text in `sentence_align_dir`. The alignment will match the line with sentence,
        the format will be a list of `tok_source_index-tok_dest_index` representing
        the token alignment.
        
        sentence_align_dir: File were the sentences in source and target languages. The 
        tokens within sentences must be separated by spaces
        alignment_dest: Destination file to save the word alignment.
        """
        raise NotImplementedError()


class SelfLanguageAligner(Aligner):
    """
    Aligner that only takes into account the source language and performs a self annotation.
    
    Its main purpose is testing.
    """

    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, **kwargs):
        sentence_aligment = sentence_align_dir.read_text().splitlines()
        bidirectional_alignment_text = ""
        for sentence_pair in sentence_aligment:
            source_sentence, target_sentence = sentence_pair.split(Aligner.SEPARATOR)
            bidirectional_alignment_text += " ".join(f"{i}-{i}" for i,tok in enumerate(source_sentence.split(" "))) + "\n"
        alignment_dest.write_text(bidirectional_alignment_text)

class FastAlignAligner(Aligner):
    """
    Aligner using the fast_align algorithm. 
    """
    
    def __init__(self, max_worker: Optional[int] = 20, fast_align_path: Optional[Path] = None) -> None:
        super().__init__(max_worker)
        self.fast_align_path = fast_align_path if fast_align_path else Path(__file__, "..", "fast_align", "build", "fast_align").resolve()
    
    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, atools_opt: bool=True, **kwargs):
        """
        Uses the fast_align algorithm to provide the bidirectional alignment for the
        sentences in `sentence_align_dir`. 
        
        sentence_align_dir: File were the sentences in source and target languages. The 
        tokens within sentences must be separated by spaces
        alignment_dest: Destination file to save the word alignment.
        atools_opt: If the atools optimizations are performed
        """
        # ./fast_align -i {sentence_align_dir} -d -o -v > {alignment_dest}
        fast_align_cmd = f'"{Path(self.fast_align_path).resolve()}"'
        atools_cmd = f'"{Path(self.fast_align_path, "..", "atools").resolve()}"'
        
        alignment_dest = alignment_dest.resolve()
        
        forward_command = make_command( 
            fast_align_cmd, 
            "-i", 
            f'"{str(sentence_align_dir)}"', 
            "-d",
            "-o",
            "-v",
            ">",
            f'"{str(alignment_dest)}"'
        )
        run_bash_command(forward_command)
        
        reverse_alignment_dest = alignment_dest / ".." / (alignment_dest.name + ".reverse.bidirectional")
        reverse_alignment_dest = reverse_alignment_dest.resolve()
        
        backward_command = make_command( 
            fast_align_cmd, 
            "-i", 
            f'"{str(sentence_align_dir)}"', 
            "-d",
            "-o",
            "-v",
            "-r",
            ">",
            f'"{str(reverse_alignment_dest)}"'
        )
        run_bash_command(backward_command)
        

        if atools_opt:
            revised_alignment_dest = alignment_dest / ".." / (alignment_dest.name + ".revised.bidirectional")
            revised_alignment_dest = revised_alignment_dest.resolve()
            improvement_command = make_command(
                atools_cmd, 
                "-i", 
                f'"{str(alignment_dest)}"', 
                "-j",
                f'"{str(reverse_alignment_dest)}"', 
                "-c",
                "grow-diag-final-and",
                ">",
                f'"{str(revised_alignment_dest)}"'
            )
            
            run_bash_command(improvement_command)
            
            copy_command = make_command(
                "mv", 
                f'"{str(revised_alignment_dest)}"',
                f'"{str(alignment_dest)}"', 
            )
            
            run_bash_command(copy_command)
            
        run_bash_command(make_command(
            "rm",
            f'"{str(reverse_alignment_dest)}"'
        ))
            
class AwesomeAlignAligner(Aligner):
    """
    Aligner using awesome-align algorithm.
    """

    SUPPORTED_KEYS = {
        "model_name_or_path",
        "data_file",
        "output_file",
        "extraction",
        "batch_size"
    }
    
    def __init__(self, max_worker: Optional[int] = None, awesome_align_path: Optional[Path] = None) -> None:
        if max_worker is None:
            super().__init__(max_worker=1)
        else:
            super().__init__(max_worker=max_worker)
            if self.max_worker > 5:
                logging.warning(f"High value for max_worker in AwesomeAlignAligner. This could lead to files not been precessed. Recommended values are [1, 2, 3]")

        self.awesome_align_path = awesome_align_path if awesome_align_path else Path(__file__, "..", "awesome-align", "awesome_align").resolve()
    
    def do_bidirectional_align_file(self, sentence_align_dir: Path, alignment_dest: Path, **kwargs):
        kwargs = kwargs.copy()
        
        kwargs.setdefault("model_name_or_path", "bert-base-multilingual-cased")
        kwargs.setdefault("output_file", f'"{str(alignment_dest)}"')
        kwargs.setdefault("data_file", f'"{str(sentence_align_dir)}"')
        kwargs.setdefault("batch_size", 32)
        kwargs.setdefault("extraction", "softmax")
        
        awesome_align_cmd = make_command(
            'python3',
            f'"{self.awesome_align_path / "run_align.py"}"',
            *[f"--{key}={value}" for key,value in kwargs.items() if key in self.SUPPORTED_KEYS]
        )
        run_bash_command(awesome_align_cmd)
        
