# AGENTS.md — SRTP-CAPD 项目 Codex 协作规则

## 0. 项目目标

本仓库目标是完成「面向听觉障碍人群的语音识别康复系统」后端 MVP，供小程序调用。

MVP 后端必须至少支持：

1. 从语料库中抽取训练句子；
2. 为句子生成训练音频；
3. 支持不同难度参数，例如语速、信噪比、语境类型；
4. 接收用户听写/识别结果；
5. 记录用户训练数据、答题历史、难度变化；
6. 导出稳定 API 文档，供小程序前端接入。

## 1. 每个 Codex 进程开始前必须读取

每个 Codex 进程开始执行任务前，必须先读取以下文件：

1. `AGENTS.md`
2. `docs/PROJECT_STATE.md`
3. `docs/STATE_MACHINE.md`
4. `.codex/shared_state.json`
5. 自己对应的 `.codex/tasks/Txx_*.md`

不要只看任务文件。必须结合共享状态文件判断哪些任务已经完成、哪些任务仍然阻塞。

## 2. Codex 进程之间如何“通信”

统一通过 `.codex/shared_state.json` 和 `.codex/logs/` 目录通信。

每个进程开始时：

1. 在 `.codex/shared_state.json` 中把自己的任务状态改为 `in_progress`；
2. 填写 `owner`，例如 `codex-T02-api`；
3. 填写 `started_at`；
4. 不要改动其他任务的状态，除非你明确完成了其依赖项。

每个进程结束时：

1. 将任务状态改为 `done` / `blocked` / `needs_review`；
2. 写入 `completed_at` 或 `blocked_reason`；
3. 更新 `files_changed`；
4. 更新 `tests_run`；
5. 将最终总结写入 `.codex/logs/Txx_result.md`；
6. 若修改了 API，必须同步更新 `docs/API_CONTRACT.md` 或 `docs/openapi-draft.yaml`。

## 3. 禁止事项

- 不要把任何 API Key、token、cookie、数据库密码写进仓库。
- 不要提交 `.env`、`~/.codex/auth.json`、云服务器密钥、真实用户数据。
- 不要直接删除原始语料。
- 不要为了“跑通”而绕过核心逻辑，例如把真实评分函数替换成随机数。
- 不要在没有小样本验证和时间估算前租用 GPU 服务器跑全量任务。
- 不要一次性重构整个项目；每个任务只做自己范围内的最小可验证修改。

## 4. 当前已知高优先级问题

1. 代码格式可能存在缺少换行/不可编译问题，必须先运行 `python -m py_compile` 验证。
2. `llm_augment.py` 中可能存在硬编码 API Key，必须移除并改为环境变量。
3. 数据库目前只覆盖 `sentences`，缺少用户、会话、答题记录、训练进度等表。
4. API 目前只有 `/start`、`/next_task`、`/submit` 的雏形，不足以给小程序长期稳定接入。
5. 音频噪声目前偏“突兀”，应从白噪声升级为可配置噪声 profile，并加入渐入/渐出、归一化和固定随机种子。
6. 离线语料处理未形成可恢复、可分批、可统计的 pipeline。
7. 缺少自动化测试和 API contract 测试。

## 5. 推荐本地命令

Windows PowerShell / Git Bash 均可，但建议优先在项目根目录执行：

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash on Windows
# 或 PowerShell: .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

python -m py_compile data_pipeline/*.py server/*.py
python -m uvicorn server.main:app --reload
```

若已添加 pytest：

```bash
pytest -q
```

## 6. 完成标准

一个任务只有同时满足以下条件才算 `done`：

1. 代码可以编译；
2. 相关测试或 smoke test 已运行；
3. API 或数据结构变化已写入文档；
4. `.codex/shared_state.json` 已更新；
5. `.codex/logs/Txx_result.md` 已写明完成内容、验证命令、剩余风险。

## 7. 面向小程序的 API 约定

后端 API 统一使用 `/api/v1` 前缀。历史接口可以保留，但新接口必须优先走 `/api/v1`。

最低目标接口：

- `GET /health`
- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`
- `GET /openapi.json`

返回 JSON 字段必须稳定，不要随意更名。
