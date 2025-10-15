"""
Text Chunker Module - Phase 2
Splits large text into manageable, overlapping chunks optimized for Claude API processing.
Ensures sentence continuity with word-level overlap.
"""

from typing import List, Dict


def chunk_text(
    text: str, 
    chunk_size: int = 1000, 
    overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks based on word count.
    Creates ~1000-word chunks with ~100-word overlap to maintain context continuity.
    Optimized for Claude API processing.
    
    Args:
        text: The text to split into chunks
        chunk_size: Target number of words per chunk (default: 1000)
        overlap: Number of words to overlap between consecutive chunks (default: 100)
        
    Returns:
        List of text chunks ready for AI processing
        
    Example:
        >>> text = "word " * 5000
        >>> chunks = chunk_text(text, chunk_size=1000, overlap=100)
        >>> len(chunks)
        6
    """
    # Handle empty or invalid input
    if not text or not text.strip():
        print("[WARNING] Empty text provided to chunker")
        return []
    
    # Validate overlap is less than chunk size
    if overlap >= chunk_size:
        print(f"[WARNING] Overlap ({overlap}) should be less than chunk_size ({chunk_size})")
        overlap = chunk_size // 4  # Set to 25% of chunk size
    
    # Split text into words
    words = text.split()
    total_words = len(words)
    
    # If text is smaller than one chunk, return as single chunk
    if total_words <= chunk_size:
        print(f"[INFO] Text is small ({total_words} words), returning as single chunk")
        return [text]
    
    chunks = []
    start = 0
    chunk_num = 0
    
    while start < total_words:
        # Calculate end position for this chunk
        end = min(start + chunk_size, total_words)
        
        # Extract words for this chunk
        chunk_words = words[start:end]
        
        # Join words back into text
        chunk = ' '.join(chunk_words)
        chunks.append(chunk)
        
        chunk_num += 1
        
        # Move start position forward, accounting for overlap
        # This ensures continuity between chunks
        start += chunk_size - overlap
        
        # If we've reached the end, stop
        if end >= total_words:
            break
    
    # Print summary
    print(f"\n[SUCCESS] Text chunking complete")
    print(f"  Total chunks created: {len(chunks)}")
    print(f"  Chunk size: {chunk_size} words")
    print(f"  Overlap: {overlap} words")
    print(f"  Source text: {total_words:,} words")
    
    return chunks


# Alias for backward compatibility
def split_into_chunks(
    text: str, 
    chunk_size: int = 1000, 
    overlap: int = 200
) -> List[str]:
    """
    Legacy function - calls chunk_text.
    For backward compatibility with existing code.
    
    Args:
        text: The text to split
        chunk_size: Number of words per chunk (default: 1000)
        overlap: Number of words to overlap between chunks (default: 200)
        
    Returns:
        List of text chunks
    """
    return chunk_text(text, chunk_size, overlap)


def get_chunk_info(chunks: List[str]) -> Dict[str, int]:
    """
    Get detailed statistics about text chunks.
    
    Args:
        chunks: List of text chunks
        
    Returns:
        Dictionary with comprehensive chunk statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_words": 0,
            "total_characters": 0,
            "avg_words_per_chunk": 0,
            "min_words": 0,
            "max_words": 0
        }
    
    word_counts = [len(chunk.split()) for chunk in chunks]
    total_words = sum(word_counts)
    total_characters = sum(len(chunk) for chunk in chunks)
    
    return {
        "total_chunks": len(chunks),
        "total_words": total_words,
        "total_characters": total_characters,
        "avg_words_per_chunk": total_words // len(chunks) if chunks else 0,
        "min_words": min(word_counts) if word_counts else 0,
        "max_words": max(word_counts) if word_counts else 0
    }


def print_chunk_summary(chunks: List[str]) -> None:
    """
    Print a detailed summary of chunk statistics.
    Useful for debugging and monitoring the chunking process.
    
    Args:
        chunks: List of text chunks
    """
    if not chunks:
        print("[WARNING] No chunks to summarize")
        return
    
    info = get_chunk_info(chunks)
    
    print("\n" + "=" * 70)
    print("CHUNK SUMMARY")
    print("=" * 70)
    print(f"Total chunks: {info['total_chunks']}")
    print(f"Total words: {info['total_words']:,}")
    print(f"Total characters: {info['total_characters']:,}")
    print(f"Average words per chunk: {info['avg_words_per_chunk']:,}")
    print(f"Minimum words in chunk: {info['min_words']:,}")
    print(f"Maximum words in chunk: {info['max_words']:,}")
    print("=" * 70)


if __name__ == "__main__":
    # Test the chunker
    test_text = "word " * 5000
    chunks = split_into_chunks(test_text, chunk_size=1000, overlap=200)
    info = get_chunk_info(chunks)
    print(f"Created {info['total_chunks']} chunks with average {info['avg_words_per_chunk']} words each")

