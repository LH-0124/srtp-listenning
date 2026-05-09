import hashlib
import os
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
from server.user_data_store import (
    create_training_session,
    create_training_task,
    get_latest_session_for_user,
    get_training_session,
    get_training_task,
    get_user_progress as get_persisted_user_progress,
    init_user_data_db,
    record_answer,
    select_sentence,
    update_session_difficulty,
)

SERVICE_NAME = "srtp-capd-backend"
SERVICE_VERSION = "0.1.0"
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
DB_PATH = os.path.join(ROOT_DIR, "capd_database.db")

app = FastAPI(title="SRTP-CAPD Backend API", version=SERVICE_VERSION)

os.makedirs(ASSETS_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=ASSETS_DIR), name="static")
init_user_data_db(DB_PATH)

sessions = {}
tasks = {}


def _difficulty_from_state(state: PatientState) -> Difficulty:
    return Difficulty(speed=round(state.speed, 2), snr=round(state.snr, 2))


def _state_from_values(speed: float, snr: float) -> PatientState:
    state = PatientState()
    state.speed = speed
    state.snr = snr
    return state


def _get_session(session_id: str) -> dict:
    session = sessions.get(session_id)
    if session:
        return session

    persisted = get_training_session(session_id, DB_PATH)
    if persisted is None:
        raise HTTPException(status_code=404, detail="Session not found")
    state = _state_from_values(persisted["speed"], persisted["snr"])
    session = {
        "user_id": persisted["user_id"],
        "state": state,
        "training_mode": persisted["training_mode"],
        "noise_profile": persisted["noise_profile"],
    }
    sessions[session_id] = session
    return session


def _select_training_sentence(training_mode: str) -> dict:
    row = select_sentence(training_mode, DB_PATH)
    if row is None:
        raise HTTPException(
            status_code=503,
            detail="No training sentences available. Please run data pipeline first.",
        )
    return row


def _persist_answer(
    *,
    session_id: str,
    task_id: str,
    user_id: str,
    user_input: str,
    target_text: str,
    is_correct: bool,
    state: PatientState,
) -> None:
    score = 1.0 if is_correct else 0.0
    update_session_difficulty(session_id, state.speed, state.snr, DB_PATH)
    record_answer(
        answer_id=str(uuid.uuid4()),
        session_id=session_id,
        task_id=task_id,
        user_id=user_id,
        user_input=user_input,
        target_text=target_text,
        correct=is_correct,
        score=score,
        current_speed=state.speed,
        current_snr=state.snr,
        db_path=DB_PATH,
    )


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
    create_training_session(
        session_id=session_id,
        user_id=req.user_id,
        training_mode=req.training_mode,
        noise_profile=req.noise_profile,
        speed=state.speed,
        snr=state.snr,
        db_path=DB_PATH,
    )
    sessions[session_id] = {
        "user_id": req.user_id,
        "state": state,
        "training_mode": req.training_mode,
        "noise_profile": req.noise_profile,
    }

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
    sentence = _select_training_sentence(session["training_mode"])
    text = sentence["text"]
    filename = await AudioService.generate_task_audio(
        text,
        state.speed,
        state.snr,
        noise_profile=session["noise_profile"],
    )
    task_id = str(uuid.uuid4())
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    audio_url = str(request.url_for("static", path=filename))

    tasks[task_id] = {
        "session_id": session_id,
        "target_text": text,
        "text_hash": text_hash,
    }
    create_training_task(
        task_id=task_id,
        session_id=session_id,
        sentence_id=sentence["id"],
        target_text=text,
        audio_url=audio_url,
        speed=state.speed,
        snr=state.snr,
        noise_profile=session["noise_profile"],
        db_path=DB_PATH,
    )

    return TaskResponse(
        task_id=task_id,
        session_id=session_id,
        text_hash=text_hash,
        target_text=text,
        audio_url=audio_url,
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
    if task is None:
        task = get_training_task(req.task_id, DB_PATH)
    if not task or task["session_id"] != req.session_id:
        raise HTTPException(status_code=404, detail="Task not found for session")

    state = session["state"]
    is_correct = req.user_input.strip() == task["target_text"].strip()
    adjustment = state.adjust(is_correct)
    _persist_answer(
        session_id=req.session_id,
        task_id=req.task_id,
        user_id=session["user_id"],
        user_input=req.user_input,
        target_text=task["target_text"],
        is_correct=is_correct,
        state=state,
    )
    return _answer_response(is_correct, adjustment)


@app.get("/api/v1/users/{user_id}/progress", response_model=ProgressResponse)
def get_user_progress(user_id: str) -> ProgressResponse:
    progress = get_persisted_user_progress(user_id, DB_PATH)
    total_answers = progress["total_answers"]
    correct_count = progress["correct_count"]

    return ProgressResponse(
        user_id=user_id,
        total_answers=total_answers,
        correct_count=correct_count,
        accuracy=round(progress["accuracy"], 4),
        current_difficulty=Difficulty(
            speed=round(progress["current_speed"], 2),
            snr=round(progress["current_snr"], 2),
        ),
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
        persisted = get_latest_session_for_user(user_id, DB_PATH)
        session_id = persisted["session_id"] if persisted else None
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
        persisted = get_latest_session_for_user(req.user_id, DB_PATH)
        session_id = persisted["session_id"] if persisted else None
    if session_id is None:
        raise HTTPException(status_code=400, detail="Session not found")

    session = _get_session(session_id)
    state = session["state"]
    is_correct = req.user_input.strip() == req.target_text.strip()
    adjustment = state.adjust(is_correct)
    task_id = str(uuid.uuid4())
    create_training_task(
        task_id=task_id,
        session_id=session_id,
        sentence_id=None,
        target_text=req.target_text,
        audio_url=None,
        speed=state.speed,
        snr=state.snr,
        noise_profile=session["noise_profile"],
        db_path=DB_PATH,
    )
    _persist_answer(
        session_id=session_id,
        task_id=task_id,
        user_id=req.user_id,
        user_input=req.user_input,
        target_text=req.target_text,
        is_correct=is_correct,
        state=state,
    )
    return _answer_response(is_correct, adjustment)
