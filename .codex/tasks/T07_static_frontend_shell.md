# T07_static_frontend_shell — 本地前端页面骨架

## 角色

你是前端/后端整合工程师。目标是让访问 `http://127.0.0.1:8000/` 时不再是空页面，而是进入一个本地 demo 前端。

## 开始前必须读取

- `AGENTS.md`
- `docs/PROJECT_STATE.md`
- `docs/STATE_MACHINE.md`
- `.codex/shared_state.json`
- `docs/TECHNICAL_OVERVIEW.md`
- `docs/NEXT_PHASE_PLAN.md`
- `.codex/tasks/T07_static_frontend_shell.md`

## 目标

1. 新增静态前端页面；
2. FastAPI 根路径 `/` 能返回该页面；
3. 页面有基础布局和视觉风格；
4. 页面支持白天/黑夜模式；
5. 不改 `/api/v1` 业务逻辑；
6. 不改数据库 schema；
7. 不做完整 API 流程，那是 T08。

## 建议实现

- 新增 `web/index.html`
- 新增 `web/styles.css`
- 新增 `web/app.js`
- 在 `server/main.py` 中挂载或返回首页；
- 可使用纯 HTML/CSS/JS，不引入前端构建工具；
- 页面应包含：
  - 项目标题；
  - 会话配置区域；
  - 任务/音频区域占位；
  - 答案输入区域占位；
  - 进度区域占位；
  - 主题切换按钮；
  - API 状态提示区域。

## 验收命令

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

还应启动服务后人工确认：

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

打开：

```text
http://127.0.0.1:8000/
```

## 输出

- 更新 `.codex/shared_state.json`
- 写 `.codex/logs/T07_result.md`

## 禁止事项

- 不要新增 `/api/v1` 字段；
- 不要重构 `server/main.py`；
- 不要引入 React/Vue/Vite 等构建系统，除非用户明确要求；
- 不要提交 `.env`、音频产物、`__pycache__`。
