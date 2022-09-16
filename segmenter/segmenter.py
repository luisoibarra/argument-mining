from concurrent.futures import Future, ThreadPoolExecutor, wait
from pathlib import Path
from typing import List, Tuple
import random as rand

SplittedArgumentInfo = Tuple[str,str]

class ArgumentSegmenter:
    
    def __init__(self, max_worker: int = 3) -> None:
        self.max_worker = max_worker
    
    def extract_arguments_dir(self, annotation_dir: Path, export_dir: Path):
        annotated_files = [file for file in annotation_dir.iterdir() if file.name.endswith(".txt")]
        
        if not export_dir.exists(): export_dir.mkdir(exist_ok=True, parents=True)
        
        batch = len(annotated_files)//self.max_worker + 1
        
        def batch_work(slice: int) -> str:
            for annotated_file in annotated_files[batch*slice:batch*(slice+1)]:
                self.extract_arguments_from_file(annotated_file, export_dir)
        
        futures: List[Future] = []
        with ThreadPoolExecutor(max_workers=self.max_worker) as exe:
            for i in range(self.max_worker):
                futures.append(exe.submit(batch_work, i))
                # batch_work(i)
        wait(futures)
        exceptions = [future.exception() for future in futures if future.exception()]
        
        if exceptions:
            raise Exception(exceptions)
    
    def extract_arguments_from_file(self, source_file: Path, dest_directory: Path):
        """
        Read a space separated content from `source_file` and create in `dest_directory`
        the .conll and the .txt file of the argumentative split.
        
        source_file: A file tokenized by whitespaces of the text to extract arguments from
        dest_directory: A destination directory for the conll annotated result
        """
        
        content = source_file.read_text()
        argument_info = self.extract_arguments_from_text(content)
        
        conll_dest_file = dest_directory / f"{source_file.name}.conll"
        text_dest_file = dest_directory / f"{source_file.name}.txt"
        
        conll_dest_file.touch(exist_ok=True)
        text_dest_file.touch(exist_ok=True)
        
        with conll_dest_file.open("w") as file1, text_dest_file.open("w") as file2:
            # Write Conll data
            file1.write("\n".join([f"{tok}\t{tag}" for tok, tag in argument_info]))
            # Write text data
            file2.write(" ".join([tok for tok, _ in argument_info]))

    def extract_arguments_from_text(self, text: str) -> List[SplittedArgumentInfo]:
        """
        Split the text by its argumentative units.
        
        text: Text to be splitted
        
        returns: A list of pairs with the component and its tag in the text.
        """
        raise NotImplementedError()

class RandomArgumentSegmenter(ArgumentSegmenter):
    
    def __init__(self, arg_tags: List[str], max_sequence_length: int=10) -> None:
        super().__init__()
        self.max_sequence_length = max_sequence_length
        self.arg_tags = arg_tags
    
    def extract_arguments_from_text(self, text: str) -> List[SplittedArgumentInfo]:
        text = text.split()
        generated_tags = []
        arg_units = []
        
        current = 0
        while current < len(text):
            length = rand.randint(1, self.max_sequence_length)
            final_current = min(current + length, len(text))
            meta_tag = rand.choice(self.arg_tags)
            
            inside = rand.randint(0,1)
            if inside:
                tag = meta_tag
            else:
                tag = None

            generated_tags.append(tag)
            current_arg = ""
            while current < final_current:
                current_arg += text[current] + " "
                current += 1
            arg_units.append(current_arg)

        return [x for x in zip(arg_units, generated_tags)]

