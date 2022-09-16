# Aligner

It is responsible for applying the bidirectional alignments algorithms to the corpus.

## Problem

The aligners are in charge of finding the alignment of words between them, given two sentences, one original in the source language and another that is the translation of the original in some target language. A word alignment is a link between the word in the original sentence and the words representing it in the target sentence. For example:

- Original sentence: `The blue sky will be dark at night`
- Target sentene: `El cielo azul será oscuro en la noche`
- Alignment: `1-1 2-3 3-2 4-4 5-4 6-5 7-6 8-7 8-8`

The alignment, as can be seen, is a many-to-many relationship between the tokens of the original and target sentences.

## Alignment tools

To perform this task two tools are supported:

- [fast_align](https://github.com/clab/fast_align): **FastAlignAligner**
- [awesome_align](https://github.com/neulab/awesome-align): **AwesomeAlignAligner**

## Usage

### Console

```bash
usage: main.py [-h] [--aligner {awesome_align,fast_align}]
               [--max_worker MAX_WORKER]
               sentence_alignment_path bidirectional_path

positional arguments:
  sentence_alignment_path
                        Destination path to save the aligned sentences
  bidirectional_path    Destination path to save the sentence's bidirectional
                        alignments

optional arguments:
  -h, --help            show this help message and exit
  --aligner {awesome_align,fast_align}
                        Select the alignment algorithm to use
  --max_worker MAX_WORKER
                        Max threads active that can have the process
```

### Python API

To use this as a python api import the corresponding **Aligner** from `aligner.py` and call the wanted function.

```python
from pathlib import Path
from aligner.aligner import FastAlignAligner

aligner = FastAlignAligner()
aligner.do_bidirectional_align_file(Path("data/sentence_alignment/testing"), Path("data/bidirectional_alignmet/testing"))
```

### Adding new Aligners

To add new aligner just create a class that extends from **Aligner** and implement the methods (See **SelfLanguageAligner**).
