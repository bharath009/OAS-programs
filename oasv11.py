#!/usr/bin/env python3

import sys

# Add the system path directories to the sys.path list
sys.path.extend([
    '/opt/homebrew/Cellar/python@3.12/3.12.2_1/Frameworks/Python.framework/Versions/3.12/lib/python312.zip',
    '/opt/homebrew/Cellar/python@3.12/3.12.2_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12',
    '/opt/homebrew/Cellar/python@3.12/3.12.2_1/Frameworks/Python.framework/Versions/3.12/lib/python3.12/lib-dynload',
    '/opt/homebrew/lib/python3.12/site-packages',
    '/opt/homebrew/opt/python-tk@3.12/libexec'
])

#!/usr/bin/env python3

import pytesseract
import re
import os
import glob
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from pyzbar.pyzbar import decode
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from tkinter import filedialog
from tkinter import *
from multiprocessing import Pool
from datetime import datetime

# Function to select a directory

def select_directory():
    root = Tk()
    root.withdraw()  # Hide the main window
    last_directory = read_last_directory()  # Read the last used directory
    directory = filedialog.askdirectory(initialdir=last_directory, title="Select Directory")
    root.destroy()  # Close the Tkinter window
    if directory:
        save_last_directory(directory)  # Save the current directory for future use
    return directory

# Function to read the last used directory from a file

def read_last_directory():
    last_directory_file = "last_directory.txt"
    if os.path.exists(last_directory_file):
        with open(last_directory_file, "r") as file:
            last_directory = file.readline().strip()
        return last_directory
    return ""

# Function to save the current directory to a file

def save_last_directory(directory):
    last_directory_file = "last_directory.txt"
    with open(last_directory_file, "w") as file:
        file.write(directory)
        

def extract_raw_student_name(raw_text):
        name_pattern = re.compile(r'Student:\s*(.*)')
        consecutive_words_pattern = re.compile(r'\b[A-Z][a-z]*\s+[A-Z][a-z]*\b')
    
            # Search the text for the patterns
        name_match = name_pattern.search(raw_text)
        consecutive_words_match = consecutive_words_pattern.search(raw_text)
    
            # If a pattern was found, process the result
        if name_match:
            student_info = name_match.group(1).replace('“', '"').replace('”', '"')
            student_name = re.sub(r'"[^"]*"', '', student_info).strip()
            student_name = re.sub(r'\W+', ' ', student_name)
            words = student_name.split()
            
            if len(words) >= 2 and all(word[0].isupper() for word in words[:2]) and not any(char.isdigit() for char in words[0] + words[1]):
                name = " ".join(words[:2])
                return name
            
            else:
                first_occurrence_index = raw_text.find("Student:")
                second_occurrence_match = re.search(r'Student:.*', raw_text[first_occurrence_index + 1:])
                
                if second_occurrence_match:
                    second_occurrence_index = second_occurrence_match.start() + first_occurrence_index + 1
                else:
                    second_occurrence_index = None
                    
                if second_occurrence_index is not None:
                    student_index = second_occurrence_index
                else:
                    student_index = first_occurrence_index
                    
                    student_info = raw_text[student_index:]
                    matchstu = re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+', student_info)
                    
                    if matchstu:
                        captured_words = matchstu.group()
                        return captured_words
                    else:
                        return None
                    
        else:
            return None

# Function to extract Student Name
        
def extract_student_name(text,raw_text):
    # Define the regular expression pattern to capture exactly two consecutive names together
    pattern = r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b'
    
    # Find all matches of first name and last name together
    matches = re.findall(pattern, text)
    
    if(matches):
    # Assuming there's only one match, which contains both first and last names
        full_name = matches[0]
        return full_name
    
    return extract_raw_student_name(raw_text)

    

def crop_text(text,delimiter):
    
    parts = text.split(delimiter, 1)

    text = parts[0]
    
    return text
    

# Preprocess the text to remove the descripencies

