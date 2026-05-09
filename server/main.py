import hashlib
import os
import sqlite3
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from server.adaptive_logic import PatientState
from server.audio_service import AudioService
from server.models import (
    AnswerRequest,
    AnswerResponse,
    Difficulty,
    HealthResponse,
    InitSessionRequest,
    LegacyAnswerRequest,
    ProgressResponse,
    SessionResponse,
    TaskDifficulty,
    TaskResponse,
)

SERVICE_NAME = "srtp-capd-backend"
SERVICE_VERSION = "0.1.0"
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
DB_PATH = os.path.join(ROOT_DIR, "capd_database.db")

app = FastAPI(title="SRTP-CAPD Backend API", version=SERVICE_VERSION)

os.makedirs(ASSETS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=ASSETS_DIR), name="static")

sessions = {}
tasks = {}
user_progress = {}


def _difficulty_from_state(state: PatientState) -> Difficulty:
    return Difficulty(speed=round(state.speed, 2), snr=round(state.snr, 2))


def _get_session(session_id: str) -> dict:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]


def _select_sentence(training_mode: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text FROM sentences WHERE context_type=? ORDER BY RANDOM() LIMIT 1",
            (training_mode,),
        )
        row = cursor.fetchone()
        if row is None:
            cursor.execute("SELECT text FROM sentences ORDER BY RANDOM() LIMIT 1")
            row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(
            status_code=503,
            detail="No training sentences available. Please run data pipeline first.",
        )
    return row[0]


def _record_answer(user_id: str, is_correct: bool, state: PatientState) -> None:
    progress = user_progress.setdefault(
        user_id,
        {"total_answers": 0, "correct_count": 0, "state": state},
    )
    progress["total_answers"] += 1
    if is_correct:
        progress["correct_count"] += 1
    progress["state"] = state


def _answer_response(is_correct: bool, adjustment: dict) -> AnswerResponse:
    new_params = adjustment["new_params"]
    return AnswerResponse(
        correct=is_correct,
        score=1.0 if is_correct else 0.0,
        message=adjustment["msg"],
        new_difficulty=Difficulty(
            speed=round(new_params["speed"], 2),
            snr=round(new_params["snr"], 2),
        ),
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service=SERVICE_NAME, version=SERVICE_VERSION)


@app.post("/api/v1/sessions", response_model=SessionResponse)
def create_session(req: InitSessionRequest) -> SessionResponse:
    session_id = str(uuid.uuid4())
    state = PatientState()
    sessions[session_id] = {
        "user_id": req.user_id,
        "state": state,
        "training_mode": req.training_mode,
        "noise_profile": req.noise_profile,
    }
    user_progress.setdefault(
        req.user_id,
        {"total_answers": 0, "correct_count": 0, "state": state},
    )

    return SessionResponse(
        session_id=session_id,
        user_id=req.user_id,
        training_mode=req.training_mode,
        difficulty=_difficulty_from_state(state),
    )


@app.get("/api/v1/tasks/next", response_model=TaskResponse)
async def get_next_task_v1(session_id: str, request: Request) -> TaskResponse:
    session = _get_session(session_id)
    state = session["state"]
    text = _select_sentence(session["training_mode"])
    filename = await AudioService.generate_task_audio(text, state.speed, state.snr)
    task_id = str(uuid.uuid4())
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    tasks[task_id] = {
        "session_id": session_id,
        "target_text": text,
        "text_hash": text_hash,
    }

    return TaskResponse(
        task_id=task_id,
        session_id=session_id,
        text_hash=text_hash,
        target_text=text,
        audio_url=str(request.url_for("static", path=filename)),
        difficulty=TaskDifficulty(
            speed=round(state.speed, 2),
            snr=round(state.snr, 2),
            noise_profile=session["noise_profile"],
        ),
    )


@app.post("/api/v1/answers", response_model=AnswerResponse)
def submit_answer_v1(req: AnswerRequest) -> AnswerResponse:
    session = _get_session(req.session_id)
    task = tasks.get(req.task_id)
    if not task or task["session_id"] != req.session_id:
        raise HTTPException(status_code=404, detail="Task not found for session")

    state = session["state"]
    is_correct = req.user_input.strip() == task["target_text"].strip()
    adjustment = state.adjust(is_correct)
    _record_answer(session["user_id"], is_correct, state)
    return _answer_response(is_correct, adjustment)


@app.get("/api/v1/users/{user_id}/progress", response_model=ProgressResponse)
def get_user_progress(user_id: str) -> ProgressResponse:
    progress = user_progress.get(user_id)
    if progress is None:
        progress = {"total_answers": 0, "correct_count": 0, "state": PatientState()}

    total_answers = progress["total_answers"]
    correct_count = progress["correct_count"]
    accuracy = correct_count / total_answers if total_answers else 0.0

    return ProgressResponse(
        user_id=user_id,
        total_answers=total_answers,
        correct_count=correct_count,
        accuracy=round(accuracy, 4),
        current_difficulty=_difficulty_from_state(progress["state"]),
    )


@app.post("/start")
def start_session(req: InitSessionRequest):
    session = create_session(req)
    return {"message": "Session started", "config": session.training_mode}


@app.get("/next_task")
async def get_next_task(user_id: str, request: Request):
    session_id = next(
        (sid for sid, session in sessions.items() if session["user_id"] == user_id),
        None,
    )
    if session_id is None:
        raise HTTPException(status_code=400, detail="User session not found")
    return await get_next_task_v1(session_id, request)


@app.post("/submit")
def submit_answer(req: LegacyAnswerRequest):
    session_id = next(
        (sid for sid, session in sessions.items() if session["user_id"] == req.user_id),
        None,
    )
    if session_id is None:
        raise HTTPException(status_code=400, detail="Session not found")

    session = sessions[session_id]
    state = session["state"]
    is_correct = req.user_input.strip() == req.target_text.strip()
    adjustment = state.adjust(is_correct)
    _record_answer(req.user_id, is_correct, state)
    return _answer_response(is_correct, adjustment)
