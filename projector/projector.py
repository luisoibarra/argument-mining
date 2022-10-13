from concurrent.futures import Future, ThreadPoolExecutor, wait
from sentence_aligner.sentence_aligner import SentenceAligner
import string
from corpus_parser.conll_parser import ConllParser
from typing import Dict, List, Tuple, Union
import logging as log
from utils.console_utils import make_command, run_bash_command

from pathlib import Path

class Projector:
    """
    Abstract class for projection algorithm
    """
    
    def __init__(self) -> None:
        self.max_worker = 20
    
    def project_dir(self, annotation_dir: Path, sentence_alignment_dir: Path, bidirectional_alignment_dir: Path,
                    export_dir: Path, split_senteneces=True, **kwargs):
        """
        Creates annotated corpus in `export_dir` containing the projected labels from `annotation_dir`files using
        the sentence alignments from `sentence_alignment_dir` and the bidiectional alignment from `bidirectional_alignment_dir`
        
        annotation_dir: Path that contains the .conll files with the annotations
        sentence_alignment_dir: Path that contains the .align files with the sentence alignments
        bidirectional_alignment_dir: Path that contains the .bidirectional files.
        export_dir: Path to export the projected files in `dest_language`.
        
        """
        
        annotated_files = [file for file in annotation_dir.iterdir() if file.name.endswith(".conll")]
        sentences_aligned_files = [file for file in sentence_alignment_dir.iterdir() if file.name.endswith(".align")]
        bidirectional_alignments_files = [file for file in bidirectional_alignment_dir.iterdir() if file.name.endswith(".bidirectional")]
        
        if not export_dir.exists(): export_dir.mkdir(exist_ok=True, parents=True)
        
        parser = ConllParser()
        
        batch = len(annotated_files)//self.max_worker + 1
        
        def batch_work(slice: int) -> str:
            for annotated_file in annotated_files[batch*slice:batch*(slice+1)]:
                try:
                    sentence_aligned_file = [
                        file for file in sentences_aligned_files 
                            if file.name.startswith(annotated_file.name) and file.name.endswith(".align")
                    ][0] # Find the associated .align file
                except IndexError as e:
                    raise IndexError(f"No aligned sentence found for {annotated_file}. Expected like {annotated_file}.align")
                try:
                    bidirectional_alignment_file = [
                        file for file in bidirectional_alignments_files 
                            if file.name.startswith(annotated_file.name) and file.name.endswith(".bidirectional")
                    ][0] # Find the associated .bidirectional file
                except IndexError as e:
                    raise IndexError(f"No bidirectional alignment found for {annotated_file}. Expected like {annotated_file}.bidirectional")
                
                # Reading files. BIO annotations, Sentence alignment, Bidirectional alignment
                annotation_df = parser.parse_file(annotated_file)
                key = str(annotated_file)
                annotation = parser.from_dataframes({key : annotation_df }, get_tags=True, **kwargs)[key][0]
                annotation = [x for x in annotation if x["bio_tag"]]
                sentences_aligned = sentence_aligned_file.read_text().splitlines()
                bidirectional_alignments = bidirectional_alignment_file.read_text().splitlines()
                
                # Checking that the sentence amount is the same
                if len(sentences_aligned) != len(bidirectional_alignments):
                    raise Exception(f"Sentences aligned and bidirectional aligments amount doesn't match for {annotated_file}")
                
                file_target_projection = []
                
                current_annotation_offset = 0
                
                for sentence_aligned, bidirectional_alignment in zip(sentences_aligned, bidirectional_alignments):
                    # Reading and parsing text
                    source_sentence, target_sentence = sentence_aligned.split(kwargs.get("separator", SentenceAligner.SEPARATOR))
                    source_sentence_tokens, target_sentence_tokens = source_sentence.split(" "), target_sentence.split(" ")
                    bidirectional_alignment_dict = self._parse_bidirectional_alignment(bidirectional_alignment)
                    
                    # Updating offset
                    next_annotation_offset = current_annotation_offset + len(source_sentence_tokens)
                    
                    current_annotations = annotation[current_annotation_offset:next_annotation_offset]
                    
                    # Sanity check. 
                    assert len(source_sentence_tokens) == len(current_annotations), "Tokens and tags amounts aren't equal"
                    assert tuple(source_sentence_tokens) == tuple(tag_info["tok"] for tag_info in current_annotations), "Tokens and tags lexeme aren't equal"

                    
                    target_projection = self.project_sentence(source_sentence_tokens, target_sentence_tokens,
                                                            bidirectional_alignment_dict, current_annotations)
                    if split_senteneces:
                        target_projection.append("")
                    file_target_projection.extend(target_projection)
                    
                    current_annotation_offset = next_annotation_offset
                
                if current_annotation_offset != len(annotation):
                    raise Exception(f"Missing annotations to be used in {annotated_file}: {annotation[current_annotation_offset:]}")
                
                target_annotated_file = export_dir / (annotated_file.name + ".projected.conll")
                
                final_projection_text = parser.get_conll_text_from_annotation(file_target_projection)
                
                target_annotated_file.write_text(final_projection_text)
        
        futures: List[Future] = []
        with ThreadPoolExecutor(max_workers=self.max_worker) as exe:
            for i in range(self.max_worker):
                futures.append(exe.submit(batch_work, i))
        wait(futures)
        exceptions = [future.exception() for future in futures if future.exception()]
        
        if exceptions:
            raise Exception(exceptions)

            
    def project_sentence(self, sentence_source_tokens:List[str], sentence_target_tokens:List[str],
                         alignment:Dict[int, List[int]], tags_info: List[Dict[str,Union[str,int]]]) -> List[str]:
        """
        Projects the `sentence_source_tokens`'s annotations annotated in `tags_info` into `sentence_target_tokens`
        using the bidirectional `alignment` information.
        
        sentence_source_tokens: Tokens of the sentence in source language.
        sentence_target_tokens: Tokens of the `sentence_source` translated into the target language 
        alignment: Bidirectional alignment information
        tags_info: sentence_source's annotations
        
        returns: The projected tags in the target language
        """
        raise NotImplementedError()
        
    def _parse_bidirectional_alignment(self, bidirectional_alignment: str) -> Dict[int, List[int]]:
        """
        Parse the single line `bidirectional_alignment` in .bidirectional format
        
        bidirectional_alignment: Sinlge line of a .bidirectional format file. i.e. "1-2 2-1 3-3 4-3"
        
        returns: A dictionary mapping the index to the respective index in the target languages
        """
        alignments = bidirectional_alignment.split(" ")
        
        # Parsing alignments: id1-id2 id3-id4 ...
        alignment_dict: Dict[int, List[int]] = {}
        for align_tuple in alignments:
            source, target = tuple(map(int, align_tuple.split("-")))
            if source not in alignment_dict:
                alignment_dict[source] = []
            alignment_dict[source].append(target)
        
        return alignment_dict
    
