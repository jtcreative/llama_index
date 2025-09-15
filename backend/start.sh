
if [ ! -d ./chroma_db ]; then
    echo "Extracting Chroma index..."
    unzip compressed_index/index.zip -d chroma_db
fi
uvicorn main:app --host 0.0.0.0 --port 10000
