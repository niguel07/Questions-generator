"""
Server API - Phases 5-10
Comprehensive FastAPI backend with analytics, file uploads, generation,
AI review, user management, and dataset export/import.
"""

import json
import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging

# Import our custom modules
from reviewer import QuestionReviewer
from users import UserManager
from auth import AuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Question Generator AI - Complete System",
    description="Full-featured API for question generation, review, and management",
    version="3.0.0"
)

# CORS configuration - Allow all local ports for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File paths
QUESTIONS_FILE = Path("output/questions.json")
VALIDATION_REPORT_FILE = Path("output/validation_report.txt")
BOOKS_DIR = Path("books")

# Initialize managers
reviewer = QuestionReviewer()
user_manager = UserManager()
auth_manager = AuthManager()

# Global state
generation_state = {
    "status": "idle",
    "progress": 0,
    "message": "",
    "logs": [],
    "start_time": None,
    "end_time": None,
    "error": None,
    "current_user": None
}

current_session = {
    "user": None
}


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GenerationRequest(BaseModel):
    """Request model for multi-topic generation."""
    topics: List[str]
    total_questions: int

class ReviewRequest(BaseModel):
    """Request model for question review."""
    question: str
    options: Dict[str, str]
    answer: str
    explanation: str
    category: str
    difficulty: str

