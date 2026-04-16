# Language Detection Models

This directory contains machine learning models for language detection and other NLP tasks.

## Required Models

### `lid.176.bin` (fastText Language Identification)
- **Size**: ~160MB
- **Purpose**: Language detection for multi-language support
- **Download**: 
  ```bash
  curl -o lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
  ```
- **Source**: [Facebook AI Research fastText](https://fasttext.cc/docs/en/crawl-vectors.html)

## Setup

Run this once after cloning:

```bash
cd models
curl -o lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

The SDK will fail gracefully if this file is missing, with a clear error message pointing to this README.
