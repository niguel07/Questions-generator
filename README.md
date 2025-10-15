# Question Generator AI - Complete System (Phases 1-10)

An intelligent question generator that creates multiple-choice questions from PDF documents using Claude AI (Anthropic). Features advanced text extraction, preprocessing, AI-powered question generation, and a professional React dashboard with real-time progress tracking.

## ⚡ Performance Optimizations (Latest Update)

**Up to 10x faster generation** with our latest optimizations:

- 🚀 **Async/Concurrent Processing**: Process 5+ API calls simultaneously instead of sequentially
- 🎯 **Smart Chunking**: Only process chunks actually needed (not all 284 chunks for 333 questions!)
- 📦 **Batch Generation**: Generate 5-10 questions per API call instead of 1
- ⏱️ **Minimal Delays**: Reduced delays from 2s to 0.1s between batches (API handles rate limiting)
- 🧠 **Intelligent Allocation**: Dynamically calculate optimal questions-per-chunk ratio

**Performance Comparison:**
- **Old**: 333 questions from 284 chunks = 284 API calls × 2s delay = ~10-15 minutes
- **New**: 333 questions from ~50 chunks = 50 API calls × 0.1s delay = **~2-3 minutes** (5-7x faster!)

## Features

- 📚 **PDF Processing**: Automatically extracts and cleans text from multiple PDF files
- 🤖 **AI-Powered Generation**: Uses Claude 3.5 Sonnet to generate high-quality questions
- 🎯 **Flexible Topics**: Generate questions on any topic with multi-topic support
- ⚖️ **Balanced Categories**: Automatically balances question categories for comprehensive coverage
- 📊 **Adjustable Scale**: Generate anywhere from 100 to 10,000 questions
- 💾 **JSON Output**: Clean, structured JSON format for easy integration
- 🔄 **Progress Tracking**: Real-time progress bars and detailed statistics
- 🎨 **React Dashboard**: Professional UI with analytics, charts, and live monitoring
- 🔐 **User Authentication**: Secure signup/login with session management
- 🤖 **AI Review Assistant**: Claude-powered question review and feedback
- 📥 **Export/Import**: Download and upload question datasets

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

## Phase 3 – Question Generation Engine

Phase 3 implements the core Claude AI integration for generating high-quality multiple-choice questions with robust error handling and comprehensive logging.

### Question Generation (`src/generator.py`)

The generator module leverages Claude 3.5 Sonnet to create structured questions from preprocessed text chunks:

#### Core Features

- **Claude API Integration**: Uses Anthropic's Claude 3.5 Sonnet model
- **Dynamic Question Distribution**: Calculates optimal questions per chunk based on total target
- **Category Balancing**: For Cameroon topic, enforces 25% distribution across 4 categories
- **Robust Retry Logic**: Attempts up to 3 retries with exponential backoff for failed API calls
- **Rate Limiting**: 2-second delay between API calls to prevent rate limit errors
- **Error Logging**: Failed chunks logged to `output/errors.log` with timestamps and details
- **Progress Tracking**: Real-time progress bars showing chunk processing status
- **Comprehensive Statistics**: Tracks API calls, success rates, duration, and failures

#### How It Works

1. **Initialization**
   - Loads Claude API key from `.env`
   - Initializes error logging system
   - Prepares statistics tracking

2. **Question Generation Loop**
   ```
   For each text chunk:
   1. Create structured prompt with category requirements
   2. Send to Claude API with retry logic
   3. Parse and validate JSON response
   4. Log any errors to errors.log
   5. Wait 2 seconds before next request (rate limiting)
   6. Continue until target question count reached
   ```

3. **Validation**
   - Each question must have: question, options (A-D), answer, category, difficulty, explanation
   - Invalid questions are filtered out automatically
   - Validation errors logged for debugging

4. **Category Distribution (Cameroon)**
   When topic is "Cameroon", the system enforces balanced categories:
   - **Geography 25%**: Landmarks, regions, climate, natural resources
   - **History 25%**: Historical events, independence, colonial period, leaders
   - **Culture 25%**: Traditions, languages, festivals, food, customs
   - **General Knowledge 25%**: Economy, politics, sports, notable figures

### JSON Output (`src/utils/json_saver.py`)

Enhanced JSON saver with validation ensures data integrity:

- **Structure Validation**: Verifies all required fields before saving
- **UTF-8 Encoding**: Properly handles international characters
- **File Statistics**: Reports saved count, file size, and location
- **Error Recovery**: Skips invalid questions with warnings

### Execution Time & Performance

The system tracks and reports comprehensive performance metrics:

- **Duration Tracking**: Measures total execution time from start to finish
- **Questions/Second**: Calculates generation rate
- **API Statistics**: Total calls, successful calls, failed chunks
- **Success Rate**: Percentage of target questions successfully generated

### Example Generation Output

