data_pipeline/           # [离线部分]
│
│   ├── __init__.py          # (新建空文件，标记为包)
│   ├── raw_data/            # [文件夹] 请放入 corpus.txt
│   ├── preprocess.py        # 1. 清洗数据
│   ├── context_scoring.py   # 2. BERT评分
│   ├── llm_augment.py       # 3. 扩充句子
│   ├── database_manager.py  # 4. 数据库操作
│   └── run_pipeline.py      # [入口] 执行整个离线处理流程