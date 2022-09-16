# Data

Folder where the corpus will be kept for a more organized work. Its inclusion in this folder is not mandatory, but the organization that will be explained is assumed throughout the repository.

## Organización

The folders are structured according to when the files were generated. Within each folder that represents the moment there will be folders with the name of the corpus that generated it. A complete example with the corpus name **testing** is in the repository.

### Projección de corpus

1. corpus: Unprocessed corpus.
2. parsed_to_conll: Corpus processed into standard format.
3. translation: Translation files, mostly cache.
4. sentence_alignment: Aligned corpus sentences in source language and target language.
5. bidirectional_alignment: Aligned sentence bidirectional alignments.
6. projection: Corpus in standard format with annotations projected in the target language.

### Argument Segmentation

1. segmenter_corpus: Files related to training the segmentation model.
2. segmenter_processed: Result of applying the model to segment arguments
3. to_process: Files not annotated to be processed

### Link Prediction

1. link_prediction: Files related to the model training.
2. link_prediction_processed: Result of applying the link prediction model to the segmented arguments.