```bash
$ python src/main.py --input-dir books --topic "Cameroon" --total-questions 1000

======================================================================
PHASE 2: TEXT EXTRACTION & PREPROCESSING
======================================================================
[SUCCESS] Text extraction complete
  Total pages: 185
  Total words: 87,472

======================================================================
CLAUDE QUESTION GENERATION ENGINE - PHASE 3
======================================================================
Target: 1,000 questions from 98 chunks
Strategy: ~10 questions per chunk
Topic: Cameroon
Category Balance: Geography 25%, History 25%, Culture 25%, General 25%
======================================================================

Generating questions: 100%|████████████| 98/98 [03:16<00:00, 2.00s/chunk]

======================================================================
GENERATION COMPLETE
======================================================================
[SUCCESS] Generated 1,000 questions
  Target: 1,000
  Success rate: 100.0%
  Duration: 3m 16s
======================================================================

[SUCCESS] Successfully generated 1,000 questions saved to output/questions.json
  File size: 524,832 bytes (512.5 KB)

======================================================================
[SUCCESS] Generated 1,000 questions in 3m 32s for topic "Cameroon"
======================================================================

FINAL SUMMARY:
  Total execution time: 3m 32s
  Questions generated: 1,000/1,000
  Output file: output/questions.json
  File size: 512.5 KB
======================================================================
```

### Scaling Considerations

The system is designed to handle question generation from 100 to 10,000 questions:

| Question Count | Estimated Time* | API Calls | Estimated Cost** |
|----------------|-----------------|-----------|------------------|
| 100            | 30s - 1m        | ~10       | ~$0.10          |
| 500            | 2m - 5m         | ~50       | ~$0.50          |
| 1,000          | 3m - 8m         | ~100      | ~$1.00          |
| 5,000          | 15m - 40m       | ~500      | ~$5.00          |
| 10,000         | 30m - 1h 20m    | ~1000     | ~$10.00         |

*Time estimates include 2-second rate limiting between requests  
**Cost estimates based on Claude 3.5 Sonnet pricing (may vary)

### Error Handling

The system implements multiple layers of error handling:

1. **API Timeouts**: Automatic retry with exponential backoff (1s, 2s, 4s)
2. **JSON Parse Errors**: Attempts to extract JSON from markdown-wrapped responses
3. **Invalid Questions**: Filtered out with validation warnings
4. **Failed Chunks**: Logged to `output/errors.log` with full details
5. **Rate Limits**: 2-second delays prevent hitting API limits

### Error Log Format

When errors occur, they're logged to `output/errors.log`:

```
[2025-10-15 11:30:45] API_ERROR
Chunk Index: 23
Error: API call failed: Connection timeout
Chunk Preview: Cameroon's economic landscape has evolved significantly...
----------------------------------------------------------------------
```

### Adjusting Question Count & Topics

**Change Question Count:**
```bash
# Generate 100 questions (minimum)
python src/main.py --total-questions 100

# Generate 10,000 questions (maximum)
python src/main.py --total-questions 10000
```

**Change Topic:**
```bash
# Generate questions about Python programming
python src/main.py --topic "Python Programming" --total-questions 500

# Generate questions about World History
python src/main.py --topic "World History" --total-questions 2000
```

**Note**: Only the "Cameroon" topic uses the predefined 25% category distribution. Other topics use adaptive categories based on content.

## Phase 4 – Validation & Quality Scoring

Phase 4 implements a comprehensive validation and quality scoring system to ensure all generated questions are clean, unique, and high-quality before saving.

### Question Validation (`src/validator.py`)

The validator performs multiple checks to filter out invalid or duplicate questions:

#### Validation Checks

1. **Schema Validation**
   - Ensures all required fields are present: `question`, `options`, `answer`, `category`, `difficulty`, `explanation`
   - Skips questions with missing fields

2. **Text Length Check**
   - Questions must be 20-300 characters
   - Too short (<20) or too long (>300) questions are rejected

3. **Option Integrity**
   - Must have exactly 4 unique options (A, B, C, D)
   - Removes questions with duplicate options
   - Validates options are non-empty strings

4. **Answer Matching with Auto-Correction**
   - Ensures answer is one of the provided options (A, B, C, D)
   - Auto-corrects answers using fuzzy matching (`difflib.get_close_matches()`)
   - Logs auto-corrections for review

5. **Duplicate Detection**
   - Compares normalized question text
   - Uses fuzzy matching with 85% similarity threshold
   - Removes duplicate questions automatically

6. **Category Normalization**
   - Forces categories to title case (e.g., "Geography", "Culture")
   - Ensures consistent formatting

7. **Difficulty Normalization**
   - Accepts only "Easy", "Medium", or "Hard"
   - Auto-corrects variations (e.g., "intermediate" → "Medium")
   - Defaults to "Medium" for unrecognized values

8. **Factual Content Checks**
   - Removes questions starting with punctuation
   - Removes questions with only numbers
   - Removes questions with no letters

#### Validation Report

All validation results are logged to `output/validation_report.txt`:

```
======================================================================
QUESTION VALIDATION REPORT
======================================================================
Generated: 2025-10-15 12:30:45

SUMMARY:
  Total input questions: 1,000
  Valid questions retained: 876
  Questions dropped: 124
  Success rate: 87.6%

DROPPED QUESTIONS BREAKDOWN:
  - Missing required keys: 5
  - Invalid question length: 12
  - Invalid options structure: 8
  - Invalid/unfixable answer: 15
  - Duplicate questions: 60
  - Factual/formatting issues: 24

AUTO-CORRECTIONS:
  - Answers auto-corrected: 32

VALIDATION CHECKS PERFORMED:
  ✓ Schema validation (required fields)
  ✓ Question length (20-300 characters)
  ✓ Options integrity (4 unique options)
  ✓ Answer matching with auto-correction
  ✓ Duplicate detection (85% similarity threshold)
  ✓ Category normalization (title case)
  ✓ Difficulty normalization (Easy/Medium/Hard)
  ✓ Factual content checks
======================================================================
```

