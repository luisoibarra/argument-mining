

from concurrent.futures import Future, ThreadPoolExecutor, wait

import pandas
from corpus_parser.conll_parser import ConllParser, ConllTagInfo
from pathlib import Path
from typing import Dict, List, Tuple
import random as rand

class LinkPredictor:
    """
    Base class for link prediction task
    """
    
    def __init__(self, max_worker: int = 3, max_argumentative_distance: int=10, using_bioes_tags=True) -> None:
        self.max_worker = max_worker
        self.max_argumentative_distance = max_argumentative_distance
        self.using_bioes_tags = using_bioes_tags
        
    def predict_link_dir(self, annotation_dir: Path, export_dir: Path, source_language: str="english", **kwargs):
        """
        Creates a corpus with the relation between the argumentative
        components.
        
        annotation_dir: Path that contains the .conll files with the annotations
        export_dir: Path to export the new cropus with the relations
        """
        
        annotated_files = [file for file in annotation_dir.iterdir() if file.name.endswith(".conll")]
        
        if not export_dir.exists(): export_dir.mkdir(exist_ok=True, parents=True)
        
        batch = len(annotated_files)//self.max_worker + 1
        
        def batch_work(slice: int) -> str:
            for annotated_file in annotated_files[batch*slice:batch*(slice+1)]:
                                
                predicted_links_conll = self.predict_links(annotated_file.read_text(), str(annotated_file), source_language=source_language, **kwargs)
                
                target_annotated_file = export_dir / (annotated_file.name + ".link.conll")
                
                target_annotated_file.write_text(predicted_links_conll)
        
        futures: List[Future] = []
        with ThreadPoolExecutor(max_workers=self.max_worker) as exe:
            for i in range(self.max_worker):
                futures.append(exe.submit(batch_work, i))
                # batch_work(i)
        wait(futures)
        exceptions = [future.exception() for future in futures if future.exception()]
        
        if exceptions:
            raise Exception(exceptions)

    def predict_links(self, content: str, file_key: str=None, source_language: str="english", **kwargs) -> str:
        """
        Receive a conll content and return a list with 
        the annotated conll links.
        
        content: Conll text
        file_key: String that identifies the file containing the given content.
        
        returns: The conll text representing the relations
        """
        parser = ConllParser(bioes=self.using_bioes_tags)
        argumentative, relations, non_argumentative = parser.parse(content, source_language=source_language, **kwargs)
        argumentative_tuples = list(zip(argumentative['prop_id'], argumentative['prop_text'], argumentative['prop_type']))

        predictions: Dict[Tuple[int,int], Tuple[str,str,str]] = {
            
        }

        # Get relations by comparing all posible relations
        for prop_id_source, source_text, source_tag in argumentative_tuples:
            for prop_id_target, target_text, target_tag in argumentative_tuples:
                distance = prop_id_target - prop_id_source
                if prop_id_source == prop_id_target:
                    # No self relations are allowed
                    continue
                if abs(distance) > self.max_argumentative_distance:
                    # Distance is greater than the max distance allowed
                    continue
                
                predicted_relation_tag, predicted_source_tag, predicted_target_tag = self.links_from_arguments(source_text, target_text, distance)

                if source_tag != predicted_source_tag or target_tag != predicted_target_tag:
                    print(f"{source_tag} != {predicted_source_tag} or {target_tag} != {predicted_target_tag}")
                
                if predicted_relation_tag:
                    predictions[prop_id_source, prop_id_target] = predicted_relation_tag, predicted_source_tag, predicted_target_tag

        # Remove inverse relations. If the forward relation doesn't exist then
        # it will be added in either case the inverse relation will be removed.
        to_add = {}
        to_remove = set()
        for (source_id, target_id), (predicted_relation_tag, predicted_source_tag, predicted_target_tag) in predictions.items():
            inverse_relation = predicted_relation_tag.endswith("_Inverse")
            if inverse_relation:
                try:
                    _ = predictions[target_id, source_id]
                except KeyError:
                    # Add the forward relation
                    no_inverse_tag = predicted_relation_tag[:-len("_Inverse")]
                    to_add[target_id, source_id] = no_inverse_tag, predicted_target_tag, predicted_source_tag
                # Remove inverse relation
                to_remove.add((source_id, target_id))
        
        # Commit actions to predictions
        for key in to_remove:
            predictions.pop(key)
        predictions.update(to_add)
        
        # Empty relations table and fill with calculated values
        relation_dict = {
            'relation_id': [],
            'relation_type': [],
            'prop_id_source': [],
            'prop_id_target': [],
        }
        relation_id = 1
        for (source_id, target_id), (predicted_relation_tag, predicted_source_tag, predicted_target_tag) in predictions.items():
            relation_dict['relation_id'].append(relation_id)
            relation_dict['relation_type'].append(predicted_relation_tag)
            relation_dict['prop_id_source'].append(source_id)
            relation_dict['prop_id_target'].append(target_id)
            relation_id += 1
        relations = pandas.DataFrame(relation_dict)
        
        result = parser.from_dataframes({file_key: (argumentative, relations, non_argumentative)}, source_language=source_language, **kwargs)
        return result[file_key][0]
        
    def links_from_arguments(self, source_argument: str, target_argument: str, distance: int) -> Tuple[str, str, str]:
        """
        Return the relations between `source_argument` and `target_argument`.
        
        source_argument: Candidate to source argument
        target_argument: Candidate to target argument
        distance: Argumentative distance between source and target 
        
        returns: (relation_type, source_type, target_type)
        """
        raise NotImplementedError()

class RandomLinkPredictor(LinkPredictor):
    """
    Random link predictor. Predicts random relation and argumentative tags from given sets
    """
    
    def __init__(self, argumentative_tags: List[str], relation_tags: List[str]) -> None:
        super().__init__()
        self.relation_tags = relation_tags
        self.argumentative_tags = argumentative_tags
    
    def links_from_arguments(self, source_argument: str, target_argument: str, distance: int) -> Tuple[str, str, str]:
        return (rand.choice(self.relation_tags), rand.choice(self.argumentative_tags), rand.choice(self.argumentative_tags))
