#!/bin/bash

cd ..; pipreqs . --force && echo "pipreqs==0.4.11" >> requirements.txt && echo "tensorflow-addons" >> requirements.txt
