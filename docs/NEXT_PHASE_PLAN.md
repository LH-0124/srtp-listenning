# Next Phase Plan — Frontend Demo And Integration

更新时间：2026-05-09T20:05:19+08:00

## 1. 为什么需要下一阶段

当前仓库已经完成后端 MVP：

- FastAPI `/api/v1` 核心接口已实现；
- SQLite 用户、会话、任务、答案、进度持久化已实现；
- 离线语料 pipeline 已支持小样本、断点、统计；
- 音频噪声 profile、fade、RMS/peak 处理已实现；
- pytest 和 demo runbook 已补齐。

但当前还有两个用户体验层面的缺口：

1. 打开 `http://127.0.0.1:8000/` 是空的或没有合适页面，不适合演示。
2. 虽然后端 API 是正确的，但缺少一个完整的、可视化的前后端跑通实例。使用者不知道如何从创建会话、获取任务、播放音频、提交答案到查看进度。

下一阶段目标是把后端 MVP 变成一个可交互、可演示、可理解的本地完整样例。

## 2. 下一阶段总目标

构建一个轻量但完整的本地前端 demo，并把它和当前 FastAPI 后端接起来。

完成后应支持：

- 访问 `/` 能看到美观的交互页面；
- 页面支持白天/黑夜模式；
- 页面可以创建训练会话；
- 页面可以选择训练模式和噪声 profile；
- 页面可以获取下一题；
- 页面可以播放音频；
- 页面可以输入答案并提交；
- 页面可以看到正确/错误、难度变化和累计进度；
- 页面可以解释当前后端 API 是如何被调用的；
- 文档能说明小程序/前端应如何接入这些 API。

## 3. 推荐任务拆分

### T07_static_frontend_shell

目标：给 FastAPI 增加本地静态前端页面。

范围：

- 新增前端静态资源目录，例如 `web/` 或 `static_app/`；
- 实现 `/` 首页；
- 实现基础 UI 布局；
- 支持白天/黑夜模式；
- 不改 API 业务逻辑；
- 保持现有 `/api/v1` 接口不变。

建议文件：

- `server/main.py`
- `web/index.html`
- `web/styles.css`
- `web/app.js`

### T08_frontend_api_flow_demo

目标：实现完整前后端训练流程。

范围：

- 调用 `POST /api/v1/sessions`；
- 调用 `GET /api/v1/tasks/next`；
- 播放 `audio_url`；
- 调用 `POST /api/v1/answers`；
- 调用 `GET /api/v1/users/{user_id}/progress`；
- 显示当前 session、task、difficulty、progress；
- 对网络/TTS 失败给出清晰 UI 提示。

建议文件：

- `web/app.js`
- `web/index.html`
- `web/styles.css`
- `docs/FRONTEND_INTEGRATION.md`

### T09_frontend_polish_and_accessibility

目标：提升界面可用性和演示质感。

范围：

- 优化页面视觉风格；
- 完善响应式布局；
- 完善白天/黑夜主题；
- 加入 loading、error、empty、success 状态；
- 加入 API 调试信息折叠面板；
- 避免文字重叠；
- 检查桌面和移动宽度下可用性。

建议文件：

- `web/styles.css`
- `web/index.html`
- `web/app.js`

### T10_full_demo_acceptance

目标：做最后一轮完整验收。

范围：

- 跑后端 pytest；
- 跑 API smoke；
- 跑前端手动或自动 smoke；
- 验证 `/`、`/docs`、`/openapi.json`；
- 验证完整交互链路；
- 更新 README、DEMO_RUNBOOK 和最终提交清单。

建议文件：

- `README.md`
- `README-zh.md`
- `docs/DEMO_RUNBOOK.md`
- `.codex/shared_state.json`
- `.codex/logs/T10_result.md`

## 4. 并行建议

不要一开始开太多会话。

推荐顺序：

1. 先让母进程读取本计划并更新 `.codex/shared_state.json`，确认 T07-T10 任务存在。
2. 先执行 T07。
3. T07 完成并提交后，再执行 T08。
4. T08 完成并提交后，再执行 T09。
5. 最后执行 T10。

原因：

- T07/T08/T09 都会改 `web/` 和可能少量改 `server/main.py`；
- 并行很容易产生前端文件冲突；
- 这几个任务顺序执行反而更快、更稳。

如果必须并行：

- T07 只负责页面骨架和静态挂载；
- T08 只负责 JS API 调用；
- T09 只负责 CSS 和 UI 状态；
- 三者必须约定文件边界，否则不要并行。

## 5. 验收标准

下一阶段完成时，至少应满足：

- `python -m compileall -q data_pipeline server tests` 通过；
- `pytest -q` 通过；
- `python -c "import server.main; print('server import ok')"` 通过；
- `python -m uvicorn server.main:app --host 127.0.0.1 --port 8000` 能启动；
- 浏览器访问 `http://127.0.0.1:8000/` 能看到可交互页面；
- 页面能完成创建会话、获取任务、播放音频、提交答案、查看进度；
- 页面有白天/黑夜模式；
- `docs/FRONTEND_INTEGRATION.md` 或等价文档说明前端如何接入 API；
- 不提交 `.env`、`__pycache__`、临时音频和真实用户数据。

## 6. 需要注意的风险

- `/api/v1/tasks/next` 会调用在线 `edge-tts`，网络不可用时页面应显示友好错误；
- 当前评分规则是精确字符串匹配，前端需要清楚展示目标文本或说明这是 MVP 调试模式；
- `target_text` 当前会返回给前端，适合演示，不适合正式训练；
- demo DB 可以提交，但真实用户数据不应进入仓库；
- 前端 demo 不是小程序本体，但它能证明 API 流程如何接入。
