import torch
from transformers import BertTokenizer, BertForMaskedLM
import jieba
import numpy as np

class ContextScorer:
    def __init__(self, model_name='bert-base-chinese'):
        print(f"正在加载 BERT 模型: {model_name} ...")
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertForMaskedLM.from_pretrained(model_name)
        self.model.eval()

    def calculate_score(self, sentence: str) -> float:
        """
        计算句子语境分：MASK掉一个实词，看BERT预测的置信度。
        返回: 0.0 (低语境/难猜) - 1.0 (高语境/好猜)
        """
        words = list(jieba.cut(sentence))
        if len(words) < 3: return 0.5

        # 简单的策略：Mask掉中间的词
        mask_idx = len(words) // 2
        masked_words = words.copy()
        masked_words[mask_idx] = '[MASK]'
        masked_sentence = "".join(masked_words)

        inputs = self.tokenizer(masked_sentence, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = outputs.logits

        # 找到MASK的位置
        try:
            mask_token_index = (inputs.input_ids == self.tokenizer.mask_token_id)[0].nonzero(as_tuple=True)[0]
            # 获取预测概率
            probs = torch.nn.functional.softmax(predictions[0, mask_token_index], dim=-1)
            # 获取置信度最高的token的概率
            top_prob = torch.max(probs).item()
            return top_prob
        except:
            return 0.5