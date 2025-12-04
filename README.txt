CAPD_Server_Backend/
│
├── data_pipeline/          				# [离线部分]
│   ├── __init__.py         				# (新建空文件，标记为包)
│   ├── raw_data/            				# [文件夹] 请放入 corpus.txt
│   ├── preprocess.py        				# 1. 清洗数据
│   ├── context_scoring.py   			    # 2. BERT评分
│   ├── llm_augment.py       			    # 3. 扩充句子
│   ├── database_manager.py  			    # 4. 数据库操作
│   ├── run_pipeline.py      				# 5. [入口] 执行整个离线处理流程
│   └── similar_sentences_output.txt		# llm_argument.py的示例文件
│
├── server/                 				# [在线部分]
│   ├── __init__.py          				# (新建空文件)
│   ├── models.py            				# 数据模型 (Pydantic)
│   ├── adaptive_logic.py    			    # 自适应算法
│   ├── audio_service.py     				# 音频处理 (TTS+Librosa)
│   └── main.py              				# FastAPI 主程序
│
├── assets/                  				# [自动生成] 存放音频
├── capd_database.db         			    # [自动生成] 数据库
└── requirements.txt         				# 依赖库

使用说明：
1. 搜索▲可以找到可调参数。
2. 在 data_pipeline 文件夹下运行run_pipeline.py文件，先下载相应的库