"""
PDF Parser Module - Phase 2
Extracts and cleans text from PDF files with robust error handling,
file size validation, and header/footer removal for AI processing.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2
from tqdm import tqdm


# Maximum file size in bytes (50 MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


def clean_page_text(page_text: str) -> str:
    """
    Clean text extracted from a single PDF page.
    Removes headers, footers, copyright notices, and page numbers.
    
    Args:
        page_text: Raw text from a single page
        
    Returns:
        Cleaned page text
    """
    if not page_text:
        return ""
    
    lines = page_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip header/footer patterns
        if any(pattern in line.lower() for pattern in ['copyright', '©', 'all rights reserved']):
            continue
        
        # Skip page numbers (standalone numbers or "Page X" patterns)
        if re.match(r'^page\s+\d+', line, re.IGNORECASE):
            continue
        if re.match(r'^\d+\s*$', line):
            continue
        
        # Skip common footer patterns
        if re.match(r'^(chapter|section)\s+\d+', line, re.IGNORECASE):
            continue
        
        cleaned_lines.append(line)
    
    # Join lines with spaces
    cleaned_text = ' '.join(cleaned_lines)
    
    # Remove excessive whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Remove special characters that might interfere with processing
    cleaned_text = cleaned_text.replace('\x00', '').replace('\ufeff', '')
    
    return cleaned_text.strip()


def clean_text(text: str) -> str:
    """
    Final cleaning pass on combined text from all pages.
    
    Args:
        text: Combined text from multiple pages
        
    Returns:
        Final cleaned text string
    """
    # Remove excessive line breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Remove excessive spaces
    text = re.sub(r' +', ' ', text)
    
    # Remove any remaining page number patterns
    text = re.sub(r'\bPage \d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
    
    return text.strip()


def extract_text_from_pdf(pdf_path: Path) -> Tuple[str, int]:
    """
    Extract and clean text from a single PDF file with page-by-page processing.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Tuple of (cleaned_text, page_count)
    """
    all_pages_text = []
    page_count = 0
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            
            # Extract and clean each page
            for page in pdf_reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        cleaned_page = clean_page_text(page_text)
                        if cleaned_page:
                            all_pages_text.append(cleaned_page)
                except Exception as e:
                    # Skip problematic pages but continue processing
                    continue
        
        # Combine all pages with double newlines
        combined_text = '\n\n'.join(all_pages_text)
        
        # Final cleaning pass
        final_text = clean_text(combined_text)
        
        return final_text, page_count
                    
    except Exception as e:
        print(f"  [ERROR] Failed to read {pdf_path.name}: {str(e)}")
        return "", 0


def extract_text_from_pdfs(input_dir: str) -> Tuple[str, Dict[str, int]]:
    """
    Parse all PDF files in the specified directory with validation and statistics.
    Implements file size checking, progress tracking, and comprehensive error handling.
    
    Args:
        input_dir: Directory containing PDF files
        
    Returns:
        Tuple of (combined_text, statistics_dict)
        
    Raises:
        FileNotFoundError: If input directory doesn't exist
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")
    
    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"\n[WARNING] No PDF files found in '{input_dir}'")
        return "", {"files_processed": 0, "total_pages": 0, "files_skipped": 0}
    
    print(f"\n[INFO] Found {len(pdf_files)} PDF file(s) to process")
    print("-" * 70)
    
    all_text = []
    total_pages = 0
    files_processed = 0
    files_skipped = 0
    
    # Process each PDF with progress bar
    for idx, pdf_path in enumerate(tqdm(pdf_files, desc="Reading PDFs", unit="file"), 1):
        # Check file size
        file_size = pdf_path.stat().st_size
        
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            print(f"\n[WARNING] Skipping {pdf_path.name} - File too large ({size_mb:.1f} MB > 50 MB limit)")
            files_skipped += 1
            continue
        
        # Extract text from PDF
        text, page_count = extract_text_from_pdf(pdf_path)
        
        if text:
            all_text.append(text)
            total_pages += page_count
            files_processed += 1
        else:
            files_skipped += 1
    
    print("\n" + "-" * 70)
    
    # Combine all text
    combined_text = "\n\n".join(all_text)
    
    # Prepare statistics
    stats = {
        "files_processed": files_processed,
        "files_skipped": files_skipped,
        "total_files": len(pdf_files),
        "total_pages": total_pages,
        "total_characters": len(combined_text),
        "total_words": len(combined_text.split())
    }
    
    # Print summary
    print(f"[SUCCESS] Text extraction complete")
    print(f"  Files processed: {files_processed}/{len(pdf_files)}")
    if files_skipped > 0:
        print(f"  Files skipped: {files_skipped}")
    print(f"  Total pages: {total_pages:,}")
    print(f"  Total characters: {len(combined_text):,}")
    print(f"  Total words: {stats['total_words']:,}")
    
    return combined_text, stats


# Alias for backward compatibility
def parse_books(input_dir: str) -> str:
    """
    Legacy function - calls extract_text_from_pdfs and returns only text.
    For backward compatibility with existing code.
    
    Args:
        input_dir: Directory containing PDF files
        
    Returns:
        Combined text from all PDF files
    """
    text, _ = extract_text_from_pdfs(input_dir)
    return text


if __name__ == "__main__":
    # Test the parser
    test_text = parse_books("../books")
    print(f"Extracted {len(test_text)} characters")

