#!/bin/bash

pip install awesome-align
awesome-align --model_name_or_path bert-base-multilingual-cased --data_file essay001.ann.conll.align --output_file essay001.ann.conll.align.bidirectional --batch_size 32 --extraction softmax