# SRTP-CAPD 后端 MVP 技术说明

本文面向项目接手者和答辩/演示准备者，说明当前仓库已经实现了什么、代码如何组织、数据如何流动，以及应该如何运行和验证。

## 1. 项目目标

本项目是「面向听觉障碍人群的语音识别康复系统」后端 MVP，目标是给小程序提供一套可演示、可测试、可继续扩展的训练后端。

当前 MVP 支持：

- 从 SQLite 语料库中抽取训练句子；
- 为训练句子生成 TTS 音频；
- 按语速、信噪比、噪声 profile 控制训练难度；
- 创建用户训练会话；
- 获取下一道训练任务；
- 提交听写答案；
- 持久化用户、会话、任务、答案和进度；
- 提供 `/openapi.json` 和文档化 API contract；
- 提供离线语料处理 pipeline；
- 提供 pytest 自动化测试和 demo runbook。

当前项目状态约为后端 MVP 的测试就绪阶段：核心链路已经跑通，但仍需要人工听感检查、真实小程序联调和更完整的部署说明。

## 2. 目录结构

```text
CAPD_Server_Backend/
├── server/                    # FastAPI 在线服务
│   ├── main.py                # API 路由、会话流程、任务/答案处理
│   ├── models.py              # Pydantic 请求/响应模型
│   ├── adaptive_logic.py      # 简单阶梯式难度调整
│   ├── audio_service.py       # TTS、变速、噪声混合、音频保存
│   ├── noise_profiles.py      # 噪声 profile、SNR 混合、fade、归一化
│   └── user_data_store.py     # 用户/会话/任务/答案/进度 SQLite 持久化
├── data_pipeline/             # 离线语料处理
│   ├── run_pipeline.py        # CLI 入口
│   ├── preprocess.py          # 文本清洗
│   ├── context_scoring.py     # BERT/LTP 语境评分
│   ├── llm_augment.py         # GPT 句子扩写
│   └── database_manager.py    # corpus/pipeline 表管理
├── tests/                     # pytest 自动化测试
├── docs/                      # API、数据库、pipeline、demo 和项目状态文档
├── scripts/                   # API smoke test 脚本
├── assets/                    # 生成音频目录，运行时自动创建
├── capd_database.db           # demo SQLite 数据库
├── processed_corpus.txt       # demo pipeline 输出
├── README.md                  # 快速开始
├── README-zh.md               # 中文快速开始
└── requirements.txt           # Python 依赖
```

## 3. 在线 API 服务

服务入口是 `server/main.py`，FastAPI 应用对象为 `app`。

启动命令：

```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

启动后可访问：

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

核心接口：

- `GET /health`
- `POST /api/v1/sessions`
- `GET /api/v1/tasks/next?session_id=...`
- `POST /api/v1/answers`
- `GET /api/v1/users/{user_id}/progress`

旧接口仍保留：

- `POST /start`
- `GET /next_task`
- `POST /submit`

旧接口用于兼容早期调用方式，新接入应优先使用 `/api/v1`。

## 4. 训练主流程

典型训练流程如下：

1. 小程序调用 `POST /api/v1/sessions` 创建训练会话。
2. 后端写入 `users`、`training_sessions`、`user_progress`。
3. 小程序调用 `GET /api/v1/tasks/next?session_id=...` 获取任务。
4. 后端从 `sentences` 表按 `training_mode` 抽取句子。
5. 后端调用 `AudioService.generate_task_audio(...)` 生成音频。
6. 后端写入 `training_tasks`。
7. 小程序播放返回的 `audio_url`。
8. 小程序调用 `POST /api/v1/answers` 提交听写结果。
9. 后端按当前 MVP 的精确字符串匹配规则判分。
10. `PatientState.adjust(...)` 调整语速和 SNR。
11. 后端写入 `answers`，更新 `training_sessions` 和 `user_progress`。
12. 小程序调用 `GET /api/v1/users/{user_id}/progress` 查询累计进度。

## 5. 数据库设计

默认数据库是项目根目录下的 `capd_database.db`。

语料和 pipeline 表：

- `sentences`：训练句子、语境类型、分数、来源、创建时间；
- `pipeline_runs`：pipeline 每次运行的配置、统计、状态；
- `pipeline_errors`：pipeline 逐条失败记录。

用户训练表：

- `users`：用户基础记录；
- `training_sessions`：训练会话、训练模式、噪声 profile、当前速度/SNR；
- `training_tasks`：发给用户的每道题；
- `answers`：用户提交的每次答案；
- `user_progress`：累计答题数、正确数、准确率、当前难度。

表结构初始化采用 `CREATE TABLE IF NOT EXISTS`，目标是可重复执行，不破坏已有 demo 数据。

更详细字段说明见：

```text
docs/DATABASE_SCHEMA.md
```

## 6. 音频生成与噪声处理

音频入口是：

```text
server/audio_service.py
```

噪声与归一化逻辑在：

```text
server/noise_profiles.py
```

当前支持的 `noise_profile`：

- `none`
- `white`
- `cafe`
- `street`
- `speech_babble`

处理流程：

1. 使用 `edge-tts` 生成临时 MP3；
2. 使用 `librosa` 读取音频；
3. 按 `speed` 做 time stretch；
4. 按 `noise_profile` 生成确定性合成噪声；
5. 按 `snr` 混合语音和噪声；
6. 加 fade in/out；
7. 做 RMS normalization；
8. 做 peak limiting，避免 clipping；
9. 写入 `assets/task_*.wav`；
10. 删除临时 MP3。

注意：真实 TTS 依赖网络访问 Microsoft Edge TTS 服务。pytest 中通过 monkeypatch 避免网络依赖。

## 7. 离线语料 Pipeline

pipeline 入口：

```powershell
python -m data_pipeline.run_pipeline --help
```

快速 smoke：

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer heuristic --no-augment --output processed_corpus.txt
```

