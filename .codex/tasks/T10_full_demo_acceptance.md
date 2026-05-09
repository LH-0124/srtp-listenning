# T10_full_demo_acceptance — 完整演示验收

## 角色

你是 QA/Release 工程师。目标是对后端 + 本地前端 demo 做最终验收，并更新运行文档。

## 开始前必须读取

- `AGENTS.md`
- `.codex/shared_state.json`
- `docs/API_CONTRACT.md`
- `docs/TECHNICAL_OVERVIEW.md`
- `docs/NEXT_PHASE_PLAN.md`
- `.codex/logs/T07_result.md`
- `.codex/logs/T08_result.md`
- `.codex/logs/T09_result.md`
- `.codex/tasks/T10_full_demo_acceptance.md`

## 依赖

必须等 T07、T08、T09 完成。

## 目标

1. 完整验收后端和本地前端 demo；
2. 跑自动化测试；
3. 跑 API smoke；
4. 人工验证 `/` 前端流程；
5. 更新 README / DEMO_RUNBOOK / FRONTEND_INTEGRATION；
6. 明确剩余风险和提交清单。

## 验收命令

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
python -m data_pipeline.run_pipeline --help
```

启动服务：

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

检查：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

API smoke：

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_user
```

## 输出

- 更新 `.codex/shared_state.json`
- 写 `.codex/logs/T10_result.md`
- 必要时更新：
  - `README.md`
  - `README-zh.md`
  - `docs/DEMO_RUNBOOK.md`
  - `docs/FRONTEND_INTEGRATION.md`

## 完成标准

- 自动化测试通过；
- 本地前端能打开；
- 前端完整流程可跑；
- 文档能指导用户启动和演示；
- 不提交 `.env`、临时音频、`__pycache__`、真实用户数据。
