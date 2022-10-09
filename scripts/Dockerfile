FROM tensorflow/tensorflow:2.9.1-jupyter

COPY ./build_data/essay001.ann.conll.align ./essay001.ann.conll.align
COPY ./install_awesome_align_docker.sh ./install_awesome_align_docker.sh
COPY ./install_spacy.sh ./install_spacy.sh

RUN pip install tensorflow-addons \
 && pip install nltk && python -m nltk.downloader popular \
 && pip install pandas \
 && pip install scikit-learn \
 && pip install deep-translator \
 && ./install_awesome_align_docker.sh \
 && ./install_spacy.sh \
 && rm essay001.ann.conll.align install_awesome_align_docker.sh install_spacy.sh
