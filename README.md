# PDF Header Footer Extractor

A Python tool for automatically detecting and removing headers and footers from PDF documents, with special support for ISTQB documentation format.

## Features

- Automatic header and footer detection
- Smart content preservation (avoids removing non-header content)
- Support for different document versions (v2.0, v3.0)
- Batch processing capability
- Layout inspection tools

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Process a single file
python pdf_extractor.py --path file.pdf

# Inspect a file's layout
python pdf_extractor.py --path file.pdf --inspect --page 2

# Process all PDFs in a directory
python pdf_extractor.py --path ./Files --batch

# Process with custom output directory
python pdf_extractor.py --path file.pdf --output-dir ./output
```

## Requirements

- Python 3.6+
- PyMuPDF (fitz)
- click

## License

MIT License
