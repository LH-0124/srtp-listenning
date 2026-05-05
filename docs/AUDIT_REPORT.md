# AUDIT_REPORT.md — T00 仓库审查报告

审查时间：2026-05-05T21:25:56+08:00  
审查范围：只做仓库审查，未修改业务代码。

## 1. 当前完成度估计

当前后端约完成 40%—45%。仓库已经具备离线语料处理、SQLite 句子表、FastAPI 雏形、TTS/加噪音频生成和简单自适应逻辑，但仍未达到可稳定接入小程序的 MVP 状态。

已具备：

- `data_pipeline/`：清洗、BERT/LTP 语境评分、LLM 扩写、SQLite 入库入口。
- `server/`：FastAPI 应用、旧版训练接口、音频生成、自适应参数调整。
- `docs/API_CONTRACT.md` 和 `docs/openapi-draft.yaml`：已有 `/api/v1` 目标接口草案。
- `capd_database.db`：已有 `sentences` 表及基础字段。

主要缺口：

- 初次服务运行导入失败，原因是当前环境缺少 `edge_tts`；提权安装依赖后，`server.main` 导入 smoke test 已通过。
- 已实现 API 与文档约定不一致：代码仍是 `/start`、`/next_task`、`/submit`。
- 数据库缺少用户、会话、答题记录、训练进度等表。
- 仍存在硬编码 API Key，必须优先处理。
- pipeline 不支持分批、断点续跑、失败记录、统计与成本估算。
- 音频噪声为单一白噪声，缺少 profile、fade、归一化和固定随机种子。

## 2. 可编译性与运行性

执行结果：

- `python -m py_compile data_pipeline/*.py server/*.py`：在 PowerShell 下失败，原因是通配符未被展开，Python 收到字面量 `data_pipeline/*.py`。
- `Get-ChildItem -Path data_pipeline,server -Filter *.py | ForEach-Object { python -m py_compile $_.FullName ... }`：通过。
- `python -c "import server.main; print('server.main import ok')"`：初次失败；安装缺失依赖后通过。

初次运行导入失败原因：

- `server/audio_service.py` 第 1 行直接 `import edge_tts`。
- 当前环境初次 `pip install -r requirements.txt` 未能安装/确认 `edge-tts`，网络访问被沙箱拦截；提权重试后成功安装 `edge-tts`、`ltp`、`ltp-core`、`ltp-extension`、`tabulate`。

结论：

- Python 源码语法层面可编译。
- 当前环境已能导入 FastAPI 应用；仍建议 T01 保留依赖缺失时的清晰错误或降级策略，避免单个 TTS 依赖阻断服务启动。

## 3. 安全问题

高危问题：

- `data_pipeline/llm_augment.py:12` 包含硬编码 OpenAI API Key 默认值，格式为 `sk-...`。该 Key 应视为已泄露，必须从代码中删除，并在供应商后台吊销。
- `data_pipeline/llm_augment.py:54` 使用该 Key 组装 `Authorization: Bearer ...` 请求头。
- `GPT_API_URL` 指向第三方兼容接口 `https://api.chatanywhere.tech/v1/chat/completions`，需要明确是否为预期供应商，并在文档中说明配置来源。

建议：

- T01 中立即改为仅从环境变量读取 Key；缺失时返回清晰错误，不允许默认真实 Key。
- 添加 `.env.example`，只写变量名，不写真实值。
- 后续运行 secret scan，至少覆盖 `sk-`、`Bearer`、`api_key`、`token`。

## 4. API 问题

现状：

- `server/main.py` 只实现了：
  - `POST /start`
  - `GET /next_task`
  - `POST /submit`
- `docs/API_CONTRACT.md` 和 `docs/openapi-draft.yaml` 约定的是：
  - `GET /health`
  - `POST /api/v1/sessions`
  - `GET /api/v1/tasks/next`
  - `POST /api/v1/answers`
  - `GET /api/v1/users/{user_id}/progress`

问题：

- 实现与 API contract 不一致，小程序无法按文档接入。
- 当前 `/next_task` 返回 `target_text` 明文，仅适合演示，不适合正式训练评分。
- 会话存在进程内 `sessions = {}`，服务重启即丢失。
- `/submit` 依赖客户端回传 `target_text` 判分，存在篡改风险。
- `audio_url` 返回相对路径 `/static/...`，缺少可配置 base URL。
- 缺少 CORS 配置、健康检查、版本信息、稳定错误响应结构。

## 5. 数据库问题

数据库检查结果：

```text
tables: sentences, sqlite_sequence

sentences:
  id INTEGER PRIMARY KEY
  text TEXT
  context_type TEXT
  score REAL
```

问题：

