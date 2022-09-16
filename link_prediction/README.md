# Link Prediction

Package that perform the tasks related to link prediction.

## Problem

The arguments are related between them, the task is find and classify this relations.

## Data

### Input

The expected data should be in CoNLL format, containing the BIOES tags segmenting the arguments.

### Output

The files are written in CoNLL format with the links annotated.

## Training

The link prediction model isn't given in the repository, to create it open `link_prediction.ipynb` and run the respective cells to train the model. Hyperparameters can be changed there.

Once the model is created it can be used by the console interface or the Python API and also in the notebook.

## Usage

### Console

```bash

usage: main.py [-h] [--link_predictor {tensorflow}] [--corpus_tag CORPUS_TAG]
               [--source_language SOURCE_LANGUAGE]
               link_source_dir link_dest_dir

positional arguments:
  link_source_dir       Directory with the conll files to process
  link_dest_dir         Directory to save the precessed files

optional arguments:
  -h, --help            show this help message and exit
  --link_predictor {tensorflow}
                        Select the projection algorithm to use
  --corpus_tag CORPUS_TAG
                        Tag representing the corpus used for creating the
                        model
  --source_language SOURCE_LANGUAGE
                        Source language of the text to process

```

### Python API

To use this as a python api import the corresponding **LinkPredictor** from `link_predictor.py` and call the wanted function.

```python
from pathlib import Path
from link_prediction.tf_link_predictor import TensorflowLinkPredictor

link_predictor = TensorflowLinkPredictor(info_tag="persuasive_essays_paragraph", source_language="spanish")
link_predictor.predict_link_dir(Path("data/projection/testing"), Path("data/link_prediction_processed/testing"))
```

### Adding new LinkPredictors

To add new aligner just create a class that extends from **LinkPredictor** and implement the methods (See **RandomLinkPredictor**).
