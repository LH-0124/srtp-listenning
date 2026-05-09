# T06_tests_docs_release — 测试、文档与演示交付

## 角色

你是 QA + Release 工程师。目标是让项目可演示、可交接、可给小程序接入。

## 依赖

必须完成：

- T02_api_contract
- T03_data_pipeline
- T04_audio_noise
- T05_user_data

## 目标

1. 补齐 pytest；
2. 补齐 API smoke test；
3. 补齐 README；
4. 补齐小程序接入说明；
5. 生成演示运行手册。

## 建议新增测试

- `tests/test_health.py`
- `tests/test_api_session_flow.py`
- `tests/test_database_schema.py`
- `tests/test_audio_service.py`
- `tests/test_pipeline_smoke.py`

## 最小测试命令

```bash
python -m py_compile data_pipeline/*.py server/*.py
pytest -q
```

## API smoke test

写入 `scripts/api_smoke_test.sh`：

1. 启动服务；
2. 调用 `/health`；
3. 创建 session；
4. 获取下一题；
5. 提交答案；
6. 查询用户进度。

## 文档

至少更新：

- `README.md`
- `docs/API_CONTRACT.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/DEMO_RUNBOOK.md`
- `.codex/FUNCTIONAL_TEST_PLAN.md`

## 输出

- 测试文件；
- smoke 脚本；
- 交付文档；
- `.codex/logs/T06_result.md`；
- 更新 `.codex/shared_state.json`。

## 验收标准

- `pytest -q` 通过；
- smoke test 通过；
- `GET /openapi.json` 可访问；
- 文档能指导小程序同学接入。
