# 数据流水线 (Data Pipeline) 自述文件

本目录包含离线语料库流水线，用于在 FastAPI 后端提供服务前准备训练句子。

## 1. 流水线功能

该流水线读取原始文本语料库，清洗每一行，对句子的上下文进行评分，（可选）使用 GPT 扩展低上下文句子，并将结果写入 SQLite 数据库。

**主要流程：**

1. `run_pipeline.py`：解析命令行参数并协调运行。
2. `preprocess.py`：清洗原始文本行并过滤不可用的短行。
3. `context_scoring.py`：当使用 `--scorer bert` 时，使用 BERT 结合 LTP 分词对清洗后的句子进行评分。
4. `run_pipeline.py`：根据 `--high-threshold`（高阈值）将每个句子分类为 `HIGH`（高上下文）或 `LOW`（低上下文）。
5. `llm_augment.py`：（可选）调用兼容 GPT 的 API 为 `LOW` 句子生成变体。
6. `database_manager.py`：创建/恢复 SQLite 表并插入接收的句子。
7. 同时生成一个 TSV 输出文件用于人工检查。

默认的流水线数据库现在为：

```text
new_capd_datebase.db
```

这旨在避免覆盖现有的本地演示数据库 `capd_database.db`。

## 2. 重要文件

* `run_pipeline.py`：命令行入口点。
* `preprocess.py`：文本清洗。
* `context_scoring.py`：BERT/LTP 评分器和异常检测。
* `llm_augment.py`：基于 GPT 的句子扩展。
* `database_manager.py`：SQLite 表、运行记录、错误日志和句子插入管理。
* `raw_data/`：本地原始语料文件。
* `source_backups/`：GPU/500MiB 相关更改前的源码备份。

## 3. 数据库表

流水线在选定的 SQLite 数据库中创建以下表：

* `sentences`：清洗后的句子文本、上下文类型、评分、来源和创建时间。
* `pipeline_runs`：每次流水线运行的一行记录，包含参数、计数器、状态和时间。
* `pipeline_errors`：逐行失败记录，包含原始文本和错误消息。

使用 `--resume` 参数可跳过 `sentences` 表中已存在的清洗后的句子。

## 4. 参数说明

**常用参数：**

* `--input PATH`：原始语料输入文件路径。
* `--output PATH`：TSV 输出路径。
* `--db-path PATH`：SQLite 输出数据库路径。默认值：`new_capd_datebase.db`。
* `--limit N`：最多处理 N 条清洗后的句子。
* `--max-input-mb MB`：读取原始输入文件约 MB MiB 后停止。
* `--batch-size N`：每处理 N 条源句子更新一次运行计数器。
* `--resume`：跳过数据库中已有的句子。
* `--scorer heuristic|bert`：快速启发式评分器或生产级 BERT/LTP 评分器。
* `--device auto|cpu|cuda`：BERT 设备。`auto` 会在可用时使用 CUDA。
* `--high-threshold FLOAT`：判定为 `HIGH` 上下文的分数阈值。
* `--no-augment`：禁用 GPT 扩展。
* `--augment-count N`：每个 `LOW` 句子生成的 GPT 变体数量。
* `--anomaly-threshold FLOAT`：用于过滤 GPT 变体的伪 PPL (pseudo-PPL) 阈值。

**首次服务器运行的推荐默认值：**

```bash
--scorer bert --device cuda --no-augment --resume --batch-size 32

```

建议在 BERT/LTP 路径稳定后再添加 GPT，因为 GPT 调用受网络/API 限制，速度较慢且可能产生费用。

## 5. 本地冒烟测试

在租赁或使用 GPU 服务器前，请先运行此测试：

```bash
python -m data_pipeline.run_pipeline \
  --input data_pipeline/raw_data/corpus.txt \
  --db-path new_capd_datebase.db \
  --output processed_corpus.tsv \
  --limit 20 \
  --batch-size 8 \
  --scorer heuristic \
  --no-augment \
  --resume
```

然后确认：

```bash
python -m data_pipeline.run_pipeline --help
python -m compileall -q data_pipeline
```

