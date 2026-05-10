# SRTP-CAPD 后端 MVP

本仓库是面向 CAPD 听觉康复小程序的后端 MVP。项目提供稳定的 `/api/v1` API、SQLite 训练数据持久化、训练音频生成、离线语料处理 pipeline，并在根路径 `/` 提供本地静态前端 demo。

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

打开：

- `http://127.0.0.1:8000/`：本地前端 demo
- `http://127.0.0.1:8000/docs`：Swagger API 文档
- `http://127.0.0.1:8000/openapi.json`：OpenAPI JSON

## 核心 API

- `GET /health`
- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`

请求和响应字段见 `docs/API_CONTRACT.md`。

## 本地前端 Demo

静态前端位于：

- `web/index.html`
- `web/styles.css`
- `web/app.js`

demo 支持：

- 创建训练 session；
- 请求下一道训练任务；
- 播放后端返回的 `audio_url`；
- 提交听写答案；
- 刷新训练进度；
- 展示 loading、success、error、empty 状态；
- 展示 API debug 信息。

注意：`GET /api/v1/tasks/next` 会调用在线 `edge-tts` 生成音频。如果当前网络无法访问 `speech.platform.bing.com:443`，该接口可能返回 500。此时前端应保留当前 session，显示清晰的 task/audio 错误和 API debug 信息。这是环境限制，不是 API contract 变更。

## 本地验收命令

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
python -m data_pipeline.run_pipeline --help
```

启动服务后可运行 API smoke：

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_smoke
```

如果在线 TTS 被网络限制阻断，smoke 可能在 `/api/v1/tasks/next` 失败。可以先确认 `/`、`/docs`、`/openapi.json`、`/health` 和 `POST /api/v1/sessions` 正常。

## 离线语料 Pipeline

快速 smoke：

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

只有在小样本 smoke 稳定后，再考虑使用 BERT/LTP/GPT 或更大的数据规模。

## 文档入口

- `docs/DEMO_RUNBOOK.md`：本地演示步骤
- `docs/FRONTEND_INTEGRATION.md`：前端/小程序集成说明
- `docs/API_CONTRACT.md`：API contract
- `docs/DATABASE_SCHEMA.md`：数据库表结构
- `docs/TECHNICAL_OVERVIEW.md`：技术概览

## 不应提交的内容

不要提交：

- `.env`
- API key、token、cookie、云服务器密钥
- 真实用户数据
- `__pycache__/`
- `.pytest_cache/`
- `.venv/`
- `assets/*.wav`
- `assets/*.mp3`
- `data_pipeline/raw_data/` 中的原始语料
- 本地临时日志或测试文件
