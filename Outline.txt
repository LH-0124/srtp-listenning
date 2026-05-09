CAPD_Server_Backend/
│
├── data_pipeline/          				# [离线部分]
│   ├── __init__.py         				# (新建空文件，标记为包)
│   ├── raw_data/            				# [文件夹] 请放入 corpus.txt
│   ├── preprocess.py        				# 1. 清洗数据
│   ├── context_scoring.py   			   # 2. BERT评分
│   ├── llm_augment.py       			   # 3. 扩充句子
│   ├── database_manager.py  			   # 4. 数据库操作
│   ├── run_pipeline.py      				# 5. [入口] 执行整个离线处理流程
│   └── similar_sentences_output.txt	# llm_argument.py的示例文件
│
├── server/                 				# [在线部分]
│   ├── __init__.py          				# (新建空文件)
│   ├── models.py            				# 数据模型 (Pydantic)
│   ├── adaptive_logic.py    			   # 自适应算法
│   ├── audio_service.py     				# 音频处理 (TTS+Librosa)
│   └── main.py              				# FastAPI 主程序
│
├── assets/                  				# [自动生成] 存放音频
├── capd_database.db         			   # [自动生成] 数据库
└── requirements.txt         				# 依赖库

使用说明：
1. 搜索▲可以找到可调参数。
2. 在 data_pipeline 文件夹下运行run_pipeline.py文件，先下载相应的库

操作指令：
HP@LAPTOP-00OLPTDR MINGW64 /d/Program Files/Project/CAPD_Server_Backend (master)
$ git add .

HP@LAPTOP-00OLPTDR MINGW64 /d/Program Files/Project/CAPD_Server_Backend (master)
$ git commit -m "Update the back_end project"
[master 0fa7675] Update the back_end project
 18 files changed, 1034 insertions(+), 1389 deletions(-)
 create mode 100644 Log.txt
 create mode 100644 data_pipeline/README.txt
 create mode 100644 data_pipeline/raw_data/corpus - 副本.txt
 create mode 100644 data_pipeline/similar_sentences_output.txt

HP@LAPTOP-00OLPTDR MINGW64 /d/Program Files/Project/CAPD_Server_Backend (master)
$ git push origin master
fatal: unable to access 'https://github.com/LH-0124/srtp-listenning.git/': Failed to connect to github.com port 443 after 21097 ms: Could not connect to server

HP@LAPTOP-00OLPTDR MINGW64 /d/Program Files/Project/CAPD_Server_Backend (master)
$  git push origin master
Enumerating objects: 38, done.
Counting objects: 100% (38/38), done.
Delta compression using up to 16 threads
Compressing objects: 100% (22/22), done.
Writing objects: 100% (22/22), 19.27 KiB | 1.75 MiB/s, done.
Total 22 (delta 7), reused 0 (delta 0), pack-reused 0 (from 0)
remote: Resolving deltas: 100% (7/7), completed with 6 local objects.
To https://github.com/LH-0124/srtp-listenning.git
   f2f2959..0fa7675  master -> master
