#!/bin/bash

docker run -it --rm -v "$(realpath ./..)":/tf/notebooks --entrypoint /bin/bash -p 8888:8888 -p 8001:8001 argument-mining-final-tensorflow:2.9.1-jupyter -c "cd /tf/notebooks/scripts/ && ./run_streamlit.sh"
