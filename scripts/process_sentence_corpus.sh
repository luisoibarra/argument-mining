#!/bin/bash

# The corpus path must contain 3 files called "dev.conll", "train.conll" and "test.conll"
# containing the sentences separated by an empty line

cd ..

if [ -z "$1" ]
then
    echo "Missing required parameter CORPUS_NAME."
    echo "Example \$./process_sentence_corpus.sh testing"
    exit 1
fi

CORPUS_NAME=$1

python3 project_corpus.py \
"data/corpus/$CORPUS_NAME" \
"data/parsed_to_conll/$CORPUS_NAME" \
"data/sentence_alignment/$CORPUS_NAME" \
"data/bidirectional_alignment/$CORPUS_NAME" \
"data/projection/$CORPUS_NAME"
