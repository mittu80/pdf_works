# import fitz  # PyMuPDF
import os
import pathlib

import fitz
import pymupdf
from dotenv import load_dotenv
import pymupdf4llm
from langchain.text_splitter import MarkdownTextSplitter


def pdf_extractor(path, num_blocks_to_remove=0):
    # ask user and verify if the file exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist.")


    doc =fitz.open(path)
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks[:num_blocks_to_remove]:
            bbox = block["bbox"]
            y0, y1 = bbox[1], bbox[3]
            # remove header and footer
            if y0 < 80 or y1 > page.rect.height - 80:
                page.add_redact_annot(bbox, fill=(1, 1, 1))
            # if y1 < 50:
            #     page.add_redact_annot(bbox, fill=(1, 1, 1))
            # # remove footer
            # elif y0 > page.rect.height - 50:
            #     page.add_redact_annot(bbox, fill=(1, 1, 1))
        page.apply_redactions()

    doc.save('Files/CTAL_TM_2012_Syllabus_v2.0_redacted.pdf')



    # Open the PDF file
    # md_read = pymupdf4llm.LlamaMarkdownReader()
    # data = md_read.load_data(path)
    content= []
    # result 'data' is a list of pages containing meta data
    # and text content
    # print the text content of each page
    # md_text = pymupdf4llm.to_markdown(path)
    # splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=0)
    # splitter.create_documents([md_text])
    # for page in data:
        # print(type(page))
        # print(page.metadata['title'])
        # print(page.metadata['author'])
        # print(page.metadata['footer'])
        # # Entferne Header und Footer
        # print(f'processing page {page.metadata[""]}')
        # page.text = page.text.replace(page.metadata['header'], '')
        # page.text = page.text.replace(page.metadata['footer'], '')
        # print(page.text)
        # print(f"title is: {page.meta['title']}")
        # print(f"Number of Pages is: {page.meta['number_of_pages']}")
        # # PDFWriter erwartet PDF-Seiten, nicht Text!
        # pdf_writer = PdfWriter()
        # pdf_writer.add_page(page['text'])
        # # Save the extracted text to a new PDF file
        # output_path = os.path.splitext(path)[0] + "_extracted.pdf"
        # pdf_writer.write(output_path)
        # print(f"Extracted text saved to {output_path}")


def inspect_pdf_layout(path, page_number=0):
    # Open the PDF file
    doc = fitz.open(path)
    page = doc[page_number]
    blocks = page.get_text("dict")["blocks"]

    for i, block in enumerate(blocks):
        bbox = block["bbox"]
        text = "".join([line["spans"][0]["text"] for line in block["lines"] if line["spans"]])
        print(f"Block {i}: y0={bbox[1]:.2f}, y1={bbox[3]:.2f}, Text: {text[:60]}")
if __name__ == "__main__":
    # C:\\Users\\a941498\\Downloads\\CTAL_TM_2012_Syllabus_v2.0.pdf
    # user prompt to enter the path to the PDF file
    # pdf_file_path = input("Enter the path to the PDF file: ")
    # if pdf_file_path:
    #     pdf_extractor(pdf_file_path)
    # else:
    #     print("No file path provided. Exiting.")
    #     exit(1)
    # inspect_pdf_layout('Files/CTAL_TM_2012_Syllabus_v2.0.pdf')
    pdf_extractor('Files/CTAL_TM_2012_Syllabus_v2.0.pdf', num_blocks_to_remove=10)