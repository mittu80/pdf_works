# PDF Extractor Tool - Enhanced version with header/footer removal
import os
import fitz  # PyMuPDF
import click

def detect_edge_regions(page):
    """
    Automatically detects header and footer regions by analyzing text distribution.
    Uses pattern detection for consistent headers and footers across pages.
    """
    # Skip first page
    if page.number == 0:
        return 0, 0

    blocks = page.get_text("dict")["blocks"]
    page_height = page.rect.height
    page_width = page.rect.width

    # Filter out empty blocks and collect valid text coordinates
    text_positions = []
    for block in blocks:
        if "lines" in block and block.get("lines"):
            text = " ".join([
                span.get("text", "")
                for line in block["lines"]
                for span in line.get("spans", [])
            ]).strip()

            if text:  # Only consider blocks with actual text
                x0, x1 = block["bbox"][0], block["bbox"][2]
                y0, y1 = block["bbox"][1], block["bbox"][3]
                font = None
                font_size = None
                # Get font from first span
                if block["lines"] and block["lines"][0].get("spans"):
                    first_span = block["lines"][0]["spans"][0]
                    font = first_span.get("font", "")
                    font_size = first_span.get("size", 0)
                text_positions.append((x0, x1, y0, y1, text, font, font_size))

    if not text_positions:
        return 0, 0

    # Sort positions by vertical position
    text_positions.sort(key=lambda x: x[2])  # Sort by y0

    # For pages after first, look for consistent header pattern
    if page.number > 0:
        # Only look at blocks in the true header area
        header_max_y = page_height * 0.15  # 15% of page height
        header_candidates = [
            pos for pos in text_positions
            if pos[2] <= header_max_y and not 'copyright' in pos[4].lower()
        ]

        if not header_candidates:
            return 0, 0

        # Find the header blocks
        header_blocks = []
        max_y = 0
        for pos in header_candidates:
            block_text = pos[4].lower()
            # Only include blocks that are definitively part of the header
            if any(marker in block_text for marker in [
                'certified tester',
                'test management',
                'advanced level',
                'software testing qualifications board'
            ]) and not any(skip in block_text for skip in [
                'copyright',
                'notice',
                'revision'
            ]):
                header_blocks.append(pos)
                max_y = max(max_y, pos[3])
            elif header_blocks and pos[2] > max_y + 20:  # If we've moved too far down after finding header blocks
                break

        if header_blocks:
            max_header_y = max(block[3] for block in header_blocks)
            return max_header_y + 2, page_height * 0.15

    # Default header and footer zones
    footer_zone = page_height * 0.85
    potential_footers = []

    # Collect footer blocks
    for pos in text_positions:
        if pos[2] >= footer_zone:  # y0 >= footer_zone
            potential_footers.append(pos)

    # Calculate footer height
    footer_height = 0
    if potential_footers:
        min_footer_y = min(pos[2] for pos in potential_footers)
        footer_height = page_height - min_footer_y + 5

    return 0, footer_height

def get_header_footer_blocks(blocks, header_height, footer_height, page_height, page_number):
    """
    Identifies header and footer blocks using pattern detection.
    Ensures full width coverage for headers and handles split blocks.
    """
    if page_number == 0:  # Skip first page
        return [], []

    header_blocks = []
    footer_blocks = []

    # Skip processing if no header/footer heights are defined
    if header_height == 0 and footer_height == 0:
        return [], []

    # First pass: collect all blocks in header/footer areas
    for block in blocks:
        if "lines" not in block:
            continue

        text = " ".join([
            span.get("text", "")
            for line in block["lines"]
            for span in line.get("spans", [])
        ]).strip()

        if not text:  # Skip empty blocks
            continue

        bbox = block["bbox"]
        y0, y1 = bbox[1], bbox[3]
        x0, x1 = bbox[0], bbox[2]

        # Header detection - any block that touches the header area
        if header_height > 0 and (y0 <= header_height or y1 <= header_height):
            header_blocks.append(block)

        # Footer detection
        elif footer_height > 0 and y0 >= (page_height - footer_height):
            if text.replace(' ', '').isdigit() or y0 >= (page_height - footer_height):
                footer_blocks.append(block)

    return header_blocks, footer_blocks

