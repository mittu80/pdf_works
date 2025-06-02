# PDF Works

A Python tool for processing PDF files, with features including:
- Text extraction
- Header and footer removal
- PDF layout inspection

## Requirements

- Python 3.x
- PyMuPDF (fitz)
- click

## Installation

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

To inspect PDF layout:
```bash
python -m pdf_extractor --path "path/to/your.pdf" --inspect
```

To remove headers/footers:
```bash
python -m pdf_extractor --path "path/to/your.pdf" --num-blocks 10
```

## Features

- PDF Layout Inspection: Analyze the structure of PDF documents
- Header/Footer Removal: Clean up PDFs by removing unwanted headers and footers
- Text Block Analysis: View detailed information about text blocks in PDFs

