#!/bin/bash
if [ ! -f ./lid.176.bin ]; then
    echo "Downloading FastText language model..."
    curl -L -o lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
    echo "Download complete."
fi
uvicorn main:app --host 0.0.0.0 --port 10000