class SelfLanguageProjector(Projector):
    """
    Projector that only takes into account the source language and performs a self projection.
    
    Its main purpose is testing.
    """
    
    def project_sentence(self, sentence_source_tokens: List[str], sentence_target_tokens: List[str], 
                         alignment: Dict[int, List[int]], tags_info: List[Dict[str, Union[str, int]]]) -> List[str]:
        assert len(sentence_source_tokens) == len(tags_info), "Tokens and tags amounts aren't equal"
        assert tuple(sentence_source_tokens) == tuple(tag_info["tok"] for tag_info in tags_info), "Tokens and tags lexeme aren't equal"
        return [info["full_tag"] for info in tags_info]
    
class PendingSourceAnnotationProjector(Projector):
    """
    Projector based on the projection algorithm in TODO find the source, it's a project that use pytorch and the algorithm is spread in the code
    """
    
    def project_sentence(self, sentence_source_tokens: List[str], sentence_target_tokens: List[str], 
                         alignment: Dict[int, List[int]], tags_info: List[Dict[str, Union[str, int]]]) -> List[str]:
        
        remove_tags_that_are_punctuation = False
        source_tags_type = []
        source_tags_info = []
        source_tags_ids = []
        words = []
        for i, (word, tag) in enumerate(zip([info["tok"] for info in tags_info], [info["full_tag"] for info in tags_info])):

            if tag.startswith("B") or tag.startswith("S"):
                try:
                    tag_type = tag[tag.find("-")+1:]
                except ValueError:
                    raise ValueError(
                        f"Unable to split tag: {tag_type} from line {i+1}"
                    )

                source_tags_ids.append([len(words)])
                source_tags_type.append(tag_type)
                source_tags_info.append(tags_info[i])
            elif tag.startswith("I"):
                try:
                    tag_type = tag[tag.find("-")+1:]
                except ValueError:
                    raise ValueError(
                        f"Unable to split tag: {tag_type} from line {i+1}"
                    )

                if (
                    source_tags_ids[-1][-1] == (len(words) - 1)
                    and source_tags_type[-1] == tag_type
                ):
                    source_tags_ids[-1].append(len(words))
                else:
                    source_tags_ids.append([len(words)])
                    source_tags_type.append(tag_type)
            elif not tag.startswith("O"):
                log.warning(f"Invalid tag {tag} at position {i} in {' '.join(sentence_source_tokens)}")
            words.append(word)
        
        source_words = words
        
        target_words = sentence_target_tokens
        alignments = alignment
        puncs = set(string.punctuation)
        
        assert len(source_tags_type) == len(source_tags_ids)

        if len(target_words) == 0 or len(source_words) == 0:
            print(
                f"Warning, empty sentence found. source_words: {source_words}. target_words: {target_words}"
            )
            return ["O"] * len(target_words)

        # GET TARGET TAGS IDS

        target_tags_ids: List[List[int]] = []
        target_tags_types: List[str] = []

        for source_tag_ids, source_tag_type in zip(source_tags_ids, source_tags_type):
            target_tag = []
            for tag_id in source_tag_ids:
                try:
                    target_tag.extend(alignments[tag_id])
                except KeyError:
                    continue

            target_tag = sorted(
                list(set(target_tag))
            )  # ENSURE NO DUPLICATED VALUES AND SORT

            if target_tag:
                target_tags_ids.append(target_tag)
                target_tags_types.append(source_tag_type)

        # REMOVE TAGS THAT ARE PUNCTUATION

        if remove_tags_that_are_punctuation:
            for target_tag_idx in range(len(target_tags_ids) - 1, -1, -1):
                target_tags_c = target_tags_ids[target_tag_idx].copy()
                for tag_idx in range(len(target_tags_ids[target_tag_idx]) - 1, -1, -1):
                    try:
                        tword = target_words[target_tags_ids[target_tag_idx][tag_idx]].strip()
                    except IndexError:
                        raise IndexError(
                            f"\ntarget_tags_ids: {target_tags_ids}\n"
                            f"target_tags_c: {target_tags_c}\n"
                            f"target_tags_ids[target_tag_idx]: {target_tags_ids[target_tag_idx]}\n"
                            f"tag_idx: {tag_idx}\n"
                            f"target_tag_idx:{target_tag_idx}\n"
                            f"source_words: {source_words}\n"
                            f"target_words: {target_words}\n"
                        )
                    if all([char in puncs for char in tword]):
                        print(f"Warning: Removing word: {tword} from projected tag. ")
                        del target_tags_ids[target_tag_idx][tag_idx]

                if len(target_tags_ids[target_tag_idx]) == 0:
                    del target_tags_ids[target_tag_idx]
                    del target_tags_types[target_tag_idx]
                    print(f"Warning: Removing tag: {[target_words[i] for i in target_tags_c]}")

        # FIX DISCONTINUOUS SPANS

        for target_tag_no, target_tag_ids in enumerate(target_tags_ids):

            # SPLIT IN GROUPS

            groups: List[List[int]] = [[target_tag_ids[0]]]
            for tag_id in target_tag_ids[1:]:
                if tag_id != groups[-1][-1] + 1:
                    groups.append([tag_id])
                else:
                    groups[-1].append(tag_id)

            # MERGE GROUPS WITH GAP = 1

            i = 0
            while i < len(groups) - 1:
                if groups[i + 1][-1] - groups[i][0] <= 2:

                    groups[i] = (
                        groups[i]
                        + list(range(groups[i][-1] + 1, groups[i + 1][0]))
                        + groups[i + 1]
                    )
                    del groups[i + 1]
                else:
                    i += 1

            # GET LARGEST GROUP

            target_tags_ids[target_tag_no] = max(groups, key=len)

        # FIX COLLISIONS
        # MERGE SAME TYPE TAGS

        i = 0
        while i < len(target_tags_ids) - 1:
            if target_tags_ids[i][-1] >= target_tags_ids[i + 1][0]:

                if target_tags_types[i] == target_tags_types[i + 1]:
                    target_tags_ids[i] = sorted(
                        list(set(target_tags_ids[i] + target_tags_ids[i + 1]))
                    )

                    del target_tags_ids[i + 1]
                    del target_tags_types[i + 1]

                else:
                    i += 1
            else:
                i += 1

        # GET LARGEST TAG IF COLLISION
        i = 0
        while i < len(target_tags_ids) - 1:
            if target_tags_ids[i][-1] >= target_tags_ids[i + 1][0]:
                if len(target_tags_ids[i]) > len(target_tags_ids[i + 1]):
                    del target_tags_types[i + 1]
                    del target_tags_ids[i + 1]
                else:
                    del target_tags_types[i]
                    del target_tags_ids[i]

            else:
                i += 1

        # WRITE TAGS

        target_tags: List[Tuple[str,str]] = [(word, "O") for word in target_words]

        for tag_ids, tag_type in zip(target_tags_ids, target_tags_types):
            try:
                if tag_ids:
                    target_tags[tag_ids[0]] = (target_tags[tag_ids[0]][0], f"B-{tag_type}")
                    for tag_id in tag_ids[1:]:
                        target_tags[tag_id] = (target_tags[tag_id][0], f"I-{tag_type}")
            except IndexError:
                print(f"target_tags: {target_tags}. tag_id:{tag_ids}")
                print(f"Source words: {source_words}")
                print(f"Source tags: {source_tags_ids}")
                print(f"target_words: {target_words}.")
                print(f"alignments: {alignments}")
                print("=================================")
                raise

        return ["\t".join(x) for x in target_tags]

