# T03_data_pipeline — 语料处理 pipeline 工程化

## 角色

你是数据 pipeline 工程师。目标不是追求模型最优，而是让语料处理可运行、可恢复、可估算。

## 依赖

必须先完成 `T01_repo_stabilize`。

## 目标

1. 支持小样本 smoke test；
2. 支持 batch size；
3. 支持断点续跑；
4. 支持处理进度统计；
5. 支持失败样本记录；
6. 给出是否租 GPU 的依据。

## 建议命令设计

为 `run_pipeline.py` 增加参数：

```bash
python -m data_pipeline.run_pipeline   --input data_pipeline/raw_data/corpus.txt   --limit 100   --batch-size 8   --resume   --output processed_corpus.txt
```

## 数据库建议

`sentences` 表建议至少包含：

- `id`
- `text`
- `context_type`
- `score`
- `source`
- `created_at`

新增 `pipeline_runs` 表：

- `id`
- `input_path`
- `limit`
- `processed_count`
- `success_count`
- `failed_count`
- `started_at`
- `completed_at`
- `status`

新增 `pipeline_errors` 表：

- `id`
- `run_id`
- `raw_text`
- `error_message`
- `created_at`

## GPU 决策规则

先跑三组小样本：

```bash
python -m data_pipeline.run_pipeline --limit 20
python -m data_pipeline.run_pipeline --limit 100
python -m data_pipeline.run_pipeline --limit 500
```

记录：

- 总耗时；
- 平均每条耗时；
- BERT 打分耗时；
- GPT 扩写调用次数；
- 失败率；
- CPU 占用；
- 内存占用。

只有当：

1. pipeline 已稳定；
2. 全量预计耗时明显过长；
3. GPU 能明显加速 BERT/LTP 部分；
4. GPT API 调用不是主要瓶颈；

才建议租服务器。

## 输出

- 修改 `data_pipeline/run_pipeline.py` 等文件；
- 生成 `docs/PIPELINE_RUNBOOK.md`；
- 写 `.codex/logs/T03_result.md`；
- 更新 `.codex/shared_state.json`。

## 验收标准

- `--limit 20` 能跑通；
- 失败样本不会中断整个流程；
- 能重复运行且不会重复入库；
- 有耗时统计；
- 有是否租 GPU 的结论模板。
