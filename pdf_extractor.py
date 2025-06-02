import os
import fitz  # PyMuPDF
import click

def pdf_extractor(path, num_blocks_to_remove=0):
    """
    Extracts text from a PDF file while removing specified blocks
    (headers and footers) based on their bounding box positions.

    Parameters:
    - path: str : path to the PDF file
    - num_blocks_to_remove: int : number of blocks to remove from each page
    """
    # Verify if the file exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist.")

    with fitz.Document(path) as doc:  # Using with statement for proper cleanup
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks[:num_blocks_to_remove]:
                bbox = block["bbox"]
                y0, y1 = bbox[1], bbox[3]
                # Remove header and footer
                if y0 < 80 or y1 > page.rect.height - 80:
                    page.add_redact_annot(bbox, fill=(1, 1, 1))
            page.apply_redactions()

        output_path = os.path.splitext(path)[0] + "_redacted.pdf"
        doc.save(output_path)
        click.echo(f"Redacted PDF saved to: {output_path}")

def inspect_pdf_layout(path, page_number=0):
    """
    Inspects the layout of a specific page in a PDF file.

    Parameters:
    - path: str : path to the PDF file
    - page_number: int : page number to inspect
    """
    with fitz.Document(path) as doc:
        page = doc[page_number]
        blocks = page.get_text("dict")["blocks"]

        for i, block in enumerate(blocks):
            bbox = block["bbox"]
            # More robust text extraction
            try:
                if "lines" in block:
                    text = " ".join([
                        span.get("text", "")
                        for line in block["lines"]
                        for span in line.get("spans", [])
                    ])
                else:
                    text = block.get("text", "")
            except Exception:
                text = "<unreadable text>"

            click.echo(f"Block {i}: y0={bbox[1]:.2f}, y1={bbox[3]:.2f}, Text: {text[:60]}")


@click.command()
@click.option('--path', prompt='Path to the PDF file', help='The path to the PDF file to be processed.')
@click.option('--num-blocks', default=0, help='Number of blocks to remove from each page (headers/footers).')
@click.option('--inspect', is_flag=True, help='Inspect layout of the first page instead of extracting text.')
def main(path, num_blocks, inspect):
    """
    Main entry point for the PDF processing tool.

    This tool allows you to extract text from a PDF file while removing specified blocks,
    such as headers and footers. You can also inspect the layout of the first page of a PDF.

    Parameters:
    - path: str : The path to the PDF file to be processed.
    - num_blocks: int : Number of blocks to remove from each page (headers/footers).
    - inspect: bool : If set, inspect the layout of the first page instead of extracting text.
    """
    if inspect:
        inspect_pdf_layout(path)
    else:
        pdf_extractor(path, num_blocks)

if __name__ == "__main__":
    main()

