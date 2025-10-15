"""
Text Chunker Module
Splits large text into manageable, overlapping chunks for processing.
"""

from typing import List


def split_into_chunks(
    text: str, 
    chunk_size: int = 1000, 
    overlap: int = 200
) -> List[str]:
    """
    Split text into overlapping chunks based on word count.
    
    Args:
        text: The text to split
        chunk_size: Number of words per chunk (default: 1000)
        overlap: Number of words to overlap between chunks (default: 200)
        
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Split text into words
    words = text.split()
    
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        # Get chunk_size words starting from start position
        end = start + chunk_size
        chunk_words = words[start:end]
        
        # Join words back into text
        chunk = ' '.join(chunk_words)
        chunks.append(chunk)
        
        # Move start position forward, accounting for overlap
        start += chunk_size - overlap
        
        # If we're at the end and the last chunk is too small, break
        if end >= len(words):
            break
    
    print(f"Split text into {len(chunks)} chunks (size: {chunk_size} words, overlap: {overlap} words)")
    
    return chunks


def get_chunk_info(chunks: List[str]) -> dict:
    """
    Get information about the chunks.
    
    Args:
        chunks: List of text chunks
        
    Returns:
        Dictionary with chunk statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_words": 0,
            "avg_words_per_chunk": 0
        }
    
    total_words = sum(len(chunk.split()) for chunk in chunks)
    
    return {
        "total_chunks": len(chunks),
        "total_words": total_words,
        "avg_words_per_chunk": total_words // len(chunks)
    }


if __name__ == "__main__":
    # Test the chunker
    test_text = "word " * 5000
    chunks = split_into_chunks(test_text, chunk_size=1000, overlap=200)
    info = get_chunk_info(chunks)
    print(f"Created {info['total_chunks']} chunks with average {info['avg_words_per_chunk']} words each")

