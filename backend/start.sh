#!/bin/bash
mkdir -p models
if [ ! -f ./models/lid.176.bin ]; then
    echo "Downloading FastText language model..."
    curl -L -o ../models/lid.176.bin \
        https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
    echo "Download complete."
fi
# Make sure the folder exists
mkdir -p chroma_db/bf424a1e-f7b4-49a4-938e-4accd3464d82

# Download the main sqlite file
if [ ! -f chroma_db/chroma.sqlite3 ]; then
    echo "Downloading chroma.sqlite3..."
    curl -L -o chroma_db/chroma.sqlite3 \
    https://medichatblobstorage.blob.core.windows.net/indexes/chroma.sqlite3
fi

# Download the folder items
for file in data_level0.bin header.bin index_metadata.pickle length.bin link_lists.bin; do
    if [ ! -f chroma_db/bf424a1e-f7b4-49a4-938e-4accd3464d82/$file ]; then
        echo "Downloading $file..."
        curl -L -o chroma_db/bf424a1e-f7b4-49a4-938e-4accd3464d82/$file \
        https://medichatblobstorage.blob.core.windows.net/indexes/bf424a1e-f7b4-49a4-938e-4accd3464d82/$file
    fi
done

uvicorn main:app --host 0.0.0.0 --port 10000
