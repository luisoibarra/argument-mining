cd ..

if [ -z "$1" ]
then
    echo "Missing required parameter CORPUS_NAME."
    echo "Usage: ./process_raw_text persuasive_essays_paragraph spanish"
    exit 1
fi

if [ -z "$2" ]
then
    echo "Missing required parameter CORPUS_LANGUAGE."
    echo "Usage: ./process_raw_text persuasive_essays_paragraph spanish"
    exit 1
fi

CORPUS_NAME=$1
LANGUAGE=$2

python3 predict_relations.py --corpus_tag $CORPUS_NAME --source_language $LANGUAGE \
"data/to_process/$CORPUS_NAME" \
"data/segmenter_processed/$CORPUS_NAME" \
"data/link_prediction_processed/$CORPUS_NAME"

