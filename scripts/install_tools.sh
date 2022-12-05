#!/bin/bash

echo "Downloading GloVe files"
./download_glove_embeddings.sh

echo "Installing Awesome Align"
./install_awesome_align.sh

echo "Installing Fast Align"
./install_fast_align.sh

echo "Installing Spacy"
./install_spacy.sh


if [[ $1 = nobrat ]] 
then
    echo "Not Installing Brat"
else
    echo "Installing Brat"
    ./install_brat.sh
fi
