from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Tuple
from .parser import AnnotatedRawTextInfo, ArgumentationInfo, Parser
import pandas as pd
import logging as log
import random

class BratParser(Parser):
    """
    Parse files annotated with BRET tool. The files must end in .ann for the parser to work out of the box.
    """
    
    # Regex using named groups
    ARGUMENTATIVE_UNIT = r"^T(?P<prop_id>\d+)\s(?P<prop_type>[\w\-_]+)\s(?P<prop_init>\d+)\s(?P<prop_end>\d+)\s(?P<prop_text>.+)\s*$"
    RELATION = r"^R(?P<relation_id>\d+)\s(?P<relation_type>[\w\-_]+)\sArg1:T(?P<prop_id_source>\d+)\sArg2:T(?P<prop_id_target>\d+)\s*$"
    
    def __init__(self, **kwargs) -> None:
        super().__init__((".ann",), ".ann")
        self.argumentative_unit_regex = re.compile(self.ARGUMENTATIVE_UNIT)
        self.relation_regex = re.compile(self.RELATION)

    def unknown_match_handler(self, content: str, argumentative_units: pd.DataFrame, non_argumentative_units: pd.DataFrame, relations: pd.DataFrame, file: Path, index: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Handler for mismatched content
        """
        log.warning(f"Line {index} file {file.name}. Match not found: {content}")
        return argumentative_units, non_argumentative_units, relations

    def parse(self, content:str, file: Path, **kwargs) -> ArgumentationInfo:
        """
        Parse `content` returning DataFrames containing
        the argumentative unit and the relation information.
        
        content: text containing the content to parse
        file: Content's original file
        
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
          
        return: (argumentative_units, relations, non_argumentative_units)
        """
        content_lines = content.splitlines()
        original_text_file = (file / ".." / ((".".join(file.name.split('.')[:-1]) if "." in file.name else file.name) + ".txt")).resolve()
        original_text = original_text_file.read_text()

        argumentative_units = pd.DataFrame(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
        non_argumentative_units = pd.DataFrame(columns=["prop_init", "prop_end", "prop_text"])
        relations = pd.DataFrame(columns=["relation_id", "relation_type", "prop_id_source", "prop_id_target"])
        
        for i,line in enumerate(content_lines):
            argument_match = self.argumentative_unit_regex.match(line)
            if argument_match:
                argument_dict = argument_match.groupdict()
                
                argument_dict["prop_id"] = int(argument_dict["prop_id"])
                argument_dict["prop_init"] = int(argument_dict["prop_init"])
                argument_dict["prop_end"] = int(argument_dict["prop_end"])
                argument_dict["prop_type"] = argument_dict["prop_type"].replace("-", "_")

                argumentative_units = pd.concat([argumentative_units, pd.DataFrame(argument_dict, index=[0])], ignore_index=True)
                continue
            relation_match = self.relation_regex.match(line)
            if relation_match:
                argument_dict = relation_match.groupdict()
                
                argument_dict["relation_id"] = int(argument_dict["relation_id"])
                argument_dict["prop_id_source"] = int(argument_dict["prop_id_source"])
                argument_dict["prop_id_target"] = int(argument_dict["prop_id_target"])
                argument_dict["relation_type"] = argument_dict["relation_type"].replace("-", "_")
                
                relations = pd.concat([relations, pd.DataFrame(argument_dict, index=[0])], ignore_index=True)
                continue
            argumentative_units, non_argumentative_units, relations = self.unknown_match_handler(line, argumentative_units, non_argumentative_units, relations, file, i)
            
        argumentative_units.sort_values(by="prop_init", inplace=True)
        
        order_ids = {old_id: new_id for new_id, old_id in enumerate(argumentative_units['prop_id'], start=1)}
        argumentative_units['prop_id'] = argumentative_units['prop_id'].map(lambda x: order_ids.get(x, -1))
        relations['prop_id_source'] = relations['prop_id_source'].map(lambda x: order_ids.get(x, -1))
        relations['prop_id_target'] = relations['prop_id_target'].map(lambda x: order_ids.get(x, -1))
        
        last_match = 0
        for _, (_, _, prop_init, prop_end, _) in argumentative_units.iterrows():
            if last_match < prop_init:
                # Non argumentative gap
                non_argument_dict = {
                    "prop_init":last_match,
                    "prop_end":prop_init,
                    "prop_text":original_text[last_match:prop_init],
                }
                non_argumentative_units = pd.concat([non_argumentative_units, pd.DataFrame(non_argument_dict, index=[0])], ignore_index=True)
                # last_match = prop_end
            elif last_match == prop_init:
                # Arguments together
                pass
            else:
                log.warning("Inconsistency gap")
            last_match = prop_end
        
        if last_match != len(original_text):
            # If text ends in a non argumentative gap
            non_argument_dict = {
                "prop_init":last_match,
                "prop_end":len(original_text),
                "prop_text":original_text[last_match:len(original_text)],
            }
            non_argumentative_units = pd.concat([non_argumentative_units, pd.DataFrame(non_argument_dict, index=[0])], ignore_index=True)
        
        return argumentative_units, relations, non_argumentative_units

    def from_dataframes(self, dataframes: Dict[str, ArgumentationInfo], language="english", **kwargs) -> Dict[str, AnnotatedRawTextInfo]:
        """
        Creates a Brat annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        language: Language for tokenization process
        
        returns: Brat annotated string, Raw text
        """
        
        results = {}
        default_gap = " "

        argumentative_format = "T{prop_id}\t{prop_type} {prop_init} {prop_end}\t{prop_text}\n"
        relation_format = "R{relation_id}\t{relation_type} Arg1:T{prop_id_source} Arg2:T{prop_id_target}\n"
        
        for file_path_str, (argumentative_units, relations, non_argumentative_units) in dataframes.items():

            result = ""
            all_units = pd.concat([argumentative_units, non_argumentative_units], ignore_index=True)
            all_units.sort_values(by="prop_init", inplace=True)
            all_units = all_units.reindex(columns=["prop_id", "prop_type", "prop_init", "prop_end", "prop_text"])
            max_length = all_units["prop_end"].max()
            
            text = default_gap*max_length
            
            for index, (prop_id, prop_type, prop_init, prop_end, prop_text) in all_units.iterrows():
                text = text[:prop_init] + prop_text + text[prop_end:]
                if pd.notna(prop_id) and pd.notna(prop_type):
                    to_write = argumentative_format.format_map({
                        "prop_id": int(prop_id),
                        "prop_type": prop_type,
                        "prop_init": prop_init,
                        "prop_end": prop_end,
                        "prop_text": prop_text
                    })
                    result += to_write
            
            relations = relations.reindex(columns=["relation_id", "relation_type", "prop_id_source", "prop_id_target"])
            
            for index, (relation_id, relation_type, prop_id_source, prop_id_target) in relations.iterrows():
                to_write = relation_format.format_map({
                    "relation_id": int(relation_id),
                    "relation_type": relation_type,
                    "prop_id_source": prop_id_source,
                    "prop_id_target": prop_id_target,
                })
                result += to_write
            
            results[file_path_str] = result, text
        
        return results

    def create_conf_files(self, corpus_path: Path, relation_types: Iterable[str], argument_types: Iterable[str]):
        """
        Creates the configuration files needed by bart. The files created are:
        - annotation.conf
        - tools.conf
        - visual.conf
        
        corpus_path: Path to save the generated files
        relation_types: Relation types extracted from the corpus
        argument_types: Arguments types extracted from the corpus
        """
        
        # Annotation file
        annotation_file = corpus_path / "annotation.conf"
        
        # Generating entities
        annotation_content = "[entities]\n\n"
        argument_entities = sorted(argument_types)
        annotation_content += "\n".join(argument_entities)
        
        # Generating relations. All vs All
        annotation_content += "\n\n[relations]\n\n"
        relations = sorted(relation_types)
        annotation_content += "\n".join(relation + " " + "Arg1:" + "|".join(argument_entities) + ", Arg2:" + "|".join(argument_entities) for relation in relations)
        
        
        # Generating attributes
        annotation_content += "\n\n[attributes]\n\n"

        # Generating events
        annotation_content += "\n\n[events]\n\n"
        
        
        # Writing the file
        annotation_file.touch(exist_ok=True)
        annotation_file.write_text(annotation_content)
        
        
        # Tools file
        tools_file = corpus_path / "tools.conf"
        
        
        # Visual file
        visual_file = corpus_path / "visual.conf"
        visual_content = "[labels]\n\n"
        
        visual_content += "\n".join(f"{arg}|{arg}" for arg in argument_entities)
        visual_content += "\n\n[drawing]\n\n"
        gen = random.Random()
        gen.seed("".join(argument_entities + relations))
        visual_content += "\n".join(f"{arg}\tbgColor:#{gen.randint(0,0xFFFFFF):06x}" for arg in argument_entities)
        
        visual_file.touch(exist_ok=True)
        visual_file.write_text(visual_content)

    def create_conf_files_from_argumentation_dict(self, corpus_path: Path, argumentation_dict: Dict[str, ArgumentationInfo]):
        """
        Creates the configuration files needed by bart. The files created are:
        - annotation.conf
        - tools.conf
        - visual.conf
        
        corpus_path: Path to save the generated files
        argumentation_dict: Result of calling the `parse_dir` function
        """
        
        relations = set()
        arguments = set()
        
        for info in argumentation_dict.values():
            arg, rel, _ = info
            relations.update(rel['relation_type'])
            arguments.update(arg['prop_type'])
        
        self.create_conf_files(corpus_path, relations, arguments)

class PersuasiveEssaysParser(BratParser):
    """
    Parser created for the PersuasiveEssays Corpus. Convert the claim's stances into attack or support relations.
    New relations will be directed from the Claim to all MajorClaims 
    """
    
    STANCE = r"^A(?P<prop_id>\d+)\sStance\sT(?P<prop_id_source>\d+)\s(?P<stance_relation_type>(Against)|(For))\s*$"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.stance_regex = re.compile(self.STANCE)
        
    def unknown_match_handler(self, content: str, argumentative_units: pd.DataFrame, non_argumentative_units: pd.DataFrame, relations: pd.DataFrame, file: Path, index: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        stance_match = self.stance_regex.match(content)
        if stance_match:
            argument_dict = stance_match.groupdict()
            
            argument_dict["relation_id"] = -1 # Mark Relation ID
            argument_dict["prop_id_source"] = int(argument_dict["prop_id_source"]) 
            argument_dict["prop_id_target"] = 1 # Must be filled with all Major Claims 
            
            relations = pd.concat([relations, pd.DataFrame(argument_dict, index=[0])], ignore_index=True)

            return argumentative_units, non_argumentative_units, relations
        else:
            return super().unknown_match_handler(content, argumentative_units, non_argumentative_units, relations, file, index)
    
    def parse(self, content: str, file: Path, **kwargs) -> ArgumentationInfo:
        argumentative_units, relations, non_argumentative_units = super().parse(content, file, **kwargs)
        relations_add = {
            "relation_id": [], 
            "relation_type": [], 
            "prop_id_source": [], 
            "prop_id_target": [],
        }

        relation_len = len(relations)
        stance_relation_dict = {
            'Against': "attacks",
            'For': 'supports'
        }
        
        # Add an attack or support relation to every MajorClaim from every Claim with a Stance
        for _, rel_row in relations[relations['relation_id'] == -1].iterrows():
            for _, arg_row in argumentative_units[argumentative_units['prop_type'] == "MajorClaim"].iterrows():
                relations_add['relation_id'].append(relation_len + 1 + len(relations_add['relation_id']))
                relations_add['relation_type'].append(stance_relation_dict[rel_row['stance_relation_type']])
                relations_add['prop_id_source'].append(rel_row['prop_id_source'])
                relations_add['prop_id_target'].append(arg_row['prop_id'])
                
        relations = relations.drop(relations[relations['relation_id'] == -1].index)
        relations = pd.concat([relations, pd.DataFrame(relations_add)], ignore_index=True)
        
        return argumentative_units, relations, non_argumentative_units