## 6. GPU 服务器设置

在 Linux GPU 服务器上：

```bash
git clone <你的仓库地址>
cd CAPD_Server_Backend

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

```

如果默认的 `pip install -r requirements.txt` 安装的是 CPU 版 PyTorch，请安装支持 CUDA 的版本。检查 PyTorch 官网安装命令以匹配你的 CUDA 版本，然后验证：

```bash
python - <<'PY'
import torch
print("cuda_available:", torch.cuda.is_available())
print("device_count:", torch.cuda.device_count())
print("device_name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
PY

```

如果显示 `cuda_available: False`，则 `--device cuda` 将失效，`--device auto` 将回退到 CPU。

## 7. 运行前 500 MiB 的 Baike Triples 数据

大型源文件路径：

```text
data_pipeline/raw_data/baike_triple/baike_triples.txt
```

使用 GPU 上的 BERT/LTP 处理前 500 MiB 数据（不使用 GPT）：

```bash
python -m data_pipeline.run_pipeline \
  --input data_pipeline/raw_data/baike_triple/baike_triples.txt \
  --db-path new_capd_datebase.db \
  --output processed_baike_500m.tsv \
  --max-input-mb 500 \
  --batch-size 32 \
  --resume \
  --scorer bert \
  --device cuda \
  --no-augment
```

若希望脚本自动检测 GPU，请使用 `--device auto`。

## 8. 使用 GPT 增强运行

GPT 增强需要设置环境变量：

```bash
export OPENAI_API_KEY="..."
export GPT_API_URL="https://api.openai.com/v1/chat/completions"
export GPT_MODEL="gpt-3.5-turbo"

```

然后运行：

```bash
python -m data_pipeline.run_pipeline \
  --input data_pipeline/raw_data/baike_triple/baike_triples.txt \
  --db-path new_capd_datebase.db \
  --output processed_baike_500m_gpt.tsv \
  --max-input-mb 500 \
  --batch-size 32 \
  --resume \
  --scorer bert \
  --device cuda \
  --augment-count 3

```

**注意：**

* GPT 的速度取决于远程 API，而非本地 GPU。
* GPT 成本随 `LOW` 句子数量和 `--augment-count` 增加而增加。
* 对于首次 500 MiB 测试，建议先运行 `--no-augment`，然后在较小的 `--limit` 样本上开启 GPT。

## 9. 如何检查结果

检查行数：

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect("new_capd_datebase.db")
print("sentences:", conn.execute("select count(*) from sentences").fetchone()[0])
print("latest runs:")
for row in conn.execute("""
select id, status, scorer, processed_count, success_count, skipped_count, failed_count, augmented_count, started_at, completed_at
from pipeline_runs
order by id desc
limit 5
"""):
    print(row)
conn.close()
PY

```

检查上下文类型分布：

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect("new_capd_datebase.db")
for row in conn.execute("select context_type, source, count(*) from sentences group by context_type, source"):
    print(row)
conn.close()
PY

```

## 10. 实际操作建议

* 从 `--max-input-mb 10` 或 `--limit 100` 开始以确认环境配置。
* 然后尝试 `--max-input-mb 100`。
* 最后运行 `--max-input-mb 500`。
* 始终保持开启 `--resume`，以便中断后继续运行。
* 在 BERT/LTP 吞吐量达到预期前，保持开启 `--no-augment`。
* 在稳定的 GPU 服务器上，将 `--batch-size` 增加到 32 或 64，以减少数据库更新开销。
* **切勿**提交 `new_capd_datebase.db`、`.env`、原始语料 dump 文件、生成的缓存文件或 API 密钥。

## 11. 是否需要更改代码？

是的。为了支持您的目标工作流，进行了两项小改动：

* 增加了 `--max-input-mb`：使流水线能处理数 GB 语料库的前 500 MiB，无需手动切分文件。
* 增加了 `--device auto|cpu|cuda`：使 BERT 可以显式地在 GPU 上运行。

之前的源文件已备份至：`data_pipeline/source_backups/`。