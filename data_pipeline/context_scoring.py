import torch
from transformers import BertTokenizer, BertForMaskedLM,BertTokenizerFast
import jieba
from ltp import LTP
import numpy as np

class ContextScorer:
    def __init__(self, model_name='hfl/chinese-bert-wwm-ext', ltp_path=None):
        """
        初始化评分器
        :param model_name: 使用哈工大讯飞的全词掩码模型 'hfl/chinese-bert-wwm-ext'
        :param ltp_path: LTP 模型路径，如果不传则自动下载/加载默认模型
        """
        print(f"正在加载 BERT 模型: {model_name} ...")
        # 使用 Fast 分词器以获取 offset_mapping，用于对齐 LTP 分词结果
        self.tokenizer = BertTokenizerFast.from_pretrained(model_name)
        self.model = BertForMaskedLM.from_pretrained(model_name)
        self.model.eval()

        print("正在加载 LTP 分词模型 (首次运行可能需要下载) ...")
        # 加载 LTP，默认使用 small 模型，速度快效果好
        self.ltp = LTP(ltp_path) if ltp_path else LTP()

    def calculate_score(self, sentence: str) -> float:
        """
        计算句子语境分（Context Score）：
        策略：遍历句子中的每一个词 (LTP分词)，对其进行全词掩码 (WWM)，
        计算 BERT 对原词预测的平均置信度。
        
        返回: 0.0 (低语境/难猜) - 1.0 (高语境/好猜/俗套)
        """
        if (not sentence) or len(sentence.strip()) == 0:
            return 0.5

        # 1. LTP 分词：获取词语列表
        # ltp.pipeline 返回对象，output.cws 是分词结果列表
        ltp_output = self.ltp.pipeline([sentence], tasks=["cws"])
        words = ltp_output.cws[0] # List[str], 例如 ['我', '喜欢', '深度学习']
        
        if len(words) < 2: 
            return 0.5 # 词数太少，无法有效评估上下文

        # 2. BERT Tokenize：获取 Token 和 字符偏移量映射
        # return_offsets_mapping=True 让我们可以知道每个 token 对应原句的哪些字符
        inputs = self.tokenizer(sentence, return_tensors="pt", return_offsets_mapping=True)
        input_ids = inputs["input_ids"][0]
        offsets = inputs["offset_mapping"][0] # List[(start, end)]

        # 3. 构建词语的字符跨度 (Span)
        # LTP 不直接返回 offset，我们需要累加长度计算
        word_spans = [] 
        cursor = 0
        for word in words:
            start = cursor
            end = cursor + len(word)
            word_spans.append((start, end))
            cursor = end

        word_scores = []

        # 4. 遍历每个词，进行全词掩码预测
        for w_start, w_end in word_spans:
            # 找到该词对应的 BERT Token 索引列表
            mask_token_indices = []
            for idx, (t_start, t_end) in enumerate(offsets):
                if t_start == t_end: continue # 跳过 [CLS], [SEP] 等特殊字符
                # 如果 Token 的范围落在当前词的范围内，则归属该词
                # 注意：这里做简单的包含判断
                if t_start >= w_start and t_end <= w_end:
                    mask_token_indices.append(idx)
            
            if not mask_token_indices:
                continue

            # --- 构造 Mask 输入 ---
            masked_input_ids = input_ids.clone()
            masked_input_ids[mask_token_indices] = self.tokenizer.mask_token_id
            
            # --- BERT 预测 ---
            with torch.no_grad():
                outputs = self.model(masked_input_ids.unsqueeze(0))
                predictions = outputs.logits[0] # [seq_len, vocab_size]

            # --- 计算置信度 ---
            # 我们取该词包含的所有 Token 的预测置信度（Top Probability）的平均值
            # 这里的 Top Prob 代表“BERT 认为这里最应该填什么”，越高代表语境约束越强
            token_confidences = []
            for t_idx in mask_token_indices:
                probs = torch.nn.functional.softmax(predictions[t_idx], dim=-1)
                top_prob = torch.max(probs).item()
                token_confidences.append(top_prob)
            
            if token_confidences:
                # 当前这个词的“好猜程度”
                word_scores.append(np.mean(token_confidences))

        # 5. 聚合整个句子的分数
        if not word_scores:
            return 0.5
        
        # 返回所有词语分数的均值
        return float(np.mean(word_scores))

    def detect_anomaly(self, sentence: str, threshold: float = 20.0) -> bool:
        """
        文本异常检测：基于伪困惑度 (Pseudo-Perplexity, PPL)。
        如果 PPL 过高，说明句子不通顺或逻辑混乱（BERT 觉得这句话“很怪”）。
        
        :param threshold: 困惑度阈值，通常 20-50 之间，需根据数据调整。
        :return: True (异常) / False (正常)
        """
        if not sentence: return True
        
        # 使用 Pseudo-PPL 计算方法：累加每个 Token 在 Mask 下的 Loss
        inputs = self.tokenizer(sentence, return_tensors="pt")
        input_ids = inputs["input_ids"]
        labels = input_ids.clone()
        
        total_loss = 0
        tokens_count = 0
        
        # 这里的策略是：逐个 Mask 每一个 Token，看原 Token 的概率
        # 为了效率，可以分批次做，这里为了清晰演示逐个做 (Loop)
        seq_len = input_ids.size(1)
        
        # 跳过 [CLS] 和 [SEP]
        for i in range(1, seq_len - 1):
            masked_input = input_ids.clone()
            masked_input[0, i] = self.tokenizer.mask_token_id
            
            with torch.no_grad():
                outputs = self.model(masked_input)
                predictions = outputs.logits[0, i] # [vocab_size]
            
            # 获取原真实字符的 Log Probability
            original_token_id = labels[0, i]
            log_probs = torch.nn.functional.log_softmax(predictions, dim=-1)
            token_log_prob = log_probs[original_token_id].item()
            
            total_loss -= token_log_prob
            tokens_count += 1
            
        if tokens_count == 0: return False

        # PPL = exp(total_loss / N)
        ppl = np.exp(total_loss / tokens_count)
        
        # print(f"Sentence: {sentence[:10]}... | PPL: {ppl:.2f}") # 调试用
        
        return ppl > threshold