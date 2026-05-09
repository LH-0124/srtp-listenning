
# SRTP-CAPD 后端 MVP

CAPD（中枢听觉处理障碍）听力康复小程序的后端 MVP（最小可行性产品）。该服务提供稳定的 `/api/v1` API，将用户训练历史记录存储在 SQLite 中，生成任务音频，并包含一个离线语料处理流水线。

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

OpenAPI 文档访问地址：

* `http://127.0.0.1:8000/openapi.json`
* `http://127.0.0.1:8000/docs`

## 核心 API

* `GET /health`
* `POST /api/v1/sessions`
* `GET /api/v1/tasks/next?session_id=...`
* `POST /api/v1/answers`
* `GET /api/v1/users/{user_id}/progress`

有关请求和响应字段的详细信息，请参阅 `docs/API_CONTRACT.md`。

## 本地冒烟测试

运行测试：

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"

```

启动 uvicorn 后运行 API 冒烟测试：

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl [http://127.0.0.1:8000](http://127.0.0.1:8000) -UserId demo_smoke

```

运行快速离线流水线冒烟测试：

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt

```

## 演示指南

请参阅 `docs/DEMO_RUNBOOK.md` 获取分步的本地演示指南，其中包括如何检查 API 响应、数据库持久化、流水线输出以及生成的音频质量。

