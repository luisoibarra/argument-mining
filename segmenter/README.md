# Argument Segmentation

Package that perform the tasks related to argument segmentation.

## Problem

Given a plain text, extract and classify the argumentative units. An argumentative unit is a continuous span of text that carries argumentative meaning.

## Data

### Input

The expected data should be a raw .txt file containing the text to be segmented.

### Output

The files are written in CoNLL format with the argumentative units annotated.

## Training

The segmenter model isn't given in the repository, to create it open `segmenter.ipynb` and run the respective cells to train the model. Hyperparameters can be changed there.

Once the model is created it can be used by the console interface or the Python API and also in the notebook.

## Usage

### Console

```bash

usage: main.py [-h] [--segmenter {tensorflow}] [--corpus_tag CORPUS_TAG]
               [--source_language SOURCE_LANGUAGE]
               segmenter_source_path segmenter_export_path

positional arguments:
  segmenter_source_path
                        Path to the directory containing the files to perform
                        argument segmentation
  segmenter_export_path
                        Path to the save the result of the argument
                        segmentation process

optional arguments:
  -h, --help            show this help message and exit
  --segmenter {tensorflow}
                        Select the segmentation algorithm to use
  --corpus_tag CORPUS_TAG
                        Tag representing the corpus used for creating the
                        model
  --source_language SOURCE_LANGUAGE
                        Source language of the text to process

```

### Python API

To use this as a python api import the corresponding **ArgumentSegmenter** from `segmenter.py` and call the wanted function.

```python
from pathlib import Path
from segmenter.tf_segmenter import TensorflowArgumentSegmenter

segmenter = TensorflowArgumentSegmenter(info_tag="persuasive_essays_paragraph", source_language="spanish")
segmenter.extract_arguments_dir(Path("data/to_process/testing"), Path("data/segmenter_processed/testing"))
```

### Adding new ArgumentSegmenters

To add new aligner just create a class that extends from **ArgumentSegmenter** and implement the methods (See **RandomArgumentSegmenter**).
