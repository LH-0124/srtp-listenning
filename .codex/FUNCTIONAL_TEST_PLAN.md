# FUNCTIONAL_TEST_PLAN.md — 功能测试计划

## 1. 仓库基础测试

```bash
python -m py_compile data_pipeline/*.py server/*.py
```

通过标准：无 SyntaxError、ImportError。

## 2. 后端启动测试

```bash
python -m uvicorn server.main:app --reload
```

通过标准：

- 服务启动；
- 访问 `http://127.0.0.1:8000/docs` 正常；
- 访问 `http://127.0.0.1:8000/openapi.json` 正常。

## 3. 健康检查

```bash
curl http://127.0.0.1:8000/health
```

期望：

```json
{"status":"ok"}
```

## 4. 会话流程测试

```bash
SESSION_JSON=$(curl -s -X POST http://127.0.0.1:8000/api/v1/sessions   -H "Content-Type: application/json"   -d '{"user_id":"demo_user","training_mode":"LOW","noise_profile":"none"}')

echo "$SESSION_JSON"
```

通过标准：

- 返回 `session_id`；
- 返回 difficulty。

## 5. 获取下一题

```bash
curl "http://127.0.0.1:8000/api/v1/tasks/next?session_id=<SESSION_ID>"
```

通过标准：

- 返回 `task_id`；
- 返回 `audio_url`；
- static URL 能访问音频。

## 6. 提交答案

```bash
curl -X POST http://127.0.0.1:8000/api/v1/answers   -H "Content-Type: application/json"   -d '{"session_id":"<SESSION_ID>","task_id":"<TASK_ID>","user_input":"测试答案"}'
```

通过标准：

- 返回 correct；
- 返回 new_difficulty；
- 数据库写入 answer。

## 7. 查询用户进度

```bash
curl http://127.0.0.1:8000/api/v1/users/demo_user/progress
```

通过标准：

- 返回 total_answers；
- 返回 accuracy；
- 返回 current_difficulty。

## 8. Pipeline 小样本测试

```bash
python -m data_pipeline.run_pipeline --limit 20
```

通过标准：

- 不因单条错误中断；
- 输出统计；
- 数据库有新增或去重后的句子；
- processed_corpus.txt 有内容。

## 9. 音频噪声测试

生成以下 profile：

- none
- white_soft
- cafe
- street

检查：

- 文件存在；
- 音频时长非 0；
- 无明显爆音；
- 噪声不是突然开始或结束。

## 10. API 文档导出

```bash
curl http://127.0.0.1:8000/openapi.json > openapi.json
```

通过标准：

- JSON 有 paths；
- 包含 `/api/v1/sessions`、`/api/v1/tasks/next`、`/api/v1/answers`。
