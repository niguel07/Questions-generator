# Question Generator AI - Phases 1 & 2

An intelligent question generator that creates multiple-choice questions from PDF documents using Claude AI (Anthropic). Features advanced text extraction, preprocessing, and AI-powered question generation.

## Features

- 📚 **PDF Processing**: Automatically extracts and cleans text from multiple PDF files
- 🤖 **AI-Powered Generation**: Uses Claude 3.5 Sonnet to generate high-quality questions
- 🎯 **Flexible Topics**: Generate questions on any topic (optimized for Cameroon by default)
- ⚖️ **Balanced Categories**: Automatically balances question categories for comprehensive coverage
- 📊 **Adjustable Scale**: Generate anywhere from 100 to 10,000 questions
- 💾 **JSON Output**: Clean, structured JSON format for easy integration
- 🔄 **Progress Tracking**: Real-time progress bars and detailed statistics

## Setup

### Prerequisites

- Python 3.11 or higher
- Claude API key from Anthropic

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Questions-generator
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```
   CLAUDE_API_KEY=your_api_key_here
   ```

5. **Initialize the generator**:
   ```bash
   python src/main.py init
   ```

## Usage

### Basic Usage

Generate 1000 questions about Cameroon from PDFs in the `books/` directory:

```bash
python src/main.py --input-dir books --output-file output/questions.json --topic "Cameroon" --total-questions 1000
```

### Command-Line Options

```bash
python src/main.py [OPTIONS]

Options:
  -i, --input-dir TEXT           Directory containing PDF files [default: books]
  -o, --output-file TEXT         Output JSON file path [default: output/questions.json]
  -t, --topic TEXT               Topic to focus on [default: Cameroon]
  -n, --total-questions INTEGER  Number of questions (100-10000) [default: 100]
  --chunk-size INTEGER           Words per chunk [default: 1000]
  --overlap INTEGER              Word overlap between chunks [default: 200]
  --help                         Show this message and exit
```

### Other Commands

- **Check version**:
  ```bash
  python src/main.py version
  ```

- **Initialize/verify setup**:
  ```bash
  python src/main.py init
  ```

## Phase 2 – Text Extraction and Chunking

Phase 2 implements a robust preprocessing pipeline that prepares book text for Claude API processing:

### Text Extraction (`src/parser.py`)

The parser module handles PDF processing with production-level features:

- **File Size Validation**: Automatically skips PDFs larger than 50 MB to prevent memory issues
- **Page-by-Page Processing**: Extracts and cleans text from each page individually
- **Header/Footer Removal**: Intelligently removes:
  - Page numbers (standalone or "Page X" format)
  - Copyright notices and symbols (©, "All Rights Reserved")
  - Chapter/Section headers
  - Excessive whitespace and line breaks
- **Error Handling**: Gracefully handles corrupted pages and files
- **UTF-8 Encoding**: Ensures proper text encoding for international characters
- **Progress Tracking**: Shows real-time progress with file and page counts
- **Statistics**: Reports files processed, pages extracted, word count, and character count

### Text Chunking (`src/chunker.py`)

The chunker module splits large texts into Claude-optimized segments:

- **Word-Level Chunking**: Splits text into ~1000-word chunks (configurable)
- **Overlap Strategy**: 100-word overlap between chunks maintains sentence continuity
- **Context Preservation**: Ensures Claude receives complete, coherent text segments
- **Adaptive Processing**: Handles texts of any size, from single pages to entire books
- **Validation**: Checks for empty text and invalid overlap settings
- **Detailed Statistics**: Tracks chunk count, word distribution, and size metrics

### How It Works

```
1. PDF Files (books/) 
   ↓
2. Extract & Clean (parser.py)
   - Remove headers/footers
   - Clean whitespace
   - Validate file sizes
   ↓
3. Split into Chunks (chunker.py)
   - ~1000 words per chunk
   - 100-word overlap
   - Maintain context
   ↓
4. Ready for Claude API
   - Optimized segments
   - Complete sentences
   - Balanced distribution
```

### Example Output

When running the generator, Phase 2 preprocessing displays:

```
======================================================================
PHASE 2: TEXT EXTRACTION & PREPROCESSING
======================================================================

STEP 1: Extracting and cleaning PDF text
----------------------------------------------------------------------
[INFO] Found 3 PDF file(s) to process
Reading PDFs: 100%|████████████████████| 3/3 [00:05<00:00]

----------------------------------------------------------------------
[SUCCESS] Text extraction complete
  Files processed: 3/3
  Total pages: 185
  Total characters: 524,832
  Total words: 87,472

======================================================================
STEP 2: Chunking text for Claude API processing
----------------------------------------------------------------------

[SUCCESS] Text chunking complete
  Total chunks created: 98
  Chunk size: 1000 words
  Overlap: 100 words
  Source text: 87,472 words

======================================================================
PREPROCESSING SUMMARY
======================================================================
Extracted 185 pages -> 98 text chunks ready for Claude generation
  Source: 3 PDF file(s)
  Total words: 87,472
  Chunks created: 98
  Avg words/chunk: 892
======================================================================
```

