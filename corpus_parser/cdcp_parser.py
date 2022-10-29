from pathlib import Path
import re
from typing import Dict, Iterable, List, Optional, Tuple
from .parser import AnnotatedRawTextInfo, ArgumentationInfo, Parser
import json
import pandas as pd

class CDCPParser(Parser):
    
    def __init__(self, **kwargs) -> None:
        super().__init__((".ann.json", ), ".ann.json")
        
        
    def parse(self, content:str, file: Optional[Path] = None, **kwargs) -> ArgumentationInfo:
        """
        Parse `content` returning DataFrames containing
        the argumentative unit and the relation information.
        
        content: text containing the content to parse
        file: Optional, content's original file
        
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
        original_text_file = (file / ".." / ((".".join(file.name.split('.')[:-2]) if "." in file.name else file.name) + ".txt")).resolve()
        original_text = original_text_file.read_text()

        content_json = json.loads(content)
        
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
        
        offsets = [(off,i) for i, off in enumerate(content_json['prop_offsets'])]
        offsets.sort(key=lambda x: x[0][0])
        
        prop_dict = dict((off[1], i) for i, off in enumerate(offsets))
        
        last_arg_index = 0
        prop_id = 0
        for (init, end), original_index in offsets:
            if init != last_arg_index:
                # Non argumentative unit present
                non_argumentative_units["prop_init"].append(last_arg_index) 
                non_argumentative_units["prop_end"].append(init)
                non_argumentative_units["prop_text"].append(original_text[last_arg_index:init])
                    
            
            argumentative_units["prop_id"].append(prop_id)
            argumentative_units["prop_type"].append(content_json["prop_labels"][original_index])
            argumentative_units["prop_init"].append(init) 
            argumentative_units["prop_end"].append(end)
            argumentative_units["prop_text"].append(original_text[init:end])
            
            last_arg_index = end
            
            prop_id += 1
        
        if last_arg_index < len(original_text):
            # Missing last non argumentative unit
            non_argumentative_units["prop_init"].append(last_arg_index) 
            non_argumentative_units["prop_end"].append(len(original_text))
            non_argumentative_units["prop_text"].append(original_text[last_arg_index:])

        relation_id = 1

        def add_relations(key: str, relation_id: int):
            for (init, end), proposition in content_json[key]:
                for i in range(init, end+1):
                    relations["relation_id"].append(relation_id)
                    relations["relation_type"].append(key)
                    relations["prop_id_source"].append(prop_dict[i])
                    relations["prop_id_target"].append(prop_dict[proposition])

                    relation_id += 1
        
            return relation_id
        
        
        relation_id = add_relations('reasons', relation_id)
        relation_id = add_relations('evidences', relation_id)
        
        arg, rel, non_arg = pd.DataFrame(argumentative_units), pd.DataFrame(relations), pd.DataFrame(non_argumentative_units)
        
        return arg, rel, non_arg
                    
    def from_dataframes(self, dataframes: Dict[str, ArgumentationInfo], source_language="english", **kwargs) -> Dict[str, AnnotatedRawTextInfo]:
        """
        Creates file with annotated corpus representing the received DataFrames. 
        
        dataframes: The result from calling a parse function in any Parser class
        the keys aren't important, so a mock key can be passed.
        language: Language for tokenization process
        
        returns: Annotated string, Raw entire text
        """
        result = {}
        for key, (arg_units, realations, non_arg_units) in dataframes.items():
        
            content_json = {
                "evidences": [],
                "prop_labels": [],
                "prop_offsets": [],
                "reason": [],
                "url": {}
            }

            for _, row in arg_units.iterrows():
                content_json['prop_offsets'].append([row['prop_init'], row['prop_end']])

            for relation_type, realtion_group in realations.groupby(by="realtion_type"):
                for prop_id_target, group in realtion_group.groupby(by="prop_id_target"):
                    sources = list(group['prop_id_source'])
                    content_json[relation_type].append([sources, prop_id_target])

            all_units = pd.concat([arg_units, non_arg_units], ignore_index=True)
            all_units.sort_values(by="prop_init", inplace=True)
            all_units = all_units["prop_text"]

            text = " ".join(all_units)
            
            result[key] = json.dumps(content_json), text
        
        return result