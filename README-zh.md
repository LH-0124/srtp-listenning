# SRTP-CAPD 后端 MVP

这是面向 CAPD 听力康复小程序的后端 MVP。服务提供稳定的 `/api/v1` API，使用 SQLite 保存用户训练历史，生成训练音频，包含离线语料处理 pipeline，并在根路径 `/` 提供本地前端演示页。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m compileall -q data_pipeline server tests
pytest -q
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

启动后访问：

- `http://127.0.0.1:8000/`：本地前端 demo
- `http://127.0.0.1:8000/openapi.json`：OpenAPI JSON
- `http://127.0.0.1:8000/docs`：Swagger 文档

## 核心 API

- `GET /health`
- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`

请求和响应字段见 `docs/API_CONTRACT.md`。

## 本地前端 Demo

前端静态文件位于：

- `web/index.html`
- `web/styles.css`
- `web/app.js`

页面支持创建 session、获取任务、播放返回的 `audio_url`、提交答案、刷新进度，并显示 API 调试信息和 loading/error/success/empty 状态。小程序或前端接入说明见 `docs/FRONTEND_INTEGRATION.md`。

注意：`GET /api/v1/tasks/next` 会调用 `edge-tts`。如果当前网络无法访问 TTS 服务，页面会保留 session 并显示可重试的任务/音频错误。

## 本地冒烟测试

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

启动 uvicorn 后运行 API smoke：

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_smoke
```

运行快速离线 pipeline smoke：

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

## 演示指南

完整演示步骤见 `docs/DEMO_RUNBOOK.md`。
