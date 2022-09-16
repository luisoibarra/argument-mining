# Sentence Aligner

Package that perform the tasks related to sentence alignment.

## Problem

Given a text, split the text in sentences and translate each sentence. Then create a file containing each sentence with its translation.

```bash

Sentence in source language ||| Oración en lenguage origen
...

```

## Translator

Translators are responsible for translating sentences from the source language to the target language.

### Translator Usage

The translator are used directly by the **SentenceAligner** by passing it on the constructor.

- DeepTranslator: Based on [deep_translator](https://github.com/nidhaloff/deep-translator). Translated sentences are saved on disk.
  - GoogleDeepTranslator: Use the google api to translate sentences.

#### Translator Python API

To use this as a python api import the corresponding **Translator** from `translator.py` and call the wanted function.

```python
from sentence_aligner.translator import GoogleDeepTranslator

translator = GoogleDeepTranslator()
# Returns "Oración en lenguage origen"
translator.translate("Sentence in source language", "english", "spanish")
```

**Adding new ArgumentSegmenters:**

To add new translator just create a class that extends from **Translator** and implement the methods (See **SelfTranslator**). Other variants of **DeepTranslator** that use other translation APIs can be easily created.

## Usage

### Console

```bash

usage: main.py [-h] [--translator {google,corpus}]
               [--source_language SOURCE_LANGUAGE]
               [--target_language TARGET_LANGUAGE]
               conll_parsed_path sentence_alignment_path

positional arguments:
  conll_parsed_path     Destination path to save the parsed files
  sentence_alignment_path
                        Destination path to save the aligned sentences

optional arguments:
  -h, --help            show this help message and exit
  --translator {google,corpus}
                        Select the translation process
  --source_language SOURCE_LANGUAGE
                        Source language
  --target_language TARGET_LANGUAGE
                        Target language

```

### Python API

To use this as a python api import the corresponding **ArgumentSegmenter** from `segmenter.py` and call the wanted function.

```python
from pathlib import Path
from sentence_aligner.translator import GoogleDeepTranslator
from sentence_aligner.sentence_aligner import SentenceAligner

sentence_aligner = SentenceAligner(GoogleDeepTranslator())
sentence_aligner.sentence_alignment_dir(Path("data/parsed_to_conll/testing"), Path("data/sentence_alignment/testing"), source_language="english", target_language="spanish")
```
