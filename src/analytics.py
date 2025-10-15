"""
Analytics API - Phase 5
FastAPI backend that serves question generation statistics and reports.
Provides endpoints for the React dashboard to consume.
"""

import json
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse


# Initialize FastAPI app
app = FastAPI(
    title="Question Generator Analytics API",
    description="API for serving question generation statistics and validation reports",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
QUESTIONS_FILE = Path("output/questions.json")
VALIDATION_REPORT_FILE = Path("output/validation_report.txt")


def load_questions() -> list:
    """
    Load questions from JSON file.
    
    Returns:
        List of question dictionaries
        
    Raises:
        HTTPException: If file not found or invalid JSON
    """
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
    """
    Calculate summary statistics from questions.
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
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


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Question Generator Analytics API",
        "version": "1.0.0",
        "endpoints": {
            "/summary": "Get question statistics summary",
            "/validation-report": "Get validation report text",
            "/health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "questions_file_exists": QUESTIONS_FILE.exists(),
        "validation_report_exists": VALIDATION_REPORT_FILE.exists()
    }


@app.get("/summary")
async def get_summary():
    """
    Get summary statistics for generated questions.
    
    Returns:
        JSON with total questions, average quality score,
        category distribution, and difficulty distribution
    """
    questions = load_questions()
    summary = calculate_summary(questions)
    
    return JSONResponse(content=summary)


@app.get("/validation-report")
async def get_validation_report():
    """
    Get validation report text.
    
    Returns:
        Plain text validation report
    """
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
    """
    Get sample questions.
    
    Args:
        limit: Number of questions to return (default: 10)
        
    Returns:
        JSON with sample questions
    """
    questions = load_questions()
    
    return JSONResponse(content={
        "total": len(questions),
        "limit": limit,
        "questions": questions[:limit]
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

