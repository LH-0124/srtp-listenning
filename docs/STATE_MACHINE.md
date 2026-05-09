# STATE_MACHINE.md — 项目状态流转文件

本文定义整个项目从当前半成品状态推进到可演示后端 MVP 的状态机。

## 1. 状态枚举

```text
S0_DISCOVERED
  ↓
S1_REPO_STABILIZED
  ↓
S2_API_CONTRACT_READY
  ↓
S3_USER_DATA_READY
  ↓
S4_PIPELINE_SMOKE_READY
  ↓
S5_AUDIO_NOISE_READY
  ↓
S6_TESTS_READY
  ↓
S7_MINIPROGRAM_BACKEND_READY
  ↓
S8_DEMO_READY
```

## 2. 状态定义

### S0_DISCOVERED

当前状态。仓库已有初步代码，但不保证可运行、可测试、可对接。

进入条件：

- 已读取仓库；
- 已确认目录结构；
- 已记录已知风险。

退出条件：

- `T00_repo_audit` 完成；
- 生成 `docs/AUDIT_REPORT.md`。

### S1_REPO_STABILIZED

仓库能被正常安装、编译、启动。

进入条件：

- `python -m py_compile data_pipeline/*.py server/*.py` 通过；
- API Key 已移出代码；
- `.env.example` 已存在；
- assets 目录自动创建。

退出条件：

- `T01_repo_stabilize` 完成；
- smoke start 命令能执行。

### S2_API_CONTRACT_READY

面向小程序的 API 契约稳定。

进入条件：

- `/health` 可访问；
- `/api/v1/sessions` 可创建会话；
- `/api/v1/tasks/next` 可拿题；
- `/api/v1/answers` 可提交答案；
- `/openapi.json` 可导出；
- `docs/API_CONTRACT.md` 已更新。

退出条件：

- `T02_api_contract` 完成。

### S3_USER_DATA_READY

用户、会话、答题、进度可持久化。

进入条件：

- 数据库包含 users、sessions、answers、progress 或等价结构；
- 每次提交答案后能记录；
- 能查询用户训练进度。

退出条件：

- `T05_user_data` 完成。

### S4_PIPELINE_SMOKE_READY

语料 pipeline 能小样本跑通并可估算全量成本。

进入条件：

- 可处理 20 / 100 / 500 条样本；
- 有进度日志；
- 有失败记录；
- 支持断点续跑；
- 能估算全量时间。

退出条件：

- `T03_data_pipeline` 完成。

### S5_AUDIO_NOISE_READY

音频生成与噪声处理可用于演示。

进入条件：

- TTS 能生成音频；
- 支持至少 3 种噪声 profile；
- 噪声有 fade in/out，不突兀；
- 输出音频 RMS 合理，无明显爆音。

退出条件：

- `T04_audio_noise` 完成。

### S6_TESTS_READY

核心功能有自动化测试和 smoke test。

进入条件：

- pytest 通过；
- API smoke test 通过；
- pipeline smoke test 通过；
- 测试说明已写入 `.codex/FUNCTIONAL_TEST_PLAN.md`。

退出条件：

- `T06_tests_docs_release` 完成。

### S7_MINIPROGRAM_BACKEND_READY

后端可以给小程序接入。

进入条件：

- API 文档稳定；
- CORS 配置明确；
- 音频 URL 返回完整或可配置 base URL；
- 用户数据可查询；
- 演示数据库可用。

退出条件：

- 小程序端可按文档调用，或 curl 全流程通过。

### S8_DEMO_READY

最终可答辩/演示状态。

进入条件：

- 一条命令启动；
- 一套 demo 用户数据；
- 一套 demo 语料；
- 一套 demo 音频；
- PPT 或说明文档可展示流程。

## 3. 任务与状态映射

| 任务 | 完成后推进到 |
|---|---|
| T00_repo_audit | S0_DISCOVERED 已确认 |
| T01_repo_stabilize | S1_REPO_STABILIZED |
| T02_api_contract | S2_API_CONTRACT_READY |
| T05_user_data | S3_USER_DATA_READY |
| T03_data_pipeline | S4_PIPELINE_SMOKE_READY |
| T04_audio_noise | S5_AUDIO_NOISE_READY |
| T06_tests_docs_release | S6/S7/S8 |

## 4. 状态更新规则

所有 Codex 进程结束时都要更新 `.codex/shared_state.json`：

```json
{
  "current_state": "S1_REPO_STABILIZED",
  "last_updated_by": "codex-T01-repo",
  "last_updated_at": "2026-05-05T21:30:00+08:00",
  "state_notes": "py_compile passed; secrets moved to .env.example"
}
```

禁止只改代码不更新状态。