def pdf_extractor(path, output_path=None):
    """
    Extracts text from a PDF file while removing header and footer blocks
    based on their bounding box positions.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist.")

    with fitz.Document(path) as doc:
        for page in doc:
            header_height, footer_height = detect_edge_regions(page)
            blocks = page.get_text("dict")["blocks"]
            page_height = page.rect.height
            page_width = page.rect.width

            header_blocks, footer_blocks = get_header_footer_blocks(
                blocks, header_height, footer_height, page_height, page.number
            )

            # Create a full-width header redaction if headers were found
            if header_blocks and header_height > 0:
                max_header_y = max(block["bbox"][3] for block in header_blocks)
                header_rect = fitz.Rect(0, 0, page_width, max_header_y)
                page.add_redact_annot(header_rect, fill=(1, 1, 1))

            # Handle footer blocks individually
            for block in footer_blocks:
                bbox = block["bbox"]
                page.add_redact_annot(bbox, fill=(1, 1, 1))

            page.apply_redactions()

        if output_path:
            doc.save(output_path)
            click.echo(f"Redacted PDF saved to: {output_path}")
        else:
            output_path = os.path.splitext(path)[0] + "_redacted.pdf"
            doc.save(output_path)
            click.echo(f"Redacted PDF saved to: {output_path}")

def inspect_pdf_layout(path, page_number=1):  # Changed default to page 2 (index 1)
    """
    Inspects the layout of a specific page in a PDF file.
    Shows meaningful blocks and the last few blocks including footer.
    Default to page 2 (index 1) as we skip the first page.
    """
    with fitz.Document(path) as doc:
        page = doc[page_number]
        page_width = page.rect.width
        page_height = page.rect.height

        header_height, footer_height = detect_edge_regions(page)
        header_area = fitz.Rect(0, 0, page_width, header_height)
        footer_area = fitz.Rect(0, page_height - footer_height, page_width, page_height)

        header_text = page.get_text("text", clip=header_area).strip()
        footer_text = page.get_text("text", clip=footer_area).strip()

        click.echo("\nPage Information:")
        click.echo(f"Dimensions: {page_width:.2f} x {page_height:.2f}")
        click.echo(f"Detected header height: {header_height:.2f}")
        click.echo(f"Detected footer height: {footer_height:.2f}")

        if header_text:
            click.echo(f"\nHeader text found: {header_text}")
        if footer_text:
            click.echo(f"Footer text found: {footer_text}")

        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]

        # Filter out empty blocks
        meaningful_blocks = []
        for block in blocks:
            text = ""
            if "lines" in block:
                text = " ".join([
                    span.get("text", "")
                    for line in block["lines"]
                    for span in line.get("spans", [])
                ]).strip()

            if text:  # Only include blocks with actual text
                meaningful_blocks.append((block, text))

        click.echo(f"\nTotal meaningful blocks: {len(meaningful_blocks)}")

        def print_block_info(i, block, text):
            bbox = block["bbox"]
            distance_from_top = bbox[1]
            distance_from_bottom = page_height - bbox[3]

            if bbox[1] < header_height:
                block_type = "header"
            elif bbox[3] > (page_height - footer_height):
                block_type = "footer"
            else:
                block_type = "content"

            click.echo(f"Block {i} ({block_type}): y0={bbox[1]:.2f}, y1={bbox[3]:.2f} "
                      f"(from top: {distance_from_top:.2f}, from bottom: {distance_from_bottom:.2f}), "
                      f"Text: {text[:60]}")

        # Print first few meaningful blocks
        click.echo("\nFirst blocks:")
        for i, (block, text) in enumerate(meaningful_blocks[:3]):
            print_block_info(i, block, text)

        # Print last few blocks
        if len(meaningful_blocks) > 3:
            click.echo("\nLast blocks:")
            for i, (block, text) in enumerate(meaningful_blocks[-4:], start=len(meaningful_blocks)-4):
                print_block_info(i, block, text)

@click.command()
@click.option('--path', prompt='Path to the PDF file', help='The path to the PDF file or directory to be processed.')
@click.option('--inspect', is_flag=True, help='Inspect layout of the specified page instead of extracting text.')
@click.option('--page', default=1, help='Page number to inspect (0-based index, default is 1 for second page).')
@click.option('--batch', is_flag=True, help='Process all PDF files in the input directory.')
@click.option('--output-dir', default=None, help='Specify output directory for processed files.')
def main(path, inspect, page, batch, output_dir):
    """
    Main entry point for the PDF processing tool.

    Examples:
        # Process a single file
        python pdf_extractor.py --path file.pdf

        # Inspect a file's layout
        python pdf_extractor.py --path file.pdf --inspect --page 2

        # Process all PDFs in a directory
        python pdf_extractor.py --path ./Files --batch

        # Process with custom output directory
        python pdf_extractor.py --path file.pdf --output-dir ./output
    """
    if os.path.isdir(path) and not batch:
        click.echo("Path is a directory. Use --batch to process all PDF files.")
        return

    if batch and os.path.isdir(path):
        pdf_files = [f for f in os.listdir(path) if f.lower().endswith('.pdf')]
        if not pdf_files:
            click.echo("No PDF files found in the directory.")
            return

        for pdf_file in pdf_files:
            full_path = os.path.join(path, pdf_file)
            if output_dir:
                # Modify the output path in pdf_extractor function
                basename = os.path.splitext(os.path.basename(pdf_file))[0]
                output_path = os.path.join(output_dir, f"{basename}_redacted.pdf")
                os.makedirs(output_dir, exist_ok=True)
                if inspect:
                    inspect_pdf_layout(full_path, page)  # Use the specified page
                else:
                    pdf_extractor(full_path, output_path)
            else:
                if inspect:
                    inspect_pdf_layout(full_path, page)  # Use the specified page
                else:
                    pdf_extractor(full_path)
    else:
        if not os.path.exists(path):
            click.echo(f"File not found: {path}")
            return

        if output_dir:
            basename = os.path.splitext(os.path.basename(path))[0]
            output_path = os.path.join(output_dir, f"{basename}_redacted.pdf")
            os.makedirs(output_dir, exist_ok=True)
            if inspect:
                inspect_pdf_layout(path, page)  # Use the specified page
            else:
                pdf_extractor(path, output_path)
        else:
            if inspect:
                inspect_pdf_layout(path, page)  # Use the specified page
            else:
                pdf_extractor(path)

if __name__ == "__main__":
    main()
