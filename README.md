# Question Generator AI - Phase 1

An intelligent question generator that creates multiple-choice questions from PDF documents using Claude AI (Anthropic).

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

## Project Structure

```
Questions-generator/
├── src/
│   ├── main.py              # CLI application entry point
│   ├── parser.py            # PDF text extraction and cleaning
│   ├── chunker.py           # Text chunking for AI processing
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
