import re

def clean_text(text: str) -> str:
    """
    清洗文本：去除说话人标签、英文语气词，但保留中文及标点。
    """
    if not text:
        return None
    
    # 1. 去除说话人标签，如 <S00>, <N01>
    #  原始数据包含 <S00> 等标签
    text = re.sub(r'<[a-zA-Z0-9]+>', '', text)
    
    # 2. 去除英文单词 (如 eng, erm)
    #  原始数据包含 eng
    text = re.sub(r'[a-zA-Z]+', '', text)
    
    # 3. 只保留：汉字 + 中文标点 (，。？！、)
    # 这里的正则含义：保留 汉字 OR 标点
    text = re.sub(r'[^\u4e00-\u9fa5，。？！、]', '', text)
    
    # 4. 去除多余的空白
    text = text.strip()
    
    # 5. 再次过滤：如果去完标签后长度太短（比如全是语气词），丢弃
    if len(text) < 4:
        return None
        
    return text