- 仅覆盖语料句子，缺少 `users`、`sessions`、`tasks`、`answers`、`progress` 或等价结构。
- `sentences.text` 在代码中声明 `UNIQUE`，但当前数据库 `PRAGMA table_info` 只能看到字段，仍需进一步确认索引实际存在。
- 缺少迁移机制，后续直接改 `CREATE TABLE IF NOT EXISTS` 不足以升级已有数据库。
- 答题历史、自适应难度变化没有持久化，无法做康复进度分析。

## 6. 语料 Pipeline 问题

现状：

- `preprocess.py` 做基础正则清洗。
- `context_scoring.py` 每句加载后使用 BERT + LTP 评分。
- `run_pipeline.py` 逐行处理 `data_pipeline/raw_data/corpus.txt`，低语境句调用 LLM 扩写。
- 输出写入 `capd_database.db` 和 `processed_corpus.txt`。

问题：

- 没有 CLI 参数，不能指定样本数量、输入路径、输出路径、批次大小。
- 没有断点续跑、进度表、失败原因记录。
- BERT/LTP 模型默认下载，离线或网络受限时不可复现。
- LLM 扩写网络调用在主循环内同步执行，失败率、耗时和成本不可控。
- 没有 20/100/500 条小样本 smoke test 结果，不能判断是否需要 GPU 或云资源。
- `llm_augment.py` 的 `response_format={"type":"json_object"}` 与 prompt 要求“JSON 数组”不完全一致，解析依赖兼容逻辑。

## 7. 音频噪声问题

现状：

- `server/audio_service.py` 使用 `edge_tts` 生成中文语音。
- 使用 `librosa.effects.time_stretch` 调整语速。
- 使用 `np.random.randn` 生成白噪声，并按 SNR 混合。

问题：

- 只有白噪声，无 `none`、`cafe`、`street`、`speech_babble` 等 profile。
- 没有 fade in/out，噪声起止可能突兀。
- 没有输出 RMS/峰值归一化，存在爆音或音量不稳定风险。
- 没有固定随机种子，测试结果不可复现。
- 临时文件清理没有放在 `finally`，中途异常可能遗留临时 mp3。
- TTS 依赖缺失时直接导致整个 `server.main` 无法导入。

## 8. 依赖与环境问题

`requirements.txt` 包含：

- FastAPI/uvicorn/pydantic
- torch/transformers/ltp
- librosa/soundfile/numpy/scipy
- edge-tts/python-multipart

检查结果：

- 多数依赖已存在于本机 Python 3.12 环境。
- `edge-tts` 初次因网络/沙箱访问 PyPI 失败；提权安装后已安装成功。
- 依赖未锁版本，后续环境可复现性较弱。

建议：

- T01 先提供 `.env.example` 和明确的 Python 版本说明。
- 短期可保持 `requirements.txt`，但至少补充安装失败时的排查说明。
- 进入演示阶段前考虑生成锁定版本文件。

## 9. 下一步任务排序

建议按以下顺序推进：

1. `T01_repo_stabilize`
   - 删除硬编码 Key。
   - 增加 `.env.example`。
   - 确保 `server.main` 可导入，`uvicorn server.main:app` 能启动。
   - 保持 `py_compile` 通过。

2. `T02_api_contract`
   - 实现 `/health` 和 `/api/v1` 核心接口。
   - 让实现与 `docs/API_CONTRACT.md` 对齐。
   - 明确稳定响应字段和错误结构。

3. `T05_user_data`
   - 增加用户、会话、答案、进度数据结构。
   - 提交答案后持久化记录和难度变化。

4. `T03_data_pipeline`
   - 加入小样本模式、断点续跑、失败记录、统计输出。
   - 先跑 20/100/500 条估算耗时，再决定是否租 GPU。

5. `T04_audio_noise`
   - 加 noise profile、fade、RMS 归一化、固定随机种子。
   - 增加音频 smoke test。

6. `T06_tests_docs_release`
   - 补 pytest、API smoke test、pipeline smoke test。
   - 更新 README、DEMO_RUNBOOK 和最终小程序接入说明。

## 10. 本次审查命令

已运行：

```powershell
Get-ChildItem -Recurse -File | Select-Object -ExpandProperty FullName
python -m py_compile data_pipeline/*.py server/*.py
Get-ChildItem -Path data_pipeline,server -Filter *.py | ForEach-Object { python -m py_compile $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }
pip install -r requirements.txt
python -c "import server.main; print('server.main import ok')"
rg -n "sk-|api[_-]?key|token|Authorization|OPENAI|DASHSCOPE|DeepSeek|base_url|password|secret|Bearer" data_pipeline server docs requirements.txt README.txt Log.md
```

数据库检查使用 Python `sqlite3` 完成。`pip install -r requirements.txt` 曾在默认沙箱下失败，按权限规则提权重试后成功。

## 11. 结论

T00 审查已完成。仓库处于 `S0_DISCOVERED` 已确认状态，下一步应进入 `T01_repo_stabilize`，优先处理硬编码 Key、启动稳定性和工程化运行说明。
