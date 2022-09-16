from pathlib import Path
from typing import List
import tensorflow as tf
from utils.notebook_utils import export_notebook_as_module
from .segmenter import ArgumentSegmenter, SplittedArgumentInfo
import importlib
import sys

class TensorflowArgumentSegmenter(ArgumentSegmenter):
    
    def __init__(self, info_tag: str, source_language: str, **kwargs) -> None:
        super().__init__(max_worker=1)

        export_notebook_as_module(
            Path(__file__, "..", "models", "segmenter.ipynb").resolve(),
            new_params={
                **kwargs
            },
            new_cap_variables={
                "INFO_TAG": f'"{info_tag}"',
                "LANGUAGE": f'"{source_language}"'
            })

        import segmenter.models.segmenter as segmenter_model
        if "segmenter.models.segmenter" in sys.modules:
            importlib.reload(segmenter_model)

        self._params = segmenter_model.params.copy()
        self.model = segmenter_model.load_and_build_model_from_params(self._params)

    def extract_arguments_from_text(self, text: str) -> List[SplittedArgumentInfo]:
        data = tf.constant([text])
        encoded_tags = self.model(data)
        return list(zip(text.split(" "), encoded_tags[0]))
