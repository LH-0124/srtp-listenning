from pydantic import BaseModel
from typing import Optional

class InitSessionRequest(BaseModel):
    user_id: str
    training_mode: str = "LOW"  # 'LOW' (解码) or 'HIGH' (闭合)

class AnswerRequest(BaseModel):
    user_id: str
    target_text: str # 题目原句
    user_input: str  # 用户听写的句子

class TaskResponse(BaseModel):
    text_hash: str
    audio_url: str
    difficulty_info: dict