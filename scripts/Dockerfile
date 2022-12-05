FROM tensorflow/tensorflow:2.9.1-jupyter

COPY ./build_data/ .
COPY ./install_awesome_align_docker.sh ./install_awesome_align_docker.sh
COPY ./install_spacy.sh ./install_spacy.sh
COPY ./install_nltk_resources.sh ./install_nltk_resources.sh

RUN python3 -m pip install --upgrade pip \
 && pip install tensorflow-addons \
 && pip install nltk && python -m nltk.downloader popular \
 && chmod 777 install_nltk_resources.sh && bash install_nltk_resources.sh noancora && mv es-ancora.map ~/nltk_data/taggers/universal_tagset/es-ancora.map \
 && pip install pandas \
 && pip install scikit-learn \
 && pip install deep-translator \
 && pip install streamlit \
 && chmod 777 install_awesome_align_docker.sh && bash install_awesome_align_docker.sh \
 && chmod 777 install_spacy.sh && bash install_spacy.sh \
 && rm essay001.ann.conll.align install_awesome_align_docker.sh install_spacy.sh install_nltk_resources.sh