### Quality Scoring (`src/quality_scorer.py`)

The quality scorer assigns scores from 0.0 to 1.0 based on multiple quality criteria:

#### Scoring Criteria (Weights: 20% each)

1. **Question Clarity (20%)**
   - Optimal length: 30-200 characters
   - Bonus for ending with question mark
   - Penalizes too short or too long questions

2. **Balanced Options (20%)**
   - All 4 options must be distinct
   - Options should be reasonably similar in length
   - Better balance = higher score

3. **Valid Answer (20%)**
   - Answer must be A, B, C, or D
   - Must match an existing option key
   - Binary: 1.0 if valid, 0.0 if not

4. **Explanation Quality (20%)**
   - Must be at least 15 characters
   - Optimal: 50+ characters
   - Bonus for complete sentences (ending with period)

5. **Metadata Quality (20%)**
   - Valid category (non-empty, 3+ characters)
   - Valid difficulty (Easy, Medium, or Hard)

#### Quality Score Interpretation

- **0.9 - 1.0**: Excellent quality
- **0.7 - 0.9**: Good quality
- **0.5 - 0.7**: Fair quality
- **0.0 - 0.5**: Poor quality (consider filtering)

#### Quality Distribution

The scorer provides a distribution report:

```
======================================================================
QUALITY SCORING
======================================================================
Scoring 876 questions...

[SUCCESS] Quality scoring complete
  Average quality score: 0.892
  Score range: 0.650 - 1.000

Quality Distribution:
  Excellent (0.9-1.0): 520 (59.4%)
  Good (0.7-0.9): 312 (35.6%)
  Fair (0.5-0.7): 44 (5.0%)
  Poor (0.0-0.5): 0 (0.0%)
======================================================================
```

### Integration in Pipeline

Phase 4 automatically runs after question generation:

```
1. Generate questions with Claude API (Phase 3)
   ↓
2. Validate questions (Phase 4)
   - Remove invalid entries
   - Remove duplicates
   - Normalize data
   - Log validation report
   ↓
3. Score questions (Phase 4)
   - Calculate quality scores
   - Sort by quality (highest first)
   - Display quality distribution
   ↓
4. Save to JSON
   - Only validated, high-quality questions
   - Each question includes quality_score field
```

### Example Output with Validation & Scoring

```bash
$ python src/main.py --input-dir books --topic "Cameroon" --total-questions 1000

======================================================================
PHASE 4: QUESTION VALIDATION & QUALITY CONTROL
======================================================================
Validating 1,000 generated questions...

[SUCCESS] Validation complete - 876 valid questions retained
  Dropped: 124 invalid entries
  Duplicates removed: 60
  Auto-corrected answers: 32
  Validation report: output/validation_report.txt

======================================================================
QUALITY SCORING
======================================================================
Scoring 876 questions...

[SUCCESS] Quality scoring complete
  Average quality score: 0.892
  Score range: 0.650 - 1.000

Quality Distribution:
  Excellent (0.9-1.0): 520 (59.4%)
  Good (0.7-0.9): 312 (35.6%)
  Fair (0.5-0.7): 44 (5.0%)
  Poor (0.0-0.5): 0 (0.0%)

======================================================================
[SUCCESS] Generated 876 questions in 3m 32s for topic "Cameroon"
======================================================================

FINAL SUMMARY:
  Total execution time: 3m 32s
  Questions generated: 1,000
  Questions validated: 876
  Questions retained: 876/1,000
  Average quality score: 0.892
  Output file: output/questions.json
  File size: 458.3 KB

OUTPUT FILES:
  Questions: output/questions.json
  Validation report: output/validation_report.txt
======================================================================
```

### Using Quality Scores

Questions in the output JSON include a `quality_score` field:

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
    "difficulty": "Easy",
    "explanation": "Yaoundé is the political capital of Cameroon.",
    "quality_score": 0.950
  }
]
```

**Filtering by Quality:**

You can filter questions by quality score for specific use cases:

```python
import json

# Load questions
with open('output/questions.json', 'r') as f:
    questions = json.load(f)

# Filter for excellent quality only
excellent = [q for q in questions if q['quality_score'] >= 0.9]

