from typing import Dict, Literal

from pydantic import BaseModel, Field


TrainingMode = Literal["LOW", "HIGH"]
NoiseProfile = Literal["none", "white", "cafe", "street", "speech_babble"]


class Difficulty(BaseModel):
    speed: float = Field(..., examples=[1.0])
    snr: float = Field(..., examples=[20.0])


class TaskDifficulty(Difficulty):
    noise_profile: NoiseProfile = "none"


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class InitSessionRequest(BaseModel):
    user_id: str
    training_mode: TrainingMode = "LOW"
    noise_profile: NoiseProfile = "none"


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    training_mode: TrainingMode
    difficulty: Difficulty


class TaskResponse(BaseModel):
    task_id: str
    session_id: str
    text_hash: str
    target_text: str
    audio_url: str
    difficulty: TaskDifficulty


class AnswerRequest(BaseModel):
    session_id: str
    task_id: str
    user_input: str


class LegacyAnswerRequest(BaseModel):
    user_id: str
    target_text: str
    user_input: str


class AnswerResponse(BaseModel):
    correct: bool
    score: float
    message: str
    new_difficulty: Difficulty


class ProgressResponse(BaseModel):
    user_id: str
    total_answers: int
    correct_count: int
    accuracy: float
    current_difficulty: Difficulty


SessionStore = Dict[str, object]
