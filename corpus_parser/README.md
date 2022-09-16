# Corpus Parser

Parsers for corpus processing.

## Parsers

Parsers allow corpus conversion and management. One of its main functions is the transition from the corpus in its original form to a standard representation that is more manageable and familiar to the algorithms to be used.

### Conll

The .conll format is currently supported. In this it is assumed that annotations will have the form `"{tok}\t{bio_tag}-{prop_type}-{relation_type}-{relation_distance}\n"` where not counting `bio_tag` henceforth annotations are optional where:

- `tok`: Token's textual representation
- `bio_tag`: Token's BIOES tag. (Two sets of tags are available BIO and BIOES)
- `prop_type`: Token's argumentative component type
- `relation_type`: Relation type between argumentative units
- `realtion_distance`: Distance in argumentative components from the component it affects

### Brat

El formato de los corpus brat esperado consta de dos archivos por componente de corpus, el texto original y su anotación en formato .ann. La anotación sigue la regla de:

- Argumentative units: `"T{prop_id}\t{prop_type}\t{prop_init}\t{prop_end}\t{prop_text}"`
  - `prop_id`: Argumentative component id
  - `prop_type`: Argumentative component type
  - `prop_init`: Initial index of the proposition in the original text
  - `prop_end`: Final index of the proposition in the original text
  - `prop_text`: Argumentative component text
- Relations: `"{relation_id}\t{relation_type}\tArg1:T{prop_id_source}\tArg2:T{prop_id_target}"`
  - `relation_id`: Relation id
  - `relation_type`: Relation type
  - `prop_id_source`: Id of the source argumentative unit
  - `prop_id_target`: Id of the target argumentative unit

## Corpus representation

Since corpora can come in different forms, this package is used to bring it to a standard so that algorithms can be applied under the same corpus structure.

### Standardized DataFrames representation

The corpus is represented in a standard way as a set of DataFrames which store the information
relevant.

- argumentative_units: DataFrame that stores the information related to the argumentative components
  - `prop_id` Proposition ID inside the document
  - `prop_type` Proposition type
  - `prop_init` When the proposition starts in the original text
  - `prop_end` When the proposition ends in the  original text
  - `prop_text` Proposition text

- non_argumentative_units: DataFrame that stores the information related to the non-argumentative components
  - `prop_init` When the proposition starts in the original text
  - `prop_end` When the proposition ends in the   original text
  - `prop_text` Proposition text

- relations: DataFrame that stores the information related to relations
  - `relation_id` Relation ID inside the document
  - `relation_type` Relation type
  - `prop_id_source` Relation's source proposition id
  - `prop_id_target` Relation's target proposition id

### Standardized representation files

The selected standard is the CONLL format with textual representation. For example, these files represent a corpus unit:

- `file1.conll`: Contains BIO annotations in CONLL format.
- `file1.txt`: Contains the original text of the annotations.
