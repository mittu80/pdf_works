# PDF Works

A Python tool for processing PDF files, with features including:
- Text extraction
- Header and footer removal
- PDF layout inspection

## Installation

```bash
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
