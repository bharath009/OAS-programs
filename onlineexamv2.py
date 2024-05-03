import sys
import PyPDF2
import tkinter as tk
from tkinter import filedialog
import os


def extract_pages_with_keywordonline(pdf_reader, keyword):
    pages_with_keyword = []
    
    for page_num in range(len(pdf_reader.pages)):
        page_text = pdf_reader.pages[page_num].extract_text()
        if keyword in page_text.lower():
            pages_with_keyword.append(page_num)
            
    return pages_with_keyword
def extract_pages_with_keyword(pdf_reader, keyword):
    pages_with_keyword = []
    
    for page_num in range(len(pdf_reader.pages)):
        page_text = pdf_reader.pages[page_num].extract_text()
        if keyword in page_text:
            pages_with_keyword.append(page_num)
            
    return pages_with_keyword

def select_pdf_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return file_path

def main():
    # Select PDF file using file dialog
    input_pdf_path = select_pdf_file()
    
    if not input_pdf_path:
        print("No file selected. Exiting.")
        return
    
    # Get the directory and filename of the input PDF file
    input_directory = os.path.dirname(input_pdf_path)
    input_filename = os.path.basename(input_pdf_path)
    
    # Open the PDF file
    with open(input_pdf_path, 'rb') as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        
        # Identifier to search for in the PDF
        identifier = 'Office of Accessibility Services'

        # Extract pages containing the identifier
        pages_containing_identifier = extract_pages_with_keyword(pdf_reader, identifier)
        
        if pages_containing_identifier:
            # Create a new PDF with only the pages containing the identifier
            output_pdf_path_with_identifier = os.path.join(input_directory, 'ExamInstructions.pdf')
            with open(output_pdf_path_with_identifier, 'wb') as output_pdf_file_with_identifier:
                pdf_writer_with_identifier = PyPDF2.PdfWriter()
                for page_num in pages_containing_identifier:
                    pdf_writer_with_identifier.add_page(pdf_reader.pages[page_num])
                pdf_writer_with_identifier.write(output_pdf_file_with_identifier)
                
            print(f"A new PDF with only pages containing '{identifier}' has been created at '{output_pdf_path_with_identifier}'.")

            # Process the newly created PDF
            process_pdf(output_pdf_path_with_identifier)
        else:
            print(f"No pages containing '{identifier}' were found in the PDF. No new PDF created.")

def process_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        
        # Identifier to search for in the PDF
        identifier = 'online exam/test'
        
        # Extract pages containing the identifier
        pages_containing_identifier = extract_pages_with_keywordonline(pdf_reader, identifier)
        
        if pages_containing_identifier:
            # Create a new PDF without the pages containing the identifier
            output_pdf_path_without_identifier = pdf_path.replace('ExamInstructions.pdf', 'Paper Exams.pdf')
            with open(output_pdf_path_without_identifier, 'wb') as output_pdf_file_without_identifier:
                pdf_writer_without_identifier = PyPDF2.PdfWriter()
                for page_num in range(len(pdf_reader.pages)):
                    if page_num not in pages_containing_identifier:
                        pdf_writer_without_identifier.add_page(pdf_reader.pages[page_num])
                pdf_writer_without_identifier.write(output_pdf_file_without_identifier)
                
            print(f"A new PDF without pages containing '{identifier}' has been created at '{output_pdf_path_without_identifier}'.")
            
            # Create a new PDF with only the pages containing the identifier
            output_pdf_path_with_identifier = pdf_path.replace('ExamInstructions.pdf', 'Online Exams.pdf')
            with open(output_pdf_path_with_identifier, 'wb') as output_pdf_file_with_identifier:
                pdf_writer_with_identifier = PyPDF2.PdfWriter()
                for page_num in pages_containing_identifier:
                    pdf_writer_with_identifier.add_page(pdf_reader.pages[page_num])
                pdf_writer_with_identifier.write(output_pdf_file_with_identifier)
                
            print(f"A new PDF with only pages containing '{identifier}' has been created at '{output_pdf_path_with_identifier}'.")
        else:
            print(f"No pages containing '{identifier}' were found in the PDF. No new PDFs created.")

if __name__ == "__main__":
    main()
    