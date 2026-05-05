# T00_repo_audit result

完成时间：2026-05-05T21:28:47+08:00

## 完成内容

- 已读取 `AGENTS.md`、`docs/PROJECT_STATE.md`、`docs/STATE_MACHINE.md`、`.codex/shared_state.json`、`.codex/tasks/T00_repo_audit.md`。
- 已审查目录结构、关键 Python 文件、API 草案、数据库结构、依赖安装情况和安全风险。
- 已生成 `docs/AUDIT_REPORT.md`。
- 未修改业务代码。

## 验证命令

- `Get-ChildItem -Recurse -File | Select-Object -ExpandProperty FullName`
- `python -m py_compile data_pipeline/*.py server/*.py`
  - PowerShell 下失败，原因是通配符未展开。
- `Get-ChildItem -Path data_pipeline,server -Filter *.py | ForEach-Object { python -m py_compile $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }`
  - 通过。
- `pip install -r requirements.txt`
  - 默认沙箱下失败，`edge-tts` 因网络/沙箱访问 PyPI 失败未安装；提权重试后成功安装缺失依赖。
- `python -c "import server.main; print('server.main import ok')"`
  - 初次失败，`ModuleNotFoundError: No module named 'edge_tts'`；安装依赖后通过。
- 使用 Python `sqlite3` 检查 `capd_database.db`
  - 仅发现 `sentences` 和 `sqlite_sequence`。

## 主要发现

- `data_pipeline/llm_augment.py` 存在硬编码 OpenAI API Key，必须立即移除并吊销旧 Key。
- 当前 Python 文件语法编译通过；安装依赖后服务导入 smoke test 通过。
- API 实现仍是 `/start`、`/next_task`、`/submit`，未实现 `/api/v1` contract。
- 数据库仅有 `sentences` 表，缺少用户、会话、答案和进度表。
- pipeline 缺少小样本、断点续跑、失败记录和统计。
- 音频噪声只有白噪声，缺少 profile、fade、归一化和固定随机种子。

## 剩余风险

- 本次没有修改业务代码，因此所有发现的问题仍待 T01 及后续任务处理。
- `py_compile` 会刷新 `__pycache__` 产物，未作为业务代码变更处理。
