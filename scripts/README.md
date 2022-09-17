# Scripts

Folder containing helper scripts to install or run the tools used.

## Assumptions

- Working on a Linux environment, like Ubuntu
- Installed (Usually this tools are installed by default):
  - `git`
  - `make`
  - `cmake`
- The script will run being in the scripts folder
  - `scripts$ ./install_fast_align.sh`

## Summary

- `build_docker_image.sh`: Builds the docker image that can be used to run the jupyter notebooks and the devcontainers.
- `download_glove_embeddings.sh`: Download the GloVe Embeddings (Spanish and English)
- `generate_requirements.sh`: Generate the requirements.txt file
- `install_awesome_align_docker.sh`: Install awesome-align in the docker container and download the BERT corpus used
- `install_awesome_align.sh`: Install awesome-align in local computer and download the BERT corpus used
- `install_brat.sh`: Download and install brat
- `install_fast_align.sh`: Download and install fast-align
- `install_nltk_resources.sh`: Install missing nltk resources
- `install_tools.sh`: Download and install all tools needed.
- `process_paragraph_corpus.sh`: Process a paragraph like corpus from raw corpus to projection
- `process_raw_text.sh`: Given a path with text files, extract its arguments and relations
- `process_sentence_corpus.sh`: Process a sentence like corpus from raw corpus to projection
- `run_brat.sh`: Run brat server
- `run_docker_container.sh`: Run jupyter notebook on a docker container.
- `train_link_predictor.sh`: Train the link prediction model
- `train_segmenter.sh`: Train the argument segmenter model
