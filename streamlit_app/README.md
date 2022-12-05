# Streamlit app

Package that stores the streamlit app. This app allows to perform the extraction of the argumentative components
from a text or file and export it to brat format. Also can be used to perform the corpus projection and the training of the models.

## Usage

There are two ways of using the app. If you installed the requirements locally then you should have strealmit already installed. If not, install it by running `pip install streamlit`. Once installed run one of both commands:

1. In `scripts/`, run: `./run_stramlit.sh`
2. In `streamlit_app/`, run: `streamlit run main.py`

If you created the docker container, run the script `scripts/run_docker_streamlit.sh` to launch a container with the streamlit app.
