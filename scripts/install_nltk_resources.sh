python3 -m nltk.downloader punkt
python3 -m nltk.downloader universal_tagset
python3 -m nltk.downloader cess_esp
python3 -m nltk.downloader averaged_perceptron_tagger

if [[ $1 = noancora ]] 
then
    echo "Not installing ancora map."
else
    cp build_data/es-ancora.map ~/nltk_data/taggers/universal_tagset/es-ancora.map
fi
