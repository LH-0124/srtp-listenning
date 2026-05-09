# T08_frontend_api_flow_demo — 前后端完整流程示例

## 角色

你是前端 API 集成工程师。目标是让本地 demo 页面真正调用后端 API，跑通一个完整训练流程。

## 开始前必须读取

- `AGENTS.md`
- `docs/PROJECT_STATE.md`
- `docs/STATE_MACHINE.md`
- `.codex/shared_state.json`
- `docs/API_CONTRACT.md`
- `docs/TECHNICAL_OVERVIEW.md`
- `docs/NEXT_PHASE_PLAN.md`
- `.codex/logs/T07_result.md`
- `.codex/tasks/T08_frontend_api_flow_demo.md`

## 依赖

必须等 `T07_static_frontend_shell` 完成。

## 目标

在已有页面上实现完整 API 流程：

1. 创建训练会话；
2. 获取下一道任务；
3. 播放返回的音频；
4. 输入并提交答案；
5. 显示正确/错误、分数、难度变化；
6. 查询并显示用户进度；
7. 显示 API 调用状态和错误信息；
8. 文档说明前端/小程序如何接入。

## 建议实现

主要修改：

- `web/app.js`
- `web/index.html`
- `web/styles.css`
- `docs/FRONTEND_INTEGRATION.md`

API 调用：

- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`

注意：

- `/api/v1/tasks/next` 可能因在线 TTS 网络失败，前端必须显示友好错误；
- 当前 `target_text` 是 MVP 调试字段，可以用于 demo 自动填入/提示，但文档要说明正式训练不应直接暴露；
- 不要修改后端 API 字段名。

## 验收命令

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

人工验收：

1. 启动后端；
2. 打开 `http://127.0.0.1:8000/`；
3. 创建 session；
4. 获取任务；
5. 播放音频；
6. 提交答案；
7. 查看进度变化。

## 输出

- 更新 `.codex/shared_state.json`
- 写 `.codex/logs/T08_result.md`

## 禁止事项

- 不要改数据库 schema；
- 不要改 pipeline；
- 不要改 API contract 字段；
- 不要提交 `.env`、音频产物、`__pycache__`。