class CrossLingualAnnotationProjector(Projector):
    """
    Projector based on the projection algorithm in https://github.com/UKPLab/coling2018-xling_argument_mining
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.project_argument_algorithm = Path(__file__, "..", "cooling2018-xling_argument_mining", "projectArguments.py").resolve()
    
    def project_dir(self, annotation_dir: Path, sentence_alignment_dir: Path, bidirectional_alignment_dir: Path, export_dir: Path, **kwargs):
        
        annotated_files = [file for file in annotation_dir.iterdir() if file.name.endswith(".conll")]
        sentences_aligned_files = [file for file in sentence_alignment_dir.iterdir() if file.name.endswith(".align")]
        bidirectional_alignments_files = [file for file in bidirectional_alignment_dir.iterdir() if file.name.endswith(".bidirectional")]
        
        if not export_dir.exists(): export_dir.mkdir(exist_ok=True, parents=True)
    
        batch = len(annotated_files)//self.max_worker + 1
        
        def batch_work(slice: int) -> str:
            for annotated_file in annotated_files[batch*slice:batch*(slice+1)]:
                try:
                    sentence_aligned_file = [
                        file for file in sentences_aligned_files 
                            if file.name.startswith(annotated_file.name) and file.name.endswith(".align")
                    ][0] # Find the associated .align file
                except IndexError as e:
                    raise IndexError(f"No aligned sentence found for {annotated_file}. Expected like {annotated_file}.align")
                try:
                    bidirectional_alignment_file = [
                        file for file in bidirectional_alignments_files 
                            if file.name.startswith(annotated_file.name) and file.name.endswith(".bidirectional")
                    ][0] # Find the associated .bidirectional file
                except IndexError as e:
                    raise IndexError(f"No bidirectional alignment found for {annotated_file}. Expected like {annotated_file}.bidirectional")
                
                project_cmd = make_command(
                    'python3',
                    f'"{self.project_argument_algorithm}"',
                    f'"{annotated_file.resolve()}"',
                    f'"{sentence_aligned_file.resolve()}"',
                    f'"{bidirectional_alignment_file.resolve()}"',
                    f'"{(export_dir / (annotated_file.name + ".projected.conll")).resolve()}"'
                )
                run_bash_command(project_cmd)
        
        futures: List[Future] = []
        with ThreadPoolExecutor(max_workers=self.max_worker) as exe:
            for i in range(self.max_worker):
                futures.append(exe.submit(batch_work, i))
        wait(futures)
        exceptions = [future.exception() for future in futures if future.exception()]
        
        if exceptions:
            raise Exception(exceptions)