class QuestionUpdate(BaseModel):
    """Request model for updating a question."""
    question: Optional[str] = None
    options: Optional[Dict[str, str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None

class SignupRequest(BaseModel):
    """Request model for user signup."""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    """Request model for user login."""
    username_or_email: str
    password: str

class SessionVerifyRequest(BaseModel):
    """Request model for session verification."""
    session_token: str


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_questions() -> list:
    """Load questions from JSON file."""
    if not QUESTIONS_FILE.exists():
        return []
    
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        return questions
    except json.JSONDecodeError:
        logger.error("Invalid JSON in questions file")
        return []

def save_questions(questions: list):
    """Save questions to JSON file."""
    QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def calculate_summary(questions: list) -> Dict[str, Any]:
    """Calculate summary statistics from questions."""
    if not questions:
        return {
            "total_questions": 0,
            "avg_quality_score": 0.0,
            "categories": {},
            "difficulty": {},
            "quality_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        }
    
    categories = {}
    for q in questions:
        cat = q.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    difficulty = {}
    for q in questions:
        diff = q.get("difficulty", "Unknown")
        difficulty[diff] = difficulty.get(diff, 0) + 1
    
    quality_scores = [q.get("quality_score", 0.0) for q in questions]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
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
        logger.info(message)

async def run_generation_process(topics: List[str], total_questions: int, username: Optional[str] = None):
    """Run the question generation process for multiple topics."""
    try:
        generation_state["start_time"] = datetime.now()
        generation_state["logs"] = []
        generation_state["error"] = None
        generation_state["current_user"] = username
        
        update_progress("generating", 10, f"Starting generation: {total_questions} questions on {len(topics)} topic(s)")
        
        # Generate questions per topic
        questions_per_topic = total_questions // len(topics)
        
        for idx, topic in enumerate(topics):
            topic_progress_start = 10 + (idx * 80 // len(topics))
            update_progress("generating", topic_progress_start, f"Generating questions for topic: {topic}")
            
            # Build command for this topic
            cmd = [
                "python", "src/main.py",
                "--input-dir", "books",
                "--output-file", f"output/questions_{topic.replace(' ', '_')}.json",
                "--topic", topic,
                "--total-questions", str(questions_per_topic)
            ]
            
            # Run generation
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                line = line.strip()
                if line:
                    current_prog = topic_progress_start + (idx + 1) * 60 // len(topics)
                    update_progress("generating", current_prog, line)
                    await asyncio.sleep(0.1)
            
            process.wait()
            
            if process.returncode != 0:
                error_msg = process.stderr.read() if process.stderr else "Unknown error"
                generation_state["error"] = f"Failed for topic '{topic}': {error_msg}"
                update_progress("error", 0, f"✗ Generation failed for topic: {topic}")
                return
        
        # Merge all topic files
        update_progress("generating", 90, "Merging questions from all topics...")
        all_questions = []
        for topic in topics:
            topic_file = Path(f"output/questions_{topic.replace(' ', '_')}.json")
            if topic_file.exists():
                with open(topic_file, 'r', encoding='utf-8') as f:
                    topic_questions = json.load(f)
                    # Add topic field to each question
                    for q in topic_questions:
                        q['source_topic'] = topic
                    all_questions.extend(topic_questions)
                topic_file.unlink()  # Delete temporary file
        
        # Save merged questions
        save_questions(all_questions)
        
        generation_state["end_time"] = datetime.now()
        update_progress("completed", 100, f"✓ Generated {len(all_questions)} questions successfully!")
        
        # Log session for user
        if username:
            user_manager.add_session(username, {
                "topics": topics,
                "questions_generated": len(all_questions),
                "avg_quality": calculate_summary(all_questions)["avg_quality_score"],
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        generation_state["error"] = str(e)
        update_progress("error", 0, f"✗ Error: {str(e)}")
        logger.error(f"Generation error: {e}")


# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Question Generator AI - Complete System",
        "version": "3.0.0",
        "phases": ["1-10 Complete"],
        "endpoints": {
            "analytics": ["/summary", "/validation-report", "/questions", "/health"],
            "generation": ["/upload", "/generate", "/progress", "/status", "/files"],
            "review": ["/review", "/update-question/{id}"],
            "users": ["/login", "/logout", "/sessions", "/user-stats"],
            "export": ["/export", "/import", "/download"]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "questions_file_exists": QUESTIONS_FILE.exists(),
        "books_directory_exists": BOOKS_DIR.exists(),
        "reviewer_initialized": reviewer is not None,
        "user_manager_initialized": user_manager is not None
    }


# ============================================================================
# ANALYTICS ENDPOINTS (Phase 5)
# ============================================================================

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
        raise HTTPException(status_code=404, detail="Validation report not found")
    
    with open(VALIDATION_REPORT_FILE, 'r', encoding='utf-8') as f:
        report = f.read()
    return PlainTextResponse(content=report)

@app.get("/questions")
async def get_questions(limit: int = 100):
    """Get questions with optional limit."""
    questions = load_questions()
    return JSONResponse(content={
        "total": len(questions),
        "limit": limit,
        "questions": questions[:limit]
    })


# ============================================================================
# GENERATION ENDPOINTS (Phase 6-7)
# ============================================================================

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload PDF files to the books directory."""
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            if not file.filename.lower().endswith('.pdf'):
                errors.append(f"{file.filename}: Not a PDF file")
                continue
            
            content = await file.read()
            
            if len(content) > 50 * 1024 * 1024:
                errors.append(f"{file.filename}: File too large (>50MB)")
                continue
            
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
async def start_generation(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Start multi-topic question generation."""
    if generation_state["status"] == "generating":
        raise HTTPException(status_code=409, detail="Generation already in progress")
    
    if request.total_questions < 100 or request.total_questions > 10000:
        raise HTTPException(status_code=400, detail="Total questions must be between 100 and 10,000")
    
    if not request.topics or len(request.topics) == 0:
        raise HTTPException(status_code=400, detail="At least one topic is required")
    
    if not BOOKS_DIR.exists() or not list(BOOKS_DIR.glob("*.pdf")):
        raise HTTPException(status_code=400, detail="No PDF files found. Please upload files first.")
    
    generation_state["status"] = "starting"
    generation_state["progress"] = 0
    generation_state["logs"] = []
    generation_state["error"] = None
    
    background_tasks.add_task(
        run_generation_process,
        request.topics,
        request.total_questions,
        current_session.get("user")
    )
    
    return JSONResponse(content={
        "status": "started",
        "message": f"Generation started for {len(request.topics)} topic(s)",
        "topics": request.topics,
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
        "logs": generation_state["logs"][-20:],
        "error": generation_state["error"],
        "duration_seconds": duration
    })

@app.get("/status")
async def get_status():
    """Get simple status."""
    return JSONResponse(content={
        "status": generation_state["status"],
        "progress": generation_state["progress"],
        "message": generation_state["message"]
    })

@app.get("/files")
async def list_uploaded_files():
    """List all uploaded PDF files."""
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
    
    return JSONResponse(content={"files": files, "total": len(files)})


# ============================================================================
# REVIEW ENDPOINTS (Phase 8)
# ============================================================================

@app.post("/review")
async def review_question(request: ReviewRequest):
    """Review a question using Claude AI."""
    try:
        question_data = {
            "question": request.question,
            "options": request.options,
            "answer": request.answer,
            "explanation": request.explanation,
            "category": request.category,
            "difficulty": request.difficulty
        }
        
        result = reviewer.review_question(question_data)
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/update-question/{question_id}")
async def update_question(question_id: int, update: QuestionUpdate):
    """Update a specific question in the dataset."""
    questions = load_questions()
    
    if question_id < 0 or question_id >= len(questions):
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Update fields
    if update.question is not None:
        questions[question_id]["question"] = update.question
    if update.options is not None:
        questions[question_id]["options"] = update.options
    if update.answer is not None:
        questions[question_id]["answer"] = update.answer
    if update.explanation is not None:
        questions[question_id]["explanation"] = update.explanation
    if update.category is not None:
        questions[question_id]["category"] = update.category
    if update.difficulty is not None:
        questions[question_id]["difficulty"] = update.difficulty
    
    # Add metadata
    questions[question_id]["last_updated"] = datetime.now().isoformat()
    questions[question_id]["updated_by_reviewer"] = True
    
    save_questions(questions)
    
    return JSONResponse(content={
        "success": True,
        "message": "Question updated successfully",
        "question": questions[question_id]
    })


# ============================================================================
# AUTHENTICATION ENDPOINTS (Enhanced Phase 9)
# ============================================================================

@app.post("/auth/signup")
async def signup(request: SignupRequest):
    """Register a new user account."""
    try:
        result = auth_manager.signup(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        if result["success"]:
            current_session["user"] = request.username
            # Create user profile in user_manager
            user_manager.login(request.username)
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Authenticate user and create session."""
    try:
        result = auth_manager.login(
            username_or_email=request.username_or_email,
            password=request.password
        )
        
        if result["success"]:
            current_session["user"] = result["user"]["username"]
            # Ensure user profile exists
            user_manager.login(result["user"]["username"])
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/verify")
async def verify_session(request: SessionVerifyRequest):
    """Verify if session token is valid."""
    result = auth_manager.verify_session(request.session_token)
    return JSONResponse(content=result)

@app.post("/auth/logout")
async def logout(request: SessionVerifyRequest):
    """Logout user and invalidate session."""
    result = auth_manager.logout(request.session_token)
    current_session["user"] = None
    return JSONResponse(content=result)

# Legacy endpoints for backward compatibility
@app.post("/login")
async def legacy_login(request: dict):
    """Legacy login endpoint - redirects to new auth."""
    if "username" in request:
        # Old simple login
        result = user_manager.login(request["username"])
        if result["success"]:
            current_session["user"] = request["username"]
        return JSONResponse(content=result)
    return JSONResponse(content={"success": False, "error": "Invalid request"})

@app.post("/logout")
async def legacy_logout():
    """Legacy logout endpoint."""
    current_session["user"] = None
    return JSONResponse(content={"success": True, "message": "Logged out successfully"})

@app.get("/sessions")
async def get_user_sessions(username: str, limit: int = 50):
    """Get user's generation history."""
    sessions = user_manager.get_sessions(username, limit)
    return JSONResponse(content={"username": username, "sessions": sessions, "total": len(sessions)})

@app.get("/user-stats")
async def get_user_stats(username: str):
    """Get user statistics."""
    stats = user_manager.get_stats(username)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return JSONResponse(content=stats)


# ============================================================================
# EXPORT/IMPORT ENDPOINTS (Phase 9)
# ============================================================================

@app.get("/export")
async def export_questions():
    """Export questions JSON file."""
    if not QUESTIONS_FILE.exists():
        raise HTTPException(status_code=404, detail="No questions to export")
    
    return FileResponse(
        QUESTIONS_FILE,
        media_type="application/json",
        filename=f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

@app.get("/download")
async def download_questions():
    """Download questions JSON file."""
    return await export_questions()

@app.post("/import")
async def import_questions(file: UploadFile = File(...)):
    """Import questions from JSON file."""
    try:
        content = await file.read()
        imported_questions = json.loads(content)
        
        if not isinstance(imported_questions, list):
            raise HTTPException(status_code=400, detail="Invalid format: expected array of questions")
        
        # Merge with existing questions
        existing_questions = load_questions()
        merged = existing_questions + imported_questions
        
        save_questions(merged)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Imported {len(imported_questions)} questions",
            "total_questions": len(merged)
        })
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STATIC FILES (Phase 7 - Production)
# ============================================================================

# Serve static frontend build (if exists)
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory=frontend_dist / "assets"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React frontend for production."""
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
