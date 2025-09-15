#!/bin/bash
# if [ ! -f ./lid.176.bin ]; then
#     echo "Downloading FastText language model..."
#     curl -L -o lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
#     echo "Download complete."
# fi
mkdir -p chroma_db

# Download the zip if it doesn't already exist
echo "Downloading ChromaDB index..."
curl -L -o chroma_db/chroma_db.zip \
https://medichatblobstorage.blob.core.windows.net/indexes/chroma_db.zip
echo "Extracting ChromaDB index..."
unzip -o chroma_db/chroma_db.zip -d chroma_db

uvicorn main:app --host 0.0.0.0 --port 10000