def preprocess_text(text, words_to_remove=None):
    # Split the text by the specified delimiter
    
    # Define words to remove (if any)
    words_to_remove = ['TEST', 'steps', 'least', 'included', 'Have', 'number', 'Pronoun', 'Portal', 'have', 'please', 'Email', 'Identification', 'Check', 'Accommodation', 'administered', 'https', 'Periodic', 'above', 'Class', 'like', 'Information', 'returned', 'secure', 'them', 'Sign', 'Please',  'Name', 'questions', 'may', 'Step', 'should', 'Exams', 'Approved', 'testing', 'phone', 'scanned', 'what', 'other', 'Accessibility', 'Drop', 'Time', 'specify', 'On', 'Handing','list', 'Testing', 'Form', 'needed',  'Services', 'Upload', 'related',  'alternate', 'covered', 'hours', 'What', 'clarification', 'late', 'date',  'cell',  'instructions', 'reason', 'here', 'Course', 'would', 'Paper', 'Proctor', 'unable', 'Notes',  'reminder', 'take', 'access', 'upload',   'applicable',  'Instruction', 'Specified', 'Table', 'herself', 'quizzes', 'deducted',  'accessiblelearning',   'test',  'copy', 'Center', 'time', 'call', 'Procedures', 'disability', 'Actual',  'materials', 'from', 'Received', 'receive', 'during',  'testingcenter', 'Location', 'Exam', 'specific', 'allowed', 'Instructor', 'email', 'below', 'Extended','Print',  'Alternative', 'advance',  'From', 'Note', 'Office', 'address', 'Before', 'will', 'Individual', 'your', 'Detail','Student','Instructions','Panama','City','Accessibility','Files','Uploaded','Files Uploaded']
    
    # Combine all regular expressions into one pattern
    pattern = r'\b(' + '|'.join(words_to_remove) + r')\b|\b\d{1,2}:\d{2}\s*(?:AM|PM)\b|\b\d{1,2}/\d{1,2}/\d{2}\b|[^\w\s.]'
    
    # Use the re.sub() function to replace the matched patterns with an empty string
    text = re.sub(pattern, '', text)
    
    return text

# Extract the Course code from Raw text(not preprocessed)

def extract_raw_course_code(raw_text):
    course_pattern = r'Course:\s([A-Z]{3}\s\d{4}[A-Z]?)'
    course_code = re.search(course_pattern, raw_text)
    if course_code:
        #print("Course code:", course_code.group(1))
        return course_code.group(1)
    else:
        #print("Course code not found.")
        return None

# Extract the Course code from preprocessed text
    
def extract_course_code(processed_text,raw_text):
    course_pattern = r'\b[A-Z]{3}\b'
    numeric_pattern = r'(?<=\b)\d{4,5}(?=\.)'
    course_matches = re.findall(course_pattern, processed_text)
    course_matches = [word for word in course_matches if len(word) == 3]
    numerics = re.findall(numeric_pattern, processed_text)
    if course_matches and numerics:
        course_name = course_matches[0] + " " + numerics[0]
        #print("Course:", course_name)
        return course_name
    else:
        return extract_raw_course_code(raw_text)
        
def process_qr_code(decoded_objects, processed_text,raw_text):
    if decoded_objects:
        qr_code_data = decoded_objects[0].data.decode("utf-8")
        parsed_url = urlparse(qr_code_data)
        if parsed_url.scheme and parsed_url.netloc:
            try:
                response = requests.get(qr_code_data)
                root = ET.fromstring(response.content)
                subject = root.find('Subject').text
                course = root.find('Course').text
                class_course = subject + " " + course
                #print("Class from URL:", class_course)
                return class_course
            except requests.exceptions.RequestException as e:
                print("Error:", e)
        else:
            print("QR code does not contain a valid URL:", qr_code_data)
    else:
    #    print("No QR code found ")
        
        return extract_course_code(processed_text,raw_text)

def remove_first_two_pages(pdf_path, new_file_path):
    
    pdf = PdfReader(pdf_path)
    writer = PdfWriter()
    
    for page_num in range(2, len(pdf.pages)):
        page = pdf.pages[page_num]
        writer.add_page(page)
        
    with open(new_file_path, "wb") as output_pdf:
        writer.write(output_pdf)

def rename_pdf(pdf_path, student_name, class_name):
    
    date_str = datetime.now().strftime('%Y_%m_%d')
    success = False
    new_file_name = ""
    
    if student_name and class_name:
        # Create new file name
        new_file_name = f"{student_name} {class_name} {date_str.replace(' ', '').replace(':', '').replace('/', '')}.pdf"
        
        new_file_path = os.path.join(os.path.dirname(pdf_path), new_file_name)
        
        try:
            # Remove the first two pages of the PDF
            remove_first_two_pages(pdf_path, new_file_path)
            #print(f"{os.path.basename(pdf_path)} renamed to {new_file_name}")
            success = True
        except Exception as e:
            print(f"Failed to process {pdf_path}: {str(e)}")
    
        
    return success, os.path.basename(pdf_path), new_file_name

# Rest of your imports and functions remain unchanged...

def process_pdf(pdf_file, directory):  # Add directory as an argument
    pdf_path = os.path.join(directory, pdf_file)
    images = convert_from_path(pdf_path)
    with images[0] as img:
        decoded_objects = decode(img)
        text = pytesseract.image_to_string(img)
        raw_text=preprocess_text(text)
        processed_text = crop_text(raw_text,'fsu')
        student_name = extract_student_name(processed_text,raw_text)
        class_name = process_qr_code(decoded_objects, processed_text, raw_text)
        success, old_file_name, new_file_name = rename_pdf(pdf_path, student_name, class_name)
        if success:
            return (old_file_name, new_file_name)
        else:
            return (pdf_file, None)  # Return original filename and None for failed files

