from pathlib import Path
import sys
from typing import Tuple
from .link_predictor import LinkPredictor
from utils.notebook_utils import export_notebook_as_module
import importlib

class TensorflowLinkPredictor(LinkPredictor):
    """
    Uses the trained model to perform the prediction task
    """
    
    def __init__(self, info_tag: str, source_language: str, max_worker: int=1, max_argumentative_distance: int=10, **kwargs) -> None:
        super().__init__(max_worker=max_worker, max_argumentative_distance=max_argumentative_distance)
        
        export_notebook_as_module(
            Path(__file__, "..", "models", "link_prediction.ipynb").resolve(),
            new_params={
                **kwargs,
            },
            new_cap_variables={
                "INFO_TAG": f'"{info_tag}"',
                "LANGUAGE": f'"{source_language}"'
            }
        )
        
        import link_prediction.models.link_prediction as link_model
        if "link_prediction.models.link_prediction" in sys.modules:
            importlib.reload(link_model)

        self.process_file = link_model.process_file
        self._params = link_model.params.copy()
        self.model = link_model.load_and_build_model_from_params(self._params)

    def predict_links(self, content: str, file_key: str, source_language: str="english", **kwargs) -> str:
        result = self.process_file(self._params, content, source_language=source_language)
        return result
    
    def links_from_arguments(self, source_argument: str, target_argument: str, distance: int) -> Tuple[str, str, str]:
        result = self.model([source_argument], [target_argument], [distance])
        return result[0]