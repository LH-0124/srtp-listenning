-----2025.11.24-----
建立好模型的初步大纲

-----2025.12.04-----
1. 采用哈工大LPT分词方式和WWM全词掩码工具 
2. 调用GPT-3.5-turbo大模型进行文本生成

ToDo：搜索分词器，查找最佳的分词工具以及掩码策略。
分词方式：jieba分词、bert的WordPiece分词
掩码方式：wwm全词掩码

分词方法-https://zhuanlan.zhihu.com/p/580782591
wwm掩码方式-https://github.com/ymcui/Chinese-BERT-wwm、https://zhuanlan.zhihu.com/p/366396747、https://blog.csdn.net/weixin_49518391/article/details/126988107
微调-https://aistudio.baidu.com/projectdetail/4459155?channelType=0&channel=0
语料库-https://github.com/brightmart/nlp_chinese_corpus?tab=readme-ov-file#3%E7%99%BE%E7%A7%91%E9%97%AE%E7%AD%94baike2018qa150%E4%B8%87%E4%B8%AA%E5%B8%A6%E9%97%AE%E9%A2%98%E7%B1%BB%E5%9E%8B%E7%9A%84%E9%97%AE%E7%AD%94 、 https://github.com/EndlessLethe/jddc2019-3th-retrieve-model/tree/master/data 、 https://github.com/zll17/Neural_Topic_Models?tab=readme-ov-file#datasets 、 https://blog.csdn.net/Thanours/article/details/118368742

-----2025.12.05-----

微调：[bert需要gpu吗_mob64ca13f9a97c的技术博客_51CTO博客](https://blog.51cto.com/u_16213589/13748682)

[目前，微调一个类似 BERT 的模型进行文本分类最简单的方法是什么？ : r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/comments/1bum24a/currently_whats_the_easiest_way_to_fine_tune_a/?tl=zh-hans)

[【大模型】微调一个大模型需要多少 GPU 显存？_微调大模型需要多少显存-CSDN博客](https://blog.csdn.net/u012856866/article/details/146870846)

[微调bert方法-How to Fine-Tune BERT for Text Classification?笔记 - 知乎](https://zhuanlan.zhihu.com/p/649997216)

[15.7. 自然语言推断：微调BERT — 动手学深度学习 2.0.0 documentation](https://zh.d2l.ai/chapter_natural-language-processing-applications/natural-language-inference-bert.html)

[PyTorch 的 BERT 微调教程 | XUNGE's Blog](https://xungejiang.com/2020/06/06/BERT/)