def rename_required_files(failed_files, directory):
    renamed_files = []  # List to store the names of the renamed files
    renamed_file_paths = []  # List to store the paths of the renamed files
    old_filenames = []  # List to store the original filenames before renaming
    
    for file_name in failed_files:
        if re.match(r'\d', file_name):  # Check if the filename starts with a numerical value
            original_path = os.path.join(directory, file_name)
            directory_path, original_file_name = os.path.split(original_path)  # Store the original filename
            file_name_without_extension, extension = os.path.splitext(original_file_name)
            current_date = datetime.now().strftime("%Y_%m_%d")
            new_file_name = f"Rename_Required_{file_name_without_extension}_{current_date}{extension}"
            new_file_path = os.path.join(directory_path, new_file_name)
            remove_first_two_pages(original_path, new_file_path)
            # Store both old and new filenames
            renamed_files.append(new_file_name)
            renamed_file_paths.append(new_file_path)
            old_filenames.append(original_file_name)
        
    return old_filenames, renamed_files, renamed_file_paths


def main():
    directory = select_directory()  # Select a directory
    if not directory:
        print("No directory selected. Exiting.")
        return
    
    # Get list of PDF files
    pdf_files = [file for file in os.listdir(directory) if file.endswith(".pdf")]
    
    successful_files = []
    failed_files = []
    failed_file_paths=[]
    
    # Use multiprocessing Pool
    with Pool() as pool:
        # Pass directory as an additional argument to process_pdf
        results = pool.starmap(process_pdf, [(pdf_file, directory) for pdf_file in pdf_files])
        
    for result in results:
        if result[1] is not None:  # Check if rename_pdf succeeded (result[1] is not None)
            successful_files.append(result)
        else:
            failed_files.append(result[0])  # Append the original filename to failed_files
            
    # Print results
    
    old_filenames, renamed_files, _ = rename_required_files(failed_files, directory)
    count_success = 0
    count_renames=0

    total_files_processed = len(successful_files) + len(failed_files)
    print(f"Total files processed: {total_files_processed}\n")
    
    for idx, (old_name, new_name) in enumerate(successful_files, start=1):
        if new_name not in failed_files:  # Check if the new filename is not in the list of failed files
            count_success += 1  # Increment the counter
            #print(f"{count_success}. {old_name} renamed to {new_name}")
    
    for (old_name, new_name) in zip(old_filenames, renamed_files):
        if new_name not in failed_files:  # Check if the new filename is not in the list of failed files
            count_renames += 1
            
    if (count_success>0):
        
        print(f"Successful files: "+str(count_success+count_renames)+"\n")
        print("Rename Successful on: " +str(count_success) +"\n")
        
        serial_success=0
        for (old_name, new_name) in successful_files:
            if new_name not in failed_files:  # Check if the new filename is not in the list of failed files
                serial_success +=1  # Increment the counter
                print(f"{serial_success}. {old_name} renamed to {new_name}")
    
    else:
        
        print("No new files found for renaming\n")
    
        
    if(count_renames>0):
        serial_rename=0
        print("\nManual Rename Required: "+str(count_renames)+"\n")
        
        for (old_name, new_name) in zip(old_filenames, renamed_files):
            if new_name not in failed_files:
                serial_rename +=1# Check if the new filename is not in the list of failed files
                print(f"{serial_rename}. {old_name} renamed to {new_name}")
    else:
        print("\nNo files found for manual rename")
    
    if(len(failed_files)-len(renamed_files)>0):
        #print(f"\nTotal Failed files: {len(failed_files)-len(renamed_files)}\n")
        #print("\nList of Already Processed files: "+str(len(failed_files)-len(renamed_files))+"\n")
        
        print("\nList of Already Processed files: "+str(len(failed_files)+len(successful_files)-count_success-count_renames)+"\n")
    
        non_numeric_failed_files = [file_name for file_name in failed_files if not file_name[0].isdigit()]
    
        next_idx_old_name = 1
        next_idx_file_name = 2
        
        for file_name in non_numeric_failed_files:
            # Check if the filename matches any new filename from successful files
            for old_name, new_name in successful_files:
                if new_name == file_name:
                    print(f"{next_idx_old_name}. {old_name} ----->>>> {next_idx_file_name}. {file_name}")
                    next_idx_old_name += 2
                    next_idx_file_name += 2
                    break
                
        for file_name in non_numeric_failed_files:
            # Check if the filename matches any new filename from successful files
            for old_name, new_name in zip(old_filenames, renamed_files):
                if new_name == file_name:
                    print(f"{next_idx_old_name}. {old_name} ----->>>> {next_idx_file_name}. {file_name}")
                    next_idx_old_name += 2
                    next_idx_file_name += 2
                    break
    else:
        print("\nNo files failed")
                            
if __name__ == "__main__":
    main()