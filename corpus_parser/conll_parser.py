from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from .parser import AnnotatedRawTextInfo, ArgumentationInfo, Parser
import re
import logging as log
from nltk.tokenize import word_tokenize, sent_tokenize

ConllTagInfo = Dict[str, Union[str,int]]

class ConllParser(Parser):
    
    ANNOTATION_REGEX = r"^(?P<tok>[^\s]+)\s(?P<bio_tag>[{TAGS}])(-(?P<prop_type>\w+))?(-(?P<relation_type>\w+))?(-(?P<relation_distance>-?\d+))?\s*$"
    TAG_FORMAT = "{bio_tag}-{prop_type}-{relation_type}-{relation_distance}"
    ANNOTATION_FORMAT = f"{{tok}}\t{TAG_FORMAT}\n"
    
    def __init__(self, *additional_supported_formats, bioes=False, **kwargs) -> None:
        super().__init__((".conll", *additional_supported_formats), ".conll")
        tags = "BIO" if not bioes else "BIOES"
        self.bioes = bioes
        self.ANNOTATION_REGEX = self.ANNOTATION_REGEX.format_map({"TAGS": tags})
        self.annotation_regex = re.compile(self.ANNOTATION_REGEX)
        self.__sent_separator = {"tok":"\n", "bio_tag":""}
    
    def __split_sentences(self, line_infos: list, language: str) -> list:
        """
        Create a new list and adds a sentence separator to the `line_infos`'s content
        the separator is the dtctionary `{"tok":"", "bio_tag":""}`
        
        line_infos: Original information list
        language: Language content
        
        returns: A new list containing a sentence separator 
        """
        new_line_infos = []
        previous_splitted = [i for i, tok in enumerate(line_infos) if tok["bio_tag"] == ""]
        if len(previous_splitted) == 0 or line_infos[-1] != self.__sent_separator:
             previous_splitted.append(len(line_infos))
        index = 0
        
        for end in previous_splitted:
            content = " ".join(tok["tok"] for tok in line_infos[index:end])
            for sentence in sent_tokenize(content, language=language):
                for word in sentence.split(" "):
                    assert word == line_infos[index]["tok"]
                    new_line_infos.append(line_infos[index])
                    index += 1
                # Sentence separator
                new_line_infos.append(self.__sent_separator)
            assert index == end
            index += 1
        return new_line_infos
        
    def parse(self, content:str, file: Optional[Path] = None, get_tags=False, **kwargs) -> ArgumentationInfo:
        """
        Parse `content` returning DataFrames containing
        the argumentative unit and the relation information.
        
        content: text containing the content to parse
        file: Optional, content's original file
        get_tags: If a List of tags info is returned instead a dataframe representation
        
        argumentative_units columns: 
          - `prop_id` Proposition ID inside the document
          - `prop_type` Proposition type
          - `prop_init` When the proposition starts in the original text
          - `prop_end` When the proposition ends in the original text
          - `prop_text` Proposition text
          
        relations columns:
          - `relation_id` Relation ID inside the document
          - `relation_type` Relation type
          - `prop_id_source` Relation's source proposition id 
          - `prop_id_target` Relation's target proposition id
          
        non_argumentative_units columns:
          - `prop_init` When the proposition starts in the original text
          - `prop_end` When the proposition ends in the original text
          - `prop_text` Proposition text
          
        return: (argumentative_units, relationsm non_argumentative_units)
        """
        
        content = content.splitlines()
        
        line_parse = []
        
        for i,line in enumerate(content):
            match = self.annotation_regex.match(line)
            if match:
                line_parse.append(match.groupdict())
            elif line == "":
                line_parse.append(self.__sent_separator)
            else:
                if file:
                    log.warning(f"Line {i} file {file.name}. Match not found: {line}")
                else:
                    log.warning(f"Line {i}. Match not found: {line}")

        if get_tags:
            return line_parse

        def extract_proposition(propositions: List[dict], start_index=0):
            """
            Extracts the first proposition in `propositions`.
            
            Raise: IndexOutOfRange if no proposition is found
            """
            current = start_index
            
            def extract_language_tag(word):
                """
                Check if the word is annotated with a language tag i.e. [_es, _en, _de]
                and return the unannotated word.
                """
                if len(word) > 3 and word[-3] == "_":
                    return word[:-3]
                return word

            if propositions[current]["bio_tag"] == "": # Sentence separator
                proposition_text = extract_language_tag(propositions[current]["tok"])
                current += 1
            elif propositions[current]["bio_tag"] == "O":
                proposition_text = extract_language_tag(propositions[current]["tok"])
                current += 1

                # Join all tokens
                while current < len(propositions) and propositions[current]["bio_tag"] == "O":
                    proposition_text += " " + extract_language_tag(propositions[current]["tok"])
                    current += 1
            else:
                if self.bioes and propositions[current]["bio_tag"] == "S":
                    proposition_text = extract_language_tag(propositions[current]["tok"])
                    current += 1
                    return proposition_text, current
                
                if propositions[current]["bio_tag"] != "B":
                    proposition = propositions[current]
                    if file:
                        log.warning(f"File {file.name}. Proposition '{proposition['tok']}' at index {current} doesn't start with a B")
                    else:
                        log.warning(f"Proposition '{proposition['tok']}' at index {current} doesn't start with a B")
                
                # Current should be B
                proposition_text = extract_language_tag(propositions[current]["tok"])
                current += 1
                
                # Join all tokens
                while current < len(propositions) and propositions[current]["bio_tag"] == "I":
                    proposition_text += " " + extract_language_tag(propositions[current]["tok"])
                    current += 1
                    
                if self.bioes:
                    if current >= len(propositions) or propositions[current]["bio_tag"] != "E":
                        if file:
                            log.warning(f"File {file.name}. Proposition '{proposition['tok']}' at index {current} doesn't end with an E")
                        else:
                            log.warning(f"Proposition '{proposition['tok']}' at index {current} doesn't end with an E")
                    elif current < len(propositions):
                        proposition_text += " " + extract_language_tag(propositions[current]["tok"])
                        current += 1
                        
            return proposition_text, current
        
        argumentative_units = {
            "prop_id": [], 
            "prop_type": [], 
            "prop_init": [], 
            "prop_end": [], 
            "prop_text": [],
        }
        
        non_argumentative_units = {
            "prop_init": [], 
            "prop_end": [], 
            "prop_text": [],
        }
        
        relations = {
            "relation_id": [], 
            "relation_type": [], 
            "prop_id_source": [], 
            "prop_id_target": [],            
        }

        current = 0
        accumulative_offset = 0
        while current < len(line_parse):
            
            proposition, current = extract_proposition(line_parse, current)
            prop_info = line_parse[current-1] # All annotations of the argument are equal 
            prop_id = len(argumentative_units['prop_id']) + 1 # 0 is the root node
            
            if prop_info["bio_tag"] in ["O", ""]:
                non_argumentative_units['prop_init'].append(accumulative_offset)
                non_argumentative_units['prop_end'].append(accumulative_offset + len(proposition))
                non_argumentative_units['prop_text'].append(proposition)
            else:
                argumentative_units['prop_id'].append(prop_id)
                argumentative_units['prop_type'].append(prop_info["prop_type"])
                argumentative_units['prop_init'].append(accumulative_offset)
                argumentative_units['prop_end'].append(accumulative_offset + len(proposition))
                argumentative_units['prop_text'].append(proposition)

                if None not in [prop_info["relation_type"], prop_info["relation_distance"]]:
                    relations['relation_id'].append(len(relations['relation_id']))
                    relations['relation_type'].append(prop_info["relation_type"])
                    relations['prop_id_source'].append(prop_id)
                    relations['prop_id_target'].append(prop_id + int(prop_info["relation_distance"]))
            
            accumulative_offset += len(proposition)
            if prop_info["bio_tag"] != "":
                accumulative_offset += 1 # Extra separator when rebuilding text
        
        return pd.DataFrame(argumentative_units), pd.DataFrame(relations), pd.DataFrame(non_argumentative_units)
        
    def fix_annotations(self, annotations: List[ConllTagInfo]) -> List[ConllTagInfo]:
        """
        Fix posible errors found in `annotations` returning a new list without them.
        
        annotations: Original list of conll annotations
        """
        fixed_annotations = []
        for i, annotation in enumerate(annotations):
            # The next annotation can go after the previous annotation
            # But a sentence separator is in the middle
            if annotation == self.__sent_separator \
               and i < len(annotations) - 1 \
               and i > 0 \
               and annotations[i+1]["bio_tag"] == "I" \
               and annotations[i-1]["bio_tag"] in ["B", "I"] \
               and annotations[i-1]["prop_type"] == annotations[i+1]["prop_type"] \
               and annotations[i-1]["relation_type"] == annotations[i+1]["relation_type"] \
               and annotations[i-1]["relation_distance"] == annotations[i+1]["relation_distance"]:
                # Skip sentence separator
                continue
            fixed_annotations.append(annotation)
        return fixed_annotations

    def from_dataframes(self, dataframes: Dict[str, ArgumentationInfo], source_language="english", get_tags=False, exact_text=True, split_sentences=True, **kwargs) -> Dict[str, Union[AnnotatedRawTextInfo, Tuple[List[ConllTagInfo], str]]]:
        """
        Creates a CONLL annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        source_language: Language for tokenization process
        get_tags: If true, returns the tags instead of the annotated text
        exact_text: If true, returns the exact text representation else will 
        be returned the tokens separated by whitespaces
        
        returns: CONLL annotated string or CONLL annotations, Raw text
        """
        
        results = {}
        default_gap = " "
                
        for file_path_str, (argumentative_units, relations, non_argumentative_units) in dataframes.items():

            tags_info = []
            all_units = pd.concat([argumentative_units, non_argumentative_units], sort=True)
            all_units.sort_values(by="prop_init", inplace=True)
            all_units = all_units.reindex(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
            max_length = all_units["prop_end"].max()
            
            text = default_gap*max_length if exact_text else ""
            
            for index, (prop_id, prop_type, prop_init, prop_end, prop_text) in all_units.iterrows():
                prop_tokens = word_tokenize(prop_text, language=source_language)
                
                if exact_text:
                    text = text[:prop_init] + prop_text + text[prop_end:]
                else:
                    text += default_gap.join(prop_tokens) + default_gap
                
                if pd.notna(prop_type):
                    # It's the begining of a proposition
                    for i,tok in enumerate(prop_tokens):
                        
                        if i == 0:
                            if len(prop_tokens) == 1 and self.bioes:
                                bio_tag = "S"
                            else:    
                                bio_tag = "B"  
                        elif i == len(prop_tokens) - 1 and self.bioes:
                            bio_tag = "E"
                        else:
                            bio_tag = "I"
                        relation = relations[relations["prop_id_source"] == prop_id]
                        if len(relation) == 1:
                            relation_type = relation["relation_type"].values[0]
                            relation_distance = relation["prop_id_target"].values[0] - relation["prop_id_source"].values[0]
                        elif len(relation) == 0:
                            relation_type = "none"
                            relation_distance = "none"
                        else:
                            relation_type = "none"
                            relation_distance = - relation["prop_id_source"].values[0]
                            log.warning(f"File {file_path_str}. Relation '{prop_text}'' with more than one out edge")
                        
                        tags_info.append({
                                "tok": tok,
                                "bio_tag": bio_tag,
                                "prop_type": prop_type,
                                "relation_type": relation_type,
                                "relation_distance": relation_distance
                        })
                        tags_info[-1]["full_tag"] = self.TAG_FORMAT.format_map(tags_info[-1]).replace("-none", "")

                else:
                    if all(x == "\n" for x in prop_text): # Sentence and Paragraph separators
                        for x in prop_text:
                            tags_info.append(self.__sent_separator)
                    else:
                        # Out of proposition
                        for tok in prop_tokens:
                            # Fill the gap with O until the proposition is found
                            tags_info.append({
                                "tok": tok,
                                "bio_tag": "O",
                                "prop_type": "none",
                                "relation_type": "none",
                                "relation_distance": "none"
                            })
                            tags_info[-1]["full_tag"] = "O"
                
            if split_sentences:
                tags_info = self.__split_sentences(tags_info, source_language)
            
            tags_info = self.fix_annotations(tags_info)
            
            if get_tags:
                results[file_path_str] = tags_info, text
            else:
                result = self.get_conll_text_from_annotation_dicts(tags_info)
                results[file_path_str] = result, text
        
        return results

    def get_conll_text_from_annotation(self, annotations: List[str]) -> str:
        """
        Maps the anotation to its associated conll text representation.
        
        annotations: List containig the dictionary that holds the information about the tag
        
        returns: The annotated conll text representation
        """
        text = ""
        for annotation in annotations:
            if annotation == "":
                to_write = "\n"
            else:
                match = self.annotation_regex.match(annotation)
                assert match
                annotation = match.groupdict()
                to_write = self.ANNOTATION_FORMAT.format_map(annotation)
                to_write = to_write.replace("-none", "") # Remove unnecesary labels
                to_write = to_write.replace("-None", "") # Remove unnecesary labels
            text += to_write
        return text

    def get_text_from_annotation(self, annotations: List[ConllTagInfo]) -> str:
        """
        Returns the text associated with `annotations`. All tokens are placed in
        a single line separated by a whitespace. 
        
        annotations: List containig the dictionary that holds the information about the tag
        
        returns: The text representation
        """
        return " ".join([x["tok"] for x in annotations])
    
    def get_conll_text_from_annotation_dicts(self, annotations: List[ConllTagInfo]) -> str:
        """
        Returns the conll text associated with `annotations`.
        
        annotations: List containig the dictionary that holds the information about the tag
        
        returns: The annotated conll text representation
        """
        # Create text
        result = ""
        for tag_info in annotations:
            if tag_info == self.__sent_separator:
                to_write = "\n"
            else:
                to_write = self.ANNOTATION_FORMAT.format_map(tag_info)
                to_write = to_write.replace("-none", "") # Remove unnecesary labels
            result += to_write
        return result
    