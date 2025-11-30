# 这里你需要填入你的 大模型 API Key (如 OpenAI, 文心一言等)
# 为了保证代码能直接跑，这里写一个 Mock (模拟) 函数

def generate_similar_sentences(seed_sentence: str) -> list:
    """
    [模拟] 调用大模型，根据输入的低语境句子，生成结构相似的句子
    """
    # TODO: 实际项目中替换为 requests.post 调用 GPT API
    # prompt = f"请仿照这句话的句式造3个新句子：{seed_sentence}"
    
    # 模拟返回：
    return [
        f"{seed_sentence} (变体1)",
        f"{seed_sentence} (变体2)"
    ]