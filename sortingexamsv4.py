import re
import PyPDF2
from tkinter import Tk, filedialog
import os

def select_pdf_file():
    root = Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
    root.destroy()  # Close the Tkinter window
    return file_path

def extract_text_from_page(page):
    return page.extract_text()

def extract_student_info(text, page_num):
    
    student_info = {}
    
    # Extract the student name
    name_pattern = r'Student:\s*(.*)'
    student_name = re.search(name_pattern, text, re.IGNORECASE)
    
    if student_name:
        # Remove extra spaces within words
        name = student_name.group(1).strip()
        name = re.sub(r"([A-Z])\s([a-z])", r"\1\2", name)
        
        # Split the name into words
        words = name.split()
        
        # Reverse the first and last words
        if len(words) > 1:
            words[0], words[-1] = words[-1], words[0]
            
        # Join the words back into a string
        name = ' '.join(words)
        
        student_info['Name'] = name
    else:
        return None
    
    
        
    # Extract the date
    date_pattern = r'Date & T ime:(\d{2}/\d{2}/\d{4})'
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    if date_match:
        student_info['Date'] = date_match.group(1)
    else:
        return None
        
    # Extract the time
    
    # Check if there are at least two matches
            
    time_pattern = r"\b\d{1,2}:\d{2} [AP]M\b"
    time_match = re.findall(time_pattern, text)
    print(time_match)
    
    if len(time_match) >= 2:
        # Extract the second match
        time_value = time_match[1]
    else:
        print("Time not found")
        
    if time_value:
        student_info['Time'] = time_value
    else:
        return None
        
    student_info['Page'] = page_num
    return student_info

pdf_path = select_pdf_file()
if pdf_path:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        student_info_list = [] # List to store student info dictionaries
        serial_number = 1
        time_values = []  # List to store time values
        combined_pdf = PyPDF2.PdfWriter()  # Create a writer object for combined PDF
        remaining_pdf = PyPDF2.PdfWriter()  # Create a writer object for remaining pages

        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = extract_text_from_page(page)
            text = re.sub(r"Location: Not Specified.*?No$", "", text, flags=re.DOTALL)
            student_info = extract_student_info(text, page_num+1)
            if student_info:  # Check if student_info is not None
                student_info['Serial'] = serial_number
                student_info_list.append(student_info)
                serial_number += 1
                if 'Time' in student_info and student_info['Time'] not in time_values:
                    time_values.append(student_info['Time'])
            else:
                remaining_pdf.add_page(page)

        for student_info in student_info_list:
            print(f"Serial: {student_info['Serial']}, Name: {student_info['Name']}, Date: {student_info['Date']}, Time: {student_info['Time']}, Page: {student_info['Page']}")
        
        num=1

        for time_value in time_values:
            print(f"\nStudents with Time {time_value}:")
            # Filter students based on time value and sort by name
            sorted_students = sorted([student_info for student_info in student_info_list if student_info['Time'] == time_value], key=lambda x: x['Name'])
            
            for student_info in sorted_students:
                print(f" Sorted Page: {num},Actual Page: {student_info['Page']} Serial: {student_info['Serial'] }Name: {student_info['Name']} ")
                num+=1
                # Add pages referenced in the final list to the combined PDF
                combined_pdf.add_page(reader.pages[student_info['Page']-1])  # Adjust page number (0-indexed) to match PDF reader's convention
        

        # Get the directory path of the input PDF file
        input_dir = os.path.dirname(pdf_path)
        # Write the combined PDF to a file in the same directory
        combined_file_path = os.path.join(input_dir, "Combined_PDF.pdf")
        with open(combined_file_path, "wb") as combined_file:
            combined_pdf.write(combined_file)

        print(f"\nCombined PDF '{combined_file_path}' created with pages referenced in the final list.")

        # Write the remaining pages to a new PDF file
        remaining_file_path = os.path.join(input_dir, "Remaining_Pages.pdf")
        with open(remaining_file_path, "wb") as remaining_file:
            remaining_pdf.write(remaining_file)

        print(f"\nRemaining PDF '{remaining_file_path}' created with pages not included in the final list.")
        