重要参数：

- `--input`：输入语料路径；
- `--output`：输出 TSV 路径；
- `--db-path`：SQLite 数据库路径；
- `--limit`：最多处理多少条清洗后的句子；
- `--batch-size`：批量 checkpoint 大小；
- `--resume`：跳过数据库中已存在句子；
- `--scorer heuristic`：快速本地烟测评分；
- `--scorer bert`：真实 BERT/LTP 评分；
- `--no-augment`：关闭 GPT 扩写；
- `--augment-count`：低语境句扩写数量。

真实全量处理前建议先跑：

```powershell
python -m data_pipeline.run_pipeline --limit 20 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 100 --batch-size 8 --resume --scorer bert --no-augment
python -m data_pipeline.run_pipeline --limit 500 --batch-size 8 --resume --scorer bert --no-augment
```

根据耗时再决定是否需要 GPU。GPT 扩写是网络/API 受限任务，GPU 不会明显帮助。

## 8. 环境变量与安全

`.env` 是本地私密配置，不应提交。

`.env.example` 给出占位配置：

```env
OPENAI_API_KEY=replace_me
GPT_API_URL=https://api.openai.com/v1/chat/completions
GPT_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./capd_database.db
ASSETS_BASE_URL=http://localhost:8000/static
```

当前代码不应再包含硬编码 API Key。提交前应确认：

```powershell
git status --short
```

不要提交：

- `.env`
- `__pycache__/`
- `*.pyc`
- `.venv/`
- 临时音频 `assets/*.wav`、`assets/*.mp3`
- 真实用户数据或真实密钥。

## 9. 自动化测试

测试目录：

```text
tests/
```

当前测试覆盖：

- API contract；
- OpenAPI 核心路径；
- session/task/answer/progress 流程；
- 用户数据持久化；
- pipeline heuristic smoke；
- SQLite schema；
- noise profile、固定 seed、非静音、peak limiting、非法 profile。

运行：

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

当前验收结果：

```text
13 passed
```

## 10. Demo 运行方式

完整 demo 步骤见：

```text
docs/DEMO_RUNBOOK.md
```

最短路径：

```powershell
pip install -r requirements.txt
python -m compileall -q data_pipeline server tests
pytest -q
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```

另开一个 PowerShell：

```powershell
.\scripts\api_smoke_test.ps1 -BaseUrl http://127.0.0.1:8000 -UserId demo_user
```

如果要手工调用 API，可在浏览器打开：

```text
http://127.0.0.1:8000/docs
```

## 11. 当前剩余风险

当前仓库已经达到后端 MVP 测试就绪状态，但仍有几项需要人工或后续工程处理：

- 真实在线 `edge-tts` 需要网络环境，离线或受限网络会影响 `/api/v1/tasks/next`；
- 噪声 profile 已有数值测试，但自然度仍需人工听感检查；
- BERT/LTP/GPT 全量 pipeline 尚未跑完，需要先做 20/100/500 条耗时评估；
- 当前判分是精确字符串匹配，后续可升级为编辑距离、拼音相似度或语音识别置信度；
- 当前部署说明仍偏本地开发，生产部署需要补充服务进程、反向代理、静态资源、CORS、安全配置等。

## 12. 推荐阅读顺序

如果你想快速理解项目，建议按这个顺序读：

1. `README-zh.md`
2. `docs/DEMO_RUNBOOK.md`
3. `docs/API_CONTRACT.md`
4. `docs/DATABASE_SCHEMA.md`
5. `docs/PIPELINE_RUNBOOK.md`
6. `server/main.py`
7. `server/user_data_store.py`
8. `server/audio_service.py`
9. `server/noise_profiles.py`
10. `data_pipeline/run_pipeline.py`