# Filter for good or better
good_plus = [q for q in questions if q['quality_score'] >= 0.7]
```

### Reading the Validation Report

The validation report (`output/validation_report.txt`) provides:

- **Summary statistics**: Total input, output, dropped, success rate
- **Breakdown by issue type**: Detailed counts for each validation failure
- **Auto-corrections**: How many answers were automatically fixed
- **Validation checks performed**: Complete list of checks applied

**Use the report to:**
- Understand why questions were dropped
- Identify patterns in invalid questions
- Adjust your source material or generation parameters
- Monitor validation success rates over time

## Phase 5 – React Dashboard & Analytics API

Phase 5 adds a professional React dashboard with FastAPI backend for visualizing question generation statistics and validation reports in real-time.

### Backend Analytics API (`src/analytics.py`)

FastAPI backend that serves question statistics and reports to the React frontend:

#### API Endpoints

1. **GET /** - API information and available endpoints
2. **GET /health** - Health check endpoint
3. **GET /summary** - Returns complete statistics:
   ```json
   {
     "total_questions": 9876,
     "avg_quality_score": 0.92,
     "categories": {
       "Geography": 2450,
       "History": 2500,
       "Culture": 2460,
       "General Knowledge": 2466
     },
     "difficulty": {
       "Easy": 4700,
       "Medium": 3500,
       "Hard": 1676
     },
     "quality_distribution": {
       "excellent": 5876,
       "good": 3200,
       "fair": 700,
       "poor": 100
     }
   }
   ```

4. **GET /validation-report** - Returns validation report text
5. **GET /questions?limit=10** - Returns sample questions

#### Features

- **CORS Support**: Configured for `localhost:5173` (React dev server)
- **Error Handling**: Graceful error messages if files don't exist
- **Auto-reload**: Uses uvicorn with `--reload` flag for development

### Frontend Dashboard (`frontend/`)

Professional React + Vite dashboard with Material-UI components:

#### Tech Stack

- **React 18** with Vite for fast development
- **Material-UI** for component library
- **Recharts** for data visualization
- **Axios** for API communication

#### Two-Color Theme

**Primary Color**: #2563EB (Blue)
- Headers, buttons, charts, accents

**Neutral Color**: #F9FAFB (Light Gray)
- Background, cards, surfaces

**Design Philosophy**:
- Minimal and clean
- Rounded corners (8px)
- Subtle shadows
- Smooth hover effects
- Professional typography (Inter font)

#### Components

1. **StatsCard** - Displays key metrics (total questions, avg quality score)
   - Large value display
   - Icon decoration
   - Hover animation

2. **ChartCard** - Visualizes data distributions
   - Bar charts for categories and quality
   - Pie chart for difficulty levels
   - Responsive sizing

3. **ReportPanel** - Shows validation report
   - Monospace font for report text
   - Scrollable content area
   - Syntax highlighting

#### Features

- **Auto-Refresh**: Fetches new data every 60 seconds
- **Manual Refresh**: Button to reload data on demand
- **Last Update Timestamp**: Shows when data was last fetched
- **Error Handling**: Displays friendly error messages if backend is unavailable
- **Loading States**: Shows spinner while fetching data
- **Responsive Design**: Works on desktop, tablet, and mobile (min-width: 320px)

### Running the Full Stack

#### 1. Start the Backend (Terminal 1)

```bash
# From project root
cd Questions-generator

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Start FastAPI server
uvicorn src.analytics:app --reload
```

Backend will be available at: `http://localhost:8000`

#### 2. Start the Frontend (Terminal 2)

```bash
# From project root
cd Questions-generator/frontend

# Install npm dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

#### Quick Start Script

For convenience, you can run both servers:

**Windows (PowerShell):**
```powershell
# Terminal 1
cd Questions-generator
uvicorn src.analytics:app --reload

# Terminal 2
cd Questions-generator
npm run dev --prefix frontend
```

**Linux/Mac:**
```bash
# Terminal 1
cd Questions-generator && uvicorn src.analytics:app --reload

# Terminal 2
cd Questions-generator && npm run dev --prefix frontend
```

### Dashboard Features

#### Real-Time Statistics

The dashboard displays:

1. **Total Questions** - Number of validated questions in dataset
2. **Average Quality Score** - Mean quality score (0.0 - 1.0)
3. **Category Distribution** - Bar chart showing question breakdown by category
4. **Difficulty Distribution** - Pie chart showing Easy/Medium/Hard distribution
5. **Quality Distribution** - Bar chart showing Excellent/Good/Fair/Poor breakdown
6. **Validation Report** - Full text validation report with statistics

#### Auto-Refresh

- Data automatically refreshes every 60 seconds
- Manual refresh button available in header
- Last update timestamp displayed

#### Responsive Design

The dashboard is fully responsive:
- **Desktop** (>960px): Two-column grid layout
- **Tablet** (600-960px): Adaptive grid
- **Mobile** (<600px): Single column stack

### API Integration

The frontend communicates with the backend via REST API:

```javascript
// Fetch summary statistics
const response = await axios.get('http://localhost:8000/summary');

// Fetch validation report
const report = await axios.get('http://localhost:8000/validation-report');
```

### Development Notes

**Backend Dependencies** (added to `requirements.txt`):
- `fastapi>=0.109.0` - Modern API framework
- `uvicorn>=0.27.0` - ASGI server

**Frontend Dependencies** (package.json):
- `axios` - HTTP client
- `recharts` - Chart library
- `@mui/material` - UI components
- `@emotion/react` & `@emotion/styled` - Styling

### Troubleshooting

**Backend not starting?**
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Try different port
uvicorn src.analytics:app --reload --port 8001
```

**Frontend can't connect to backend?**
- Ensure backend is running on port 8000
- Check CORS configuration in `src/analytics.py`
- Verify API_BASE_URL in `frontend/src/App.jsx`

**Data not showing?**
- Generate questions first: `python src/main.py --total-questions 100`
- Ensure `output/questions.json` exists
- Check browser console for errors

### Screenshots

