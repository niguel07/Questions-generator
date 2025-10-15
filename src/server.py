"""
Server API - Phase 5 & 6
FastAPI backend that serves analytics and handles file uploads + generation.
Provides endpoints for the React dashboard and interactive generation UI.
"""

import json
import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel


# Initialize FastAPI app
app = FastAPI(
    title="Question Generator Server API",
    description="API for analytics, file uploads, and question generation",
    version="2.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
QUESTIONS_FILE = Path("output/questions.json")
VALIDATION_REPORT_FILE = Path("output/validation_report.txt")
BOOKS_DIR = Path("books")

# Global state for generation progress
generation_state = {
    "status": "idle",  # idle, uploading, generating, completed, error
    "progress": 0,  # 0-100
    "message": "",
    "logs": [],
    "start_time": None,
    "end_time": None,
    "error": None
}


class GenerationRequest(BaseModel):
    """Request model for generation endpoint."""
    topic: str
    total_questions: int


def load_questions() -> list:
    """Load questions from JSON file."""
    if not QUESTIONS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Questions file not found. Please generate questions first."
        )
    
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        return questions
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid JSON in questions file"
        )


def calculate_summary(questions: list) -> Dict[str, Any]:
    """Calculate summary statistics from questions."""
    if not questions:
        return {
            "total_questions": 0,
            "avg_quality_score": 0.0,
            "categories": {},
            "difficulty": {},
            "quality_distribution": {
                "excellent": 0,
                "good": 0,
                "fair": 0,
                "poor": 0
            }
        }
    
    # Count categories
    categories = {}
    for q in questions:
        cat = q.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    # Count difficulty levels
    difficulty = {}
    for q in questions:
        diff = q.get("difficulty", "Unknown")
        difficulty[diff] = difficulty.get(diff, 0) + 1
    
    # Calculate average quality score
    quality_scores = [q.get("quality_score", 0.0) for q in questions]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    # Quality distribution
    excellent = sum(1 for s in quality_scores if s >= 0.9)
    good = sum(1 for s in quality_scores if 0.7 <= s < 0.9)
    fair = sum(1 for s in quality_scores if 0.5 <= s < 0.7)
    poor = sum(1 for s in quality_scores if s < 0.5)
    
    return {
        "total_questions": len(questions),
        "avg_quality_score": round(avg_quality, 3),
        "categories": categories,
        "difficulty": difficulty,
        "quality_distribution": {
            "excellent": excellent,
            "good": good,
            "fair": fair,
            "poor": poor
        }
    }


def update_progress(status: str, progress: int, message: str, add_log: bool = True):
    """Update global generation state."""
    generation_state["status"] = status
    generation_state["progress"] = progress
    generation_state["message"] = message
    
    if add_log:
        timestamp = datetime.now().strftime("%H:%M:%S")
        generation_state["logs"].append(f"[{timestamp}] {message}")


async def run_generation_process(topic: str, total_questions: int):
    """Run the question generation process in the background."""
    try:
        generation_state["start_time"] = datetime.now()
        generation_state["logs"] = []
        generation_state["error"] = None
        
        update_progress("generating", 10, f"Starting generation: {total_questions} questions on '{topic}'")
        
        # Build command
        cmd = [
            "python", "src/main.py",
            "--input-dir", "books",
            "--output-file", "output/questions.json",
            "--topic", topic,
            "--total-questions", str(total_questions)
        ]
        
        # Run the generation process
        update_progress("generating", 20, "Parsing PDF files...")
        
        # Use subprocess to run the generation
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Monitor progress
        progress_steps = {
            "Parsing": 30,
            "Chunking": 40,
            "Generating": 60,
            "Validation": 80,
            "Scoring": 90,
            "Saving": 95
        }
        
        current_progress = 20
        
        # Read output line by line
        for line in process.stdout:
            line = line.strip()
            if line:
                # Update progress based on keywords
                for keyword, prog in progress_steps.items():
                    if keyword.lower() in line.lower():
                        current_progress = prog
                        break
                
                update_progress("generating", current_progress, line)
                await asyncio.sleep(0.1)  # Small delay for UI updates
        
        # Wait for process to complete
        return_code = process.wait()
        
        if return_code == 0:
            generation_state["end_time"] = datetime.now()
            update_progress("completed", 100, "✓ Generation completed successfully!")
        else:
            error_msg = process.stderr.read() if process.stderr else "Unknown error"
            generation_state["error"] = error_msg
            update_progress("error", 0, f"✗ Generation failed: {error_msg}")
            
    except Exception as e:
        generation_state["error"] = str(e)
        update_progress("error", 0, f"✗ Error: {str(e)}")


