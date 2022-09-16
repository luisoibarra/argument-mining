# Projector

It is responsible for applying the projection algorithms to the corpus.

## Problem

Projectors are in charge of given two sentences, their alignment between them and the associated BIO tags to the source language sentence, tag the target language sentence with the associated BIO tags. For example:

- Original sentence: `The blue sky will be dark at night`
- Original sentence BIO: `B I I O O O O B`
- Target sentence: `El cielo azul será oscuro en la noche`
- Alignment: `1-1 2-3 3-2 4-4 5-4 6-5 7-6 8-7 8-8`
- Target sentence BIO: `B I I O O O B I`

## Projection algorithms

- [Cooling2018](https://github.com/UKPLab/coling2018-xling_argument_mining): **CrossLingualAnnotationProjector**

## Usage

### Console

### Python API

To use this as a python api import the corresponding **Aligner** from `aligner.py` and call the wanted function.

```python
from pathlib import Path
from projector.projector import CrossLingualAnnotationProjector

projector = CrossLingualAnnotationProjector()
projector.project_dir(Path("data/parsed_to_conll/testing"), Path("data/sentence_alignment/testing"), Path("data/bidirectional_alignment/testing"), Path("data/projection/testing"))
```

### Adding new Projectors

To add new aligner just create a class that extends from **Projector** and implement the methods (See **SelfLanguageProjector**).