```
┌─────────────────────────────────────────────────────────┐
│  Question Generator Dashboard                  🔄 Refresh │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────────────┐  │
│  │ Total Questions │  │  Average Quality Score       │  │
│  │      9,876      │  │         0.920                │  │
│  └─────────────────┘  └──────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Category Distribution (Bar Chart)                  │ │
│  │  [=======Geography=========]                        │ │
│  │  [=======History===========]                        │ │
│  │  [=======Culture===========]                        │ │
│  │  [=======General===========]                        │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ Difficulty Chart │  │  Quality Distribution        │ │
│  │   (Pie Chart)    │  │    (Bar Chart)               │ │
│  └──────────────────┘  └──────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Validation Report                                  │ │
│  │  ═══════════════════════════════════════════════    │ │
│  │  Total: 10,000 | Valid: 9,876 | Dropped: 124       │ │
│  └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│               Niguel Clark © 2025

---

## Phase 6 – Interactive Generation UI

Phase 6 introduces a professional, minimalist web interface for uploading books and generating questions with real-time progress monitoring.

### 🎨 Features

- **Drag-and-Drop Upload**: Upload PDF files by dragging them into the browser or clicking to browse
- **Real-Time Progress**: Live progress bar and activity log during generation
- **Tabbed Interface**: Switch between Analytics Dashboard and Question Generation
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Two-Color Theme**: Clean, professional UI with blue (#2563EB) and neutral (#F9FAFB) colors

### 🚀 Getting Started

#### 1. Start the Backend Server

In the first terminal, start the FastAPI backend:

```bash
cd Questions-generator
python src/server.py
```

The API will be available at `http://localhost:8000`

#### 2. Start the Frontend Development Server

In a second terminal, start the React frontend:

```bash
cd Questions-generator/frontend
npm install  # First time only
npm run dev
```

The UI will be available at `http://localhost:5173`

### 📝 How to Use

1. **Open the Application**
   - Navigate to `http://localhost:5173` in your browser
   - You'll see two tabs: Dashboard and Generate

2. **Upload PDF Books**
   - Click on the "Generate" tab
   - Drag and drop PDF files into the upload area (or click to browse)
   - Maximum 50MB per file
   - Click "Upload" to send files to the server

3. **Configure Generation Settings**
   - Enter a topic (e.g., "Cameroon", "Python Programming", "World History")
   - Use the slider to select number of questions (100-10,000)
   - Estimated generation time is displayed

4. **Start Generation**
   - Click the "Generate Questions" button
   - Watch real-time progress in the activity log
   - Progress bar shows completion percentage

5. **Download Results**
   - When generation completes, a "Download Questions JSON" button appears
   - Click to download your generated questions
   - Switch to the Dashboard tab to view analytics

### 🖥️ UI Components

#### UploadCard Component
- Drag-and-drop zone for PDF uploads
- File list with size display
- Remove individual files before upload
- Multi-file support

#### ConfigForm Component
- Topic input field with validation
- Question count slider (100-10,000)
- Estimated time calculation
- Generate button with disabled state during processing

#### ProgressPanel Component
- Status indicators (idle, generating, completed, error)
- Progress bar with percentage
- Scrollable activity log
- Success/error alerts
- Download button on completion

### 🔧 Backend API Endpoints

Phase 6 adds the following new endpoints to `src/server.py`:

#### File Upload
```
POST /upload
Content-Type: multipart/form-data

Accepts multiple PDF files and saves them to books/ directory
Returns: Upload success/error report
```

#### Start Generation
```
POST /generate
Content-Type: application/json
Body: {
  "topic": "Cameroon",
  "total_questions": 1000
}

Starts background generation process
Returns: Confirmation message
```

#### Get Progress
```
GET /progress

Returns current generation status and logs
Response: {
  "status": "generating|completed|error|idle",
  "progress": 0-100,
  "message": "Current step description",
  "logs": ["[12:30:45] Log entry 1", ...],
  "error": null,
  "duration_seconds": 123.45
}
```

#### List Uploaded Files
```
GET /files

Returns list of PDF files in books/ directory
Response: {
  "files": [
    {"filename": "book.pdf", "size": 1234567, "size_mb": 1.18}
  ],
  "total": 1
}
```

### 📊 Expected Behavior

**Typical Generation Flow:**

1. User opens `http://localhost:5173`
2. Navigates to "Generate" tab
3. Uploads 1-20 PDF books (max 50MB each)
4. Enters topic: "Cameroon"
5. Sets question count: 1000
6. Clicks "Generate Questions"
7. UI shows progress:
   - ⏳ Starting generation (10%)
   - 📖 Parsing PDF files (20-30%)
   - ✂️ Chunking text (40%)
   - 🤖 Generating questions with Claude (60%)
   - ✓ Validating questions (80%)
   - ⭐ Scoring quality (90%)
   - 💾 Saving results (95%)
   - ✓ Completed (100%)
8. "Download Questions JSON" button appears
9. User downloads `questions.json`
10. User switches to Dashboard tab to view analytics

### 🎨 Design Guidelines

The UI follows these design principles:

- **Primary Color**: #2563EB (Blue) - for buttons, links, active states
- **Neutral Background**: #F9FAFB (Light Gray) - for cards and secondary backgrounds
- **Border Radius**: 8px for all cards and inputs
- **Shadows**: Subtle `0 1px 3px rgba(0,0,0,0.12)` for depth
- **Font**: System font stack (Inter/Montserrat-style)
- **Spacing**: Consistent 24px gaps between sections
- **Hover Effects**: Smooth 0.2s transitions on interactive elements

### 🔍 Troubleshooting

**Backend not connecting:**
- Ensure `python src/server.py` is running on port 8000
- Check that `.env` file contains valid `CLAUDE_API_KEY`

