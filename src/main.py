"""
Question Generator AI - Main CLI Application
Generates multiple-choice questions from PDF documents using Claude AI.
"""

import sys
from pathlib import Path
import typer
from typing import Optional
from dotenv import load_dotenv

# Import our modules
from parser import parse_books, extract_text_from_pdfs
from chunker import split_into_chunks, chunk_text, get_chunk_info
from generator import QuestionGenerator
from utils.json_saver import save_questions, get_question_stats


# Load environment variables
load_dotenv()

# Initialize Typer app
app = typer.Typer(
    name="question-generator",
    help="Generate multiple-choice questions from PDF documents using Claude AI"
)


@app.command()
def generate(
    input_dir: str = typer.Option(
        "books",
        "--input-dir",
        "-i",
        help="Directory containing PDF files to process"
    ),
    output_file: str = typer.Option(
        "output/questions.json",
        "--output-file",
        "-o",
        help="Path to save the generated questions JSON file"
    ),
    topic: str = typer.Option(
        "Cameroon",
        "--topic",
        "-t",
        help="Topic to focus on for question generation"
    ),
    total_questions: int = typer.Option(
        100,
        "--total-questions",
        "-n",
        help="Total number of questions to generate (100-10000)",
        min=100,
        max=10000
    ),
    chunk_size: int = typer.Option(
        1000,
        "--chunk-size",
        help="Number of words per chunk (default: 1000)"
    ),
    overlap: int = typer.Option(
        200,
        "--overlap",
        help="Number of words to overlap between chunks (default: 200)"
    )
):
    """
    Generate multiple-choice questions from PDF files.
    
    Example:
        python src/main.py --input-dir books --output-file output/questions.json --topic "Cameroon" --total-questions 1000
    """
    
    print("=" * 70)
    print("  QUESTION GENERATOR AI - Phase 1")
    print("=" * 70)
    print()
    
    # Display configuration
    print("Configuration:")
    print(f"  Input Directory: {input_dir}")
    print(f"  Output File: {output_file}")
    print(f"  Topic: {topic}")
    print(f"  Total Questions: {total_questions}")
    print(f"  Chunk Size: {chunk_size} words")
    print(f"  Chunk Overlap: {overlap} words")
    print()
    
    try:
        # Step 1: Parse PDFs (Phase 2 Enhanced)
        print("=" * 70)
        print("PHASE 2: TEXT EXTRACTION & PREPROCESSING")
        print("=" * 70)
        print("\nSTEP 1: Extracting and cleaning PDF text")
        print("-" * 70)
        
        combined_text, extraction_stats = extract_text_from_pdfs(input_dir)
        
        if not combined_text:
            typer.secho(
                "\n[ERROR] No text extracted from PDFs. Please check your input directory.",
                fg=typer.colors.RED,
                bold=True
            )
            raise typer.Exit(code=1)
        
        print()
        
        # Step 2: Split into chunks (Phase 2 Enhanced)
        print("=" * 70)
        print("STEP 2: Chunking text for Claude API processing")
        print("-" * 70)
        
        chunks = chunk_text(combined_text, chunk_size, overlap)
        
        if not chunks:
            typer.secho(
                "\n[ERROR] Failed to create text chunks.",
                fg=typer.colors.RED,
                bold=True
            )
            raise typer.Exit(code=1)
        
        # Display preprocessing summary
        print("\n" + "=" * 70)
        print("PREPROCESSING SUMMARY")
        print("=" * 70)
        print(f"Extracted {extraction_stats['total_pages']:,} pages -> {len(chunks)} text chunks ready for Claude generation")
        print(f"  Source: {extraction_stats['files_processed']} PDF file(s)")
        print(f"  Total words: {extraction_stats['total_words']:,}")
        print(f"  Chunks created: {len(chunks)}")
        print(f"  Avg words/chunk: {extraction_stats['total_words'] // len(chunks):,}")
        print("=" * 70)
        print()
        
        # Step 3: Generate questions
        print("=" * 70)
        print("STEP 3: Generating questions with Claude AI")
        print("=" * 70)
        
        generator = QuestionGenerator()
        questions = generator.generate_questions(chunks, topic, total_questions)
        
        if not questions:
            typer.secho(
                "[ERROR] No questions generated. Please check your API key and try again.",
                fg=typer.colors.RED,
                bold=True
            )
            raise typer.Exit(code=1)
        
        print()
        
        # Step 4: Save questions
        print("=" * 70)
        print("STEP 4: Saving questions to file")
        print("=" * 70)
        save_questions(questions, output_file)
        
        # Display statistics
        print()
        print("=" * 70)
        print("STATISTICS")
        print("=" * 70)
        stats = get_question_stats(questions)
        
        print(f"\nTotal Questions: {stats['total']}")
        
        print("\nBy Category:")
        for category, count in sorted(stats['by_category'].items()):
            percentage = (count / stats['total']) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        print("\nBy Difficulty:")
        for difficulty, count in sorted(stats['by_difficulty'].items()):
            percentage = (count / stats['total']) * 100
            print(f"  {difficulty}: {count} ({percentage:.1f}%)")
        
        print()
        print("=" * 70)
        typer.secho(
            "[SUCCESS] Question Generator completed successfully!",
            fg=typer.colors.GREEN,
            bold=True
        )
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        raise typer.Exit(code=130)
    
    except Exception as e:
        print()
        typer.secho(
            f"[ERROR] {str(e)}",
            fg=typer.colors.RED,
            bold=True
        )
        raise typer.Exit(code=1)


@app.command()
def version():
    """Display version information."""
    typer.echo("Question Generator AI - Phase 1")
    typer.echo("Version: 1.0.0")


@app.command()
def init():
    """Initialize the question generator and verify setup."""
    print("=" * 70)
    print("  QUESTION GENERATOR - INITIALIZATION")
    print("=" * 70)
    print()
    
    # Check for required directories
    books_dir = Path("books")
    output_dir = Path("output")
    
    print("Checking directories...")
    
    if not books_dir.exists():
        books_dir.mkdir(parents=True)
        print(f"  [OK] Created {books_dir}/")
    else:
        print(f"  [OK] Found {books_dir}/")
    
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        print(f"  [OK] Created {output_dir}/")
    else:
        print(f"  [OK] Found {output_dir}/")
    
    print()
    
    # Check for API key
    print("Checking environment...")
    try:
        from generator import QuestionGenerator
        generator = QuestionGenerator()
        print("  [OK] Claude API key found")
    except Exception as e:
        typer.secho(
            f"  [ERROR] Claude API key not found or invalid",
            fg=typer.colors.RED
        )
        typer.secho(
            "    Please ensure CLAUDE_API_KEY is set in your .env file",
            fg=typer.colors.YELLOW
        )
        raise typer.Exit(code=1)
    
    print()
    typer.secho(
        "[SUCCESS] Question Generator initialized successfully!",
        fg=typer.colors.GREEN,
        bold=True
    )
    print()


if __name__ == "__main__":
    app()