## Project Structure

```
Questions-generator/
├── src/
│   ├── main.py              # CLI application entry point
│   ├── parser.py            # PDF text extraction & cleaning (Phase 2)
│   ├── chunker.py           # Text chunking for AI processing (Phase 2)
│   ├── generator.py         # Claude AI integration
│   └── utils/
│       ├── __init__.py
│       └── json_saver.py    # JSON file handling
├── books/                   # Place your PDF files here
├── output/                  # Generated questions saved here
├── .env                     # API keys (create this)
├── .gitignore
├── requirements.txt
└── README.md
```

## Output Format

Questions are saved as a JSON array with the following structure:

```json
[
  {
    "question": "What is the capital of Cameroon?",
    "options": {
      "A": "Douala",
      "B": "Yaoundé",
      "C": "Buea",
      "D": "Bamenda"
    },
    "answer": "B",
    "category": "Geography",
    "difficulty": "easy",
    "explanation": "Yaoundé is the political capital of Cameroon, located in the Centre Region."
  }
]
```

### Field Descriptions

- **question**: The question text
- **options**: Four answer choices (A, B, C, D)
- **answer**: The correct answer letter
- **category**: Question category (e.g., Geography, History, Culture)
- **difficulty**: Question difficulty (easy, medium, hard)
- **explanation**: Brief explanation of the correct answer

## Category Distribution (Cameroon Topic)

When generating questions about Cameroon, the system automatically balances categories:

- **Geography**: 25% (landmarks, regions, climate, natural resources)
- **History**: 25% (historical events, independence, colonial period)
- **Culture**: 25% (traditions, languages, festivals, food)
- **General Knowledge**: 25% (economy, politics, sports, notable figures)

## Adjustable Question Count

You can generate anywhere from 100 to 10,000 questions:

- **100-500**: Quick dataset for testing
- **500-2000**: Standard dataset for applications
- **2000-5000**: Large dataset for comprehensive coverage
- **5000-10000**: Massive dataset for extensive training/testing

## Custom Topics

The generator works with any topic, not just Cameroon:

```bash
# Generate questions about Python programming
python src/main.py --topic "Python Programming" --total-questions 500

# Generate questions about World History
python src/main.py --topic "World History" --total-questions 1000
```

## Error Handling

The system gracefully handles:

- **API Rate Limits**: Automatic retry with exponential backoff
- **Malformed Responses**: Validates and filters invalid questions
- **Network Issues**: Retries failed requests up to 3 times
- **Empty PDFs**: Warns and continues with available content

## Performance Considerations

- **Processing Time**: Approximately 2-5 seconds per chunk (depends on API response time)
- **API Costs**: Each chunk requires one API call to Claude
- **Chunk Size**: Default 1000 words balances context and processing speed
- **Overlap**: 200-word overlap ensures context continuity

## Tips for Best Results

1. **Quality PDFs**: Use text-based PDFs (not scanned images) for best extraction
2. **Relevant Content**: Ensure PDFs contain content related to your chosen topic
3. **Sufficient Text**: More source text generally produces more diverse questions
4. **Topic Specificity**: Be specific with your topic for more focused questions

## Troubleshooting

### "No PDF files found"
- Ensure PDF files are in the `books/` directory
- Check that files have the `.pdf` extension

### "CLAUDE_API_KEY not found"
- Verify the `.env` file exists in the project root
- Check that the API key is correctly formatted

### "JSON parsing error"
- This is usually temporary; the system will retry
- If persistent, check your API key validity

### Questions not balanced correctly
- Ensure sufficient source material for all categories
- Try adjusting chunk size if needed

## Development

### Running Tests

```bash
# Test parser
python src/parser.py

# Test chunker
python src/chunker.py

# Test generator (requires API key)
python src/generator.py

# Test JSON saver
python src/utils/json_saver.py
```

## Future Enhancements (Upcoming Phases)

- Web interface for question management
- Question editing and refinement
- Export to multiple formats (CSV, Excel, Markdown)
- Question difficulty balancing
- Duplicate detection
- Multi-language support

## License

See LICENSE file for details.

## Support

For issues or questions, please open an issue on the repository.

---

**Built with ❤️ using Claude AI by Anthropic**