**Upload fails:**
- Verify file is a valid PDF (<50MB)
- Check that `books/` directory exists and is writable

**Generation hangs:**
- Check `output/errors.log` for API errors
- Verify Claude API key has sufficient credits
- Ensure PDFs contain readable text (not scanned images)

**Progress not updating:**
- Backend streams progress every 2 seconds
- Check browser console for connection errors
- Refresh the page and try again

### 📁 Updated Project Structure

```
Questions-generator/
├── src/
│   ├── main.py              # CLI entry point
│   ├── server.py            # FastAPI backend (Phase 5 & 6)
│   ├── parser.py            # PDF extraction
│   ├── chunker.py           # Text chunking
│   ├── generator.py         # Claude AI generation
│   ├── validator.py         # Question validation
│   ├── quality_scorer.py    # Quality scoring
│   └── utils/
│       └── json_saver.py    # JSON utilities
├── frontend/                # React UI (Phase 5 & 6)
│   ├── src/
│   │   ├── App.jsx          # Main app with tabs
│   │   ├── components/
│   │   │   ├── StatsCard.jsx        # Dashboard stats
│   │   │   ├── ChartCard.jsx        # Charts
│   │   │   ├── ReportPanel.jsx      # Validation report
│   │   │   ├── UploadCard.jsx       # File upload (Phase 6)
│   │   │   ├── ConfigForm.jsx       # Settings (Phase 6)
│   │   │   └── ProgressPanel.jsx    # Progress (Phase 6)
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── books/                   # PDF uploads stored here
├── output/                  # Generated questions and reports
├── .env                     # API keys
├── requirements.txt
└── README.md
```

### 🚀 Development Notes

**Frontend Technologies:**
- React 18 with Vite
- Material-UI (MUI) for components
- Axios for HTTP requests
- EventSource for Server-Sent Events (future enhancement)

**Backend Technologies:**
- FastAPI with Uvicorn
- Background task processing
- CORS middleware for cross-origin requests
- Global state management for progress tracking

**Deployment Ready:**
- Frontend builds to static files (`npm run build`)
- Backend can be served with `uvicorn src.server:app --host 0.0.0.0 --port 8000`
- Can be containerized with Docker (future enhancement)

### 🎯 Next Steps (Phase 7)

Future enhancements planned:
- WebSocket support for real-time updates
- Multi-topic generation in single session
- Question preview before download
- Export to multiple formats (CSV, PDF)
- User authentication and saved sessions
- Deployment to cloud platform (Vercel + Railway/Heroku)

---

### 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ by Niguel Clark**

---

## Phase 7 – UI Polish, Multi-Topic & Deployment Ready

Phase 7 enhances the user interface with smooth animations, multi-topic support, and prepares the system for production deployment.

### 🎨 UI Enhancements

**Animations & Polish**
- Integrated `framer-motion` for smooth transitions and micro-interactions
- Fade-in animations on component load
- Hover effects and press animations on buttons
- Progress bar with fluid transitions
- Modal animations with spring physics

**Design Refinements**
- Strict two-color palette: Primary #2563EB, Neutral #F9FAFB
- Professional typography with 600 weight headings
- Consistent 8px border radius on all cards
- Subtle box shadows for depth
- Responsive layout (max-width 800px for forms)

### 🏷️ Multi-Topic Generation

**Frontend Implementation**
- Tag-based topic input with chip display
- Press Enter to add topics
- Remove topics by clicking X on chips
- Visual feedback for active topics
- Dynamic button text showing topic count

**Backend Implementation**
- Accept array of topics in generation request
- Generate questions per topic independently
- Add `source_topic` field to each question
- Merge results from all topics
- Distribute questions evenly across topics

**Example Usage:**
```javascript
// Frontend sends:
{
  "topics": ["Cameroon", "Python Programming", "World History"],
  "total_questions": 3000
}

// Backend generates 1000 questions per topic
// Each question tagged with source_topic field
```

### 📦 Production Deployment

**Vite Build Configuration**
```bash
cd frontend
npm run build  # Builds to frontend/dist/
```

**Static File Serving**
FastAPI automatically serves the built React app:
```python
# In server.py
if Path("frontend/dist").exists():
    app.mount("/static", StaticFiles(directory="frontend/dist/assets"))
```

**Production Run**
```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start production server
uvicorn src.server:app --host 0.0.0.0 --port 8000

# Or using Python
python src/server.py
```

**Environment Setup**
Ensure `.env` contains:
```
CLAUDE_API_KEY=your_api_key_here
```

### 🎉 Completion Modal

**Features:**
- Animated entrance with spring physics
- Large success checkmark
- Display total questions generated
- Show average quality score
- Two action buttons:
  - **Download JSON**: Downloads questions immediately
  - **Start New Session**: Resets UI for next generation

**User Flow:**
1. Generation completes (100%)
2. Modal appears automatically
3. User downloads dataset
4. User either closes modal or starts new session

---

## Phase 8 – Claude Reviewer Assistant & Feedback Loop

Phase 8 adds an AI-powered review system that allows users to get expert feedback on generated questions and apply improvements.

### 🤖 AI Question Reviewer

