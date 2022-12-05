#!/bin/bash

docker run -it --rm -v "$(realpath ./..)":/tf/notebooks -p 8888:8888 argument-mining-final-tensorflow:2.9.1-jupyter