# ============================================================================
# ANALYTICS ENDPOINTS (Phase 5)
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Question Generator Server API",
        "version": "2.0.0",
        "endpoints": {
            "analytics": {
                "/summary": "Get question statistics summary",
                "/validation-report": "Get validation report text",
                "/questions": "Get sample questions",
                "/health": "Health check endpoint"
            },
            "generation": {
                "/upload": "Upload PDF files",
                "/generate": "Start question generation",
                "/progress": "Get generation progress",
                "/status": "Get current status"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "questions_file_exists": QUESTIONS_FILE.exists(),
        "validation_report_exists": VALIDATION_REPORT_FILE.exists(),
        "books_directory_exists": BOOKS_DIR.exists()
    }


@app.get("/summary")
async def get_summary():
    """Get summary statistics for generated questions."""
    questions = load_questions()
    summary = calculate_summary(questions)
    return JSONResponse(content=summary)


@app.get("/validation-report")
async def get_validation_report():
    """Get validation report text."""
    if not VALIDATION_REPORT_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Validation report not found. Please run validation first."
        )
    
    try:
        with open(VALIDATION_REPORT_FILE, 'r', encoding='utf-8') as f:
            report = f.read()
        return PlainTextResponse(content=report)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading validation report: {str(e)}"
        )


@app.get("/questions")
async def get_questions(limit: int = 10):
    """Get sample questions."""
    questions = load_questions()
    return JSONResponse(content={
        "total": len(questions),
        "limit": limit,
        "questions": questions[:limit]
    })


# ============================================================================
# GENERATION ENDPOINTS (Phase 6)
# ============================================================================

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload PDF files to the books directory.
    Accepts multiple files, max 50MB each.
    """
    # Ensure books directory exists
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Check file extension
            if not file.filename.lower().endswith('.pdf'):
                errors.append(f"{file.filename}: Not a PDF file")
                continue
            
            # Read file content
            content = await file.read()
            
            # Check file size (50MB limit)
            if len(content) > 50 * 1024 * 1024:
                errors.append(f"{file.filename}: File too large (>50MB)")
                continue
            
            # Save file
            file_path = BOOKS_DIR / file.filename
            with open(file_path, 'wb') as f:
                f.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "path": str(file_path)
            })
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    return JSONResponse(content={
        "uploaded": uploaded_files,
        "errors": errors,
        "total_uploaded": len(uploaded_files),
        "total_errors": len(errors)
    })


@app.post("/generate")
async def start_generation(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start the question generation process.
    Runs in the background and provides progress updates.
    """
    # Check if generation is already running
    if generation_state["status"] == "generating":
        raise HTTPException(
            status_code=409,
            detail="Generation already in progress"
        )
    
    # Validate input
    if request.total_questions < 100 or request.total_questions > 10000:
        raise HTTPException(
            status_code=400,
            detail="Total questions must be between 100 and 10,000"
        )
    
    if not request.topic or len(request.topic.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty"
        )
    
    # Check if books directory has PDF files
    if not BOOKS_DIR.exists() or not list(BOOKS_DIR.glob("*.pdf")):
        raise HTTPException(
            status_code=400,
            detail="No PDF files found in books directory. Please upload files first."
        )
    
    # Reset state
    generation_state["status"] = "starting"
    generation_state["progress"] = 0
    generation_state["message"] = "Initializing..."
    generation_state["logs"] = []
    generation_state["error"] = None
    
    # Start generation in background
    background_tasks.add_task(
        run_generation_process,
        request.topic,
        request.total_questions
    )
    
    return JSONResponse(content={
        "status": "started",
        "message": "Generation process started",
        "topic": request.topic,
        "total_questions": request.total_questions
    })


@app.get("/progress")
async def get_progress():
    """Get current generation progress."""
    duration = None
    if generation_state["start_time"]:
        end = generation_state["end_time"] or datetime.now()
        duration = (end - generation_state["start_time"]).total_seconds()
    
    return JSONResponse(content={
        "status": generation_state["status"],
        "progress": generation_state["progress"],
        "message": generation_state["message"],
        "logs": generation_state["logs"][-20:],  # Last 20 log entries
        "error": generation_state["error"],
        "duration_seconds": duration
    })


@app.get("/status")
async def get_status():
    """Get simple status (for polling)."""
    return JSONResponse(content={
        "status": generation_state["status"],
        "progress": generation_state["progress"],
        "message": generation_state["message"]
    })


@app.get("/files")
async def list_uploaded_files():
    """List all uploaded PDF files in books directory."""
    if not BOOKS_DIR.exists():
        return JSONResponse(content={"files": []})
    
    files = []
    for pdf_file in BOOKS_DIR.glob("*.pdf"):
        stat = pdf_file.stat()
        files.append({
            "filename": pdf_file.name,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    return JSONResponse(content={
        "files": files,
        "total": len(files)
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