**reviewer.py Module**
```python
from reviewer import QuestionReviewer

reviewer = QuestionReviewer()
result = reviewer.review_question(question_dict)

# Returns:
{
  "success": True,
  "review": {
    "rating": 0.85,  # 0.0-1.0
    "feedback": "Detailed expert review...",
    "issues": ["issue1", "issue2"],
    "suggested_fix": {
      "question": "Improved question text",
      "options": {...},
      "answer": "B",
      "explanation": "Better explanation"
    }
  }
}
```

**Review Criteria:**
1. **Correctness** (20%): Factual accuracy
2. **Clarity** (20%): Unambiguous wording
3. **Difficulty** (20%): Appropriate level
4. **Options** (20%): Plausible distractors
5. **Explanation** (20%): Complete and helpful

### 📊 Review Interface

**ReviewerPanel Component**
- Displays first 100 questions in scrollable table
- "Review" button for each question
- Real-time review status indicators
- Integrates with AI Review tab

**QuestionList Component**
- Sortable table with columns:
  - Question text (truncated)
  - Category (color-coded chip)
  - Difficulty (color-coded chip)
  - Quality score
  - Review action button
- Hover effects and smooth animations

**ReviewModal Component**
- Shows Claude's review in real-time
- Displays rating with color indicator:
  - Green (≥80%): Excellent
  - Yellow (60-79%): Good
  - Red (<60%): Needs improvement
- Lists identified issues as chips
- Shows suggested improvements side-by-side
- Two action buttons:
  - **Apply Suggestions**: Updates question in dataset
  - **Close**: Reject suggestions

### 🔄 Feedback Loop

**API Endpoints:**
```
POST /review
Body: {question, options, answer, explanation, category, difficulty}
Returns: Claude's review with suggestions

PATCH /update-question/{id}
Body: {question?, options?, answer?, explanation?}
Updates question in output/questions.json
```

**Workflow:**
1. User selects question from list
2. Click "Review with Claude"
3. Spinner shows while processing
4. Review appears with rating and feedback
5. User reviews suggestions
6. Click "Apply" to update dataset
7. Question updated with metadata: `updated_by_reviewer: true`

**Rate Limiting:**
- 2-second delay between API calls
- Exponential backoff on errors
- Max 3 retries per question

---

## Phase 9 – User Profiles, History & Dataset Export

Phase 9 implements user management, session tracking, and dataset import/export capabilities.

### 👤 User Management

**users.py Module**
```python
from users import UserManager

manager = UserManager()

# Login
result = manager.login("username")

# Add session
manager.add_session("username", {
  "topics": ["AI", "Python"],
  "questions_generated": 1000,
  "avg_quality": 0.92,
  "timestamp": "2025-10-15T12:00:00"
})

# Get history
sessions = manager.get_sessions("username", limit=50)

# Get stats
stats = manager.get_stats("username")
```

**User Data Storage**
Stored in `output/users.json`:
```json
{
  "niguel": {
    "created_at": "2025-10-15T10:00:00",
    "sessions": [
      {
        "topics": ["Cameroon", "AI"],
        "questions_generated": 10000,
        "avg_quality": 0.92,
        "timestamp": "2025-10-15T12:00:00"
      }
    ],
    "total_questions": 10000
  }
}
```

### 📜 Session History

**UserMenu Component**
- Login/logout button in header
- Dropdown menu with:
  - User stats summary
  - View History
  - Export Dataset
  - Import Dataset
  - Logout

**History Dialog**
- Sortable table showing:
  - Date
  - Topics (as chips)
  - Questions generated
  - Average quality
- Latest sessions first
- Max 50 sessions displayed

**User Stats:**
- Total sessions
- Total questions generated
- Unique topics used
- Latest session info

### 💾 Dataset Export/Import

**Export Functionality**
```bash
GET /export
Downloads: questions_export_YYYYMMDD_HHMMSS.json
```

Features:
- Timestamped filename
- Complete dataset with all metadata
- Quality scores preserved
- UTF-8 encoding

**Import Functionality**
```bash
POST /import
Body: multipart/form-data with JSON file
```

Features:
- Validates JSON structure
- Merges with existing questions
- Preserves all metadata
- Returns total count after merge

**User Flow:**
1. Click user menu → "Export Dataset"
2. Browser downloads JSON file
3. To import: Click "Import Dataset"
4. Select JSON file from disk
5. System merges and confirms

---

## Phase 10 – Final Integration, Testing & Documentation

Phase 10 completes the system with comprehensive testing, final integrations, and production-ready deployment.

### 🧪 Testing Suite

**test_core_modules.py**
Location: `tests/test_core_modules.py`

**Test Coverage:**
- `TestChunker`: Text chunking functionality
  - Basic chunking
  - Empty text handling
  - Small text handling
  
- `TestValidator`: Question validation
  - Valid questions
  - Invalid questions
  - Duplicate detection
  
- `TestQualityScorer`: Quality scoring
  - High-quality questions
  - Multiple questions
  - Score sorting
  
- `TestUserManager`: User management
  - Login
  - Session tracking
  - Statistics

**Run Tests:**
```bash
python tests/test_core_modules.py

# Expected output:
# test_chunk_text_basic ... ok
# test_validate_valid_questions ... ok
# test_score_high_quality_question ... ok
# test_login ... ok
# ...
# Ran 12 tests in 2.3s
# OK
```

### 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    USER BROWSER                      │
│              (React SPA - Port 5173)                 │
└──────────────────┬───────────────────────────────────┘
                   │ HTTP/REST API
