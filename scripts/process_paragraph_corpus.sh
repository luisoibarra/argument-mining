# The corpus path must contain 3 folders named "dev", "train" and "test"
# this folders must contain annotated conll files

cd ..

if [ -z "$1" ]
then
    echo "Missing required parameter CORPUS_NAME."
    echo "\$./process_paragraph_corpus.sh testing"
    exit 1
fi

CORPUS_NAME=$1

python3 project_corpus.py \
"data/corpus/$CORPUS_NAME/dev" \
"data/parsed_to_conll/$CORPUS_NAME/dev" \
"data/sentence_alignment/$CORPUS_NAME/dev" \
"data/bidirectional_alignment/$CORPUS_NAME/dev" \
"data/projection/$CORPUS_NAME/dev" 

python3 project_corpus.py \
"data/corpus/$CORPUS_NAME/test" \
"data/parsed_to_conll/$CORPUS_NAME/test" \
"data/sentence_alignment/$CORPUS_NAME/test" \
"data/bidirectional_alignment/$CORPUS_NAME/test" \
"data/projection/$CORPUS_NAME/test" 

python3 project_corpus.py \
"data/corpus/$CORPUS_NAME/train" \
"data/parsed_to_conll/$CORPUS_NAME/train" \
"data/sentence_alignment/$CORPUS_NAME/train" \
"data/bidirectional_alignment/$CORPUS_NAME/train" \
"data/projection/$CORPUS_NAME/train"

