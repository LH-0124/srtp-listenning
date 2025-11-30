from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import sqlite3
import os
from server.models import InitSessionRequest, AnswerRequest
from server.adaptive_logic import PatientState
from server.audio_service import AudioService

app = FastAPI()

# 挂载 assets 目录，让前端可以通过 URL 访问音频
# 例如: http://localhost:8000/static/task_xxx.wav
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
app.mount("/static", StaticFiles(directory=ASSETS_DIR), name="static")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'capd_database.db')

# 内存 Session 存储 (生产环境请用 Redis)
sessions = {}

@app.post("/start")
def start_session(req: InitSessionRequest):
    sessions[req.user_id] = {
        "state": PatientState(),
        "mode": req.training_mode
    }
    return {"message": "Session started", "config": req.training_mode}

@app.get("/next_task")
async def get_next_task(user_id: str):
    if user_id not in sessions:
        raise HTTPException(status_code=400, detail="User session not found")
    
    session_data = sessions[user_id]
    state = session_data["state"]
    mode = session_data["mode"] # 'HIGH' or 'LOW'
    
    # 1. 从数据库取题
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT text FROM sentences WHERE context_type=? ORDER BY RANDOM() LIMIT 1", (mode,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Database empty. Please run data pipeline first."}
    
    text = row[0]
    
    # 2. 生成音频
    filename = await AudioService.generate_task_audio(text, state.speed, state.snr)
    
    # 3. 返回 URL 给前端
    return {
        "target_text": text, # 实际开发中可以加密这个字段
        "audio_url": f"/static/{filename}",
        "difficulty": {
            "speed": round(state.speed, 2),
            "snr": round(state.snr, 2)
        }
    }

@app.post("/submit")
def submit_answer(req: AnswerRequest):
    if req.user_id not in sessions:
        raise HTTPException(status_code=400, detail="Session not found")
    
    state = sessions[req.user_id]["state"]
    
    # 简单的判分逻辑
    is_correct = (req.user_input.strip() == req.target_text.strip())
    
    # 调整难度
    result = state.adjust(is_correct)
    
    return result