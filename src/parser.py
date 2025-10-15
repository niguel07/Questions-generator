"""
PDF Parser Module
Extracts and cleans text from PDF files in a specified directory.
"""

import os
import re
from pathlib import Path
from typing import List
import PyPDF2
from tqdm import tqdm


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text by removing headers, footers, and extra whitespace.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Cleaned text string
    """
    # Remove excessive whitespace and newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove common header/footer patterns (page numbers, etc.)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'Page \d+', '', text, flags=re.IGNORECASE)
    
    # Remove special characters that might interfere
    text = text.replace('\x00', '')
    
    return text.strip()


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from a single PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    text = ""
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
    except Exception as e:
        print(f"Error reading {pdf_path.name}: {str(e)}")
        return ""
    
    return clean_text(text)


def parse_books(input_dir: str) -> str:
    """
    Parse all PDF files in the specified directory and return combined text.
    
    Args:
        input_dir: Directory containing PDF files
        
    Returns:
        Combined text from all PDF files
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")
    
    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"Warning: No PDF files found in '{input_dir}'")
        return ""
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    all_text = []
    
    # Process each PDF with progress bar
    for pdf_path in tqdm(pdf_files, desc="Parsing PDFs"):
        text = extract_text_from_pdf(pdf_path)
        if text:
            all_text.append(text)
    
    combined_text = "\n\n".join(all_text)
    
    print(f"Total text extracted: {len(combined_text):,} characters")
    
    return combined_text


if __name__ == "__main__":
    # Test the parser
    test_text = parse_books("../books")
    print(f"Extracted {len(test_text)} characters")