┌──────────────────▼───────────────────────────────────┐
│              FastAPI Backend (Port 8000)              │
│  ┌──────────┬───────────┬──────────┬──────────────┐ │
│  │Analytics │Generation │  Review  │ User Mgmt    │ │
│  │Endpoints │Endpoints  │Endpoints │ Endpoints    │ │
│  └──────────┴───────────┴──────────┴──────────────┘ │
└──────────────────┬──────────────────┬────────────────┘
                   │                  │
        ┌──────────▼────────┐    ┌───▼──────────┐
        │  Core Modules      │    │  Claude API   │
        │  - parser.py       │    │  (Anthropic)  │
        │  - chunker.py      │    └──────────────┘
        │  - generator.py    │
        │  - validator.py    │
        │  - quality_scorer.py│
        │  - reviewer.py     │
        │  - users.py        │
        └────────────────────┘
                   │
        ┌──────────▼────────┐
        │   Data Storage     │
        │  - questions.json  │
        │  - users.json      │
        │  - validation_report│
        │  - errors.log      │
        └────────────────────┘
```

### 📖 Complete API Reference

#### Analytics
- `GET /` - API information
- `GET /health` - Health check
- `GET /summary` - Question statistics
- `GET /validation-report` - Validation report
- `GET /questions?limit=N` - Get questions

#### Generation
- `POST /upload` - Upload PDF files
- `POST /generate` - Start generation (multi-topic)
- `GET /progress` - Get progress
- `GET /status` - Simple status
- `GET /files` - List uploaded files

#### Review (Phase 8)
- `POST /review` - Review question with Claude
- `PATCH /update-question/{id}` - Update question

#### Users (Phase 9)
- `POST /login` - Login/create user
- `POST /logout` - Logout
- `GET /sessions?username=X` - Get user history
- `GET /user-stats?username=X` - Get user stats

#### Export/Import
- `GET /export` - Download questions JSON
- `GET /download` - Alias for export
- `POST /import` - Import questions JSON

### 🚀 Deployment Guide

**Local Development:**
```bash
# Terminal 1: Backend
cd Questions-generator
python src/server.py

# Terminal 2: Frontend
cd Questions-generator/frontend
npm run dev
```

**Production Deployment:**
```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Start server (serves both API and static files)
cd ..
uvicorn src.server:app --host 0.0.0.0 --port 8000

# Access at: http://localhost:8000
```

**Cloud Deployment (Render, Railway, Heroku):**

1. **Render:**
   - Connect GitHub repository
   - Set build command: `cd frontend && npm install && npm run build`
   - Set start command: `uvicorn src.server:app --host 0.0.0.0 --port $PORT`
   - Add environment variable: `CLAUDE_API_KEY`

2. **Railway:**
   - Import from GitHub
   - Add `Procfile`: `web: uvicorn src.server:app --host 0.0.0.0 --port $PORT`
   - Set environment variables

3. **Docker:**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY . .
   
   RUN pip install -r requirements.txt
   RUN cd frontend && npm install && npm run build
   
   EXPOSE 8000
   CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

### 📊 Project Statistics

- **Total Files**: 30+
- **Lines of Code**: ~8,000
- **Phases Completed**: 10/10
- **Features**: 40+
- **API Endpoints**: 20+
- **UI Components**: 15+

### 🎯 Feature Checklist

#### Core Functionality ✓
- [x] PDF text extraction
- [x] Text chunking with overlap
- [x] Claude AI question generation
- [x] Multi-choice format (A/B/C/D)
- [x] Question validation
- [x] Quality scoring
- [x] JSON export

#### Advanced Features ✓
- [x] Multi-topic generation
- [x] Real-time progress tracking
- [x] AI-powered review
- [x] Question editing
- [x] User profiles
- [x] Session history
- [x] Dataset import/export

#### UI/UX ✓
- [x] Professional dashboard
- [x] Drag-and-drop upload
- [x] Animated modals
- [x] Progress panel
- [x] Review interface
- [x] User menu
- [x] Responsive design
- [x] Two-color theme

#### Deployment ✓
- [x] Production build
- [x] Static file serving
- [x] Error handling
- [x] Logging
- [x] Tests
- [x] Documentation

---

## Project Structure (Complete)

```
Questions-generator/
├── src/
│   ├── main.py              # CLI application entry point (Phases 1-4)
│   ├── parser.py            # PDF text extraction & cleaning (Phase 2)
│   ├── chunker.py           # Text chunking for AI processing (Phase 2)
│   ├── generator.py         # Claude AI question generation (Phase 3)
│   ├── validator.py         # Question validation & filtering (Phase 4)
│   ├── quality_scorer.py    # Quality scoring system (Phase 4)
│   ├── analytics.py         # FastAPI analytics backend (Phase 5)
│   └── utils/
│       ├── __init__.py
│       └── json_saver.py    # JSON validation & saving (Phase 3)
├── frontend/                # React dashboard (Phase 5)
│   ├── src/
│   │   ├── components/
│   │   │   ├── StatsCard.jsx
│   │   │   ├── ChartCard.jsx
│   │   │   └── ReportPanel.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── books/                   # Place your PDF files here
├── output/                  # Generated questions & reports
│   ├── questions.json       # Validated, scored questions
│   ├── validation_report.txt  # Validation statistics
│   └── errors.log           # Error log (created if issues occur)
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
