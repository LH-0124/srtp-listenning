import os
import requests
import json
from typing import List
from dotenv import load_dotenv

# --- 1. 配置和常量 ---

# 加载 .env 文件中的环境变量
load_dotenv()

# API Key 
# 安全获取，如果没配置则报错提醒
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

GPT_API_URL = os.getenv("GPT_API_URL", "https://api.openai.com/v1/chat/completions")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-3.5-turbo")

OUTPUT_FILENAME = "similar_sentences_output.txt"

# --- 2. 核心函数：调用大模型 ---

def generate_similar_sentences(seed_sentence: str, num_variants: int = 3) -> List[str]:
    """
    调用 GPT API，根据输入的种子句子，生成结构相似的句子。
    Args:
        seed_sentence: 待仿写的低语境句子。
        num_variants: 期望生成的新句子数量。
    Returns:
        一个包含仿写句子的列表。
    """
    # a.构建发送给 GPT 的提示词 (Prompt)
    prompt = f"""
    请仿照以下句子的句式和结构，根据其内容，生成 {num_variants} 个结构相似但措辞不同的新句子。
    请严格返回一个 JSON 数组，数组中只包含生成的句子字符串，不要包含任何额外的解释、编号或Markdown格式（如```json）。

    种子句子: "{seed_sentence}"

    示例输出格式:
    ["新句子1", "新句子2", "新句子3"]
    """
    
    # === 调用 GPT API ===

    # 创建HTTP请求头：告诉服务器发送的是JSON数据；使用身份验证，API密钥
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    # 创建请求数据（payload）
    payload = {
        "model": GPT_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个精通语言风格和句式仿写的语言学家。你的任务是严格按照用户要求的格式输出仿写结果。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8, # ▲可调参数
        "max_tokens": 512,  # ▲可调参数
        "response_format": {"type": "json_object"}
    }
    
    print(f"--- 正在调用 {GPT_MODEL} 生成句子，种子句：{seed_sentence} ---")

    try:
        response = requests.post(GPT_API_URL, headers=headers, data=json.dumps(payload), timeout=30)
        
        # 检查 HTTP 状态码，特别是 401 (API Key 错误) 或 429 (频率限制)
        if response.status_code != 200:
            # 4. 如果API不对给出适当的输出 (HTTP 错误处理)
            print(f"❌ API 调用失败，HTTP 状态码: {response.status_code}")
            try:
                error_details = response.json().get('error', {}).get('message', '无详细错误信息')
            except json.JSONDecodeError:
                error_details = response.text
                
            if response.status_code == 401:
                return [f"错误：API Key 无效或格式错误，请检查您的 Key。详细信息: {error_details}"]
            
            return [f"错误：API 请求失败 (状态码 {response.status_code})。详细信息: {error_details}"]

        
        # 成功响应解析
        response_data = response.json()
        message_content = response_data['choices'][0]['message']['content']
        
        # 尝试解析 JSON 字符串
        try:
            result_list = json.loads(message_content)
            
            if isinstance(result_list, list):
                return result_list
            elif isinstance(result_list, dict):
                 # 兼容模型有时将数组放入字典的情况
                key = list(result_list.keys())[0]
                return result_list[key]
            else:
                print(f"❌ 解析结果格式不符合预期，原始输出：{message_content}")
                return [f"错误：API返回格式异常"]
                
        except json.JSONDecodeError:
            print(f"❌ API 返回内容不是有效 JSON，原始文本：{message_content}")
            return [f"错误：API返回内容无法解析"]


    except requests.exceptions.RequestException as e:
        # 4. 如果API不对给出适当的输出 (网络错误处理)
        print(f"❌ 调用 API 失败: 网络连接或请求超时错误: {e}")
        return [f"错误：网络连接或请求失败 ({str(e)})"]
    
# --- 3. 示例调用和 TXT 输出 ---

def write_to_txt(original: str, variants: List[str]):
    """将结果写入 TXT 文件。"""
    # xt格式的输出
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        f.write("========== 句子仿写结果 ==========\n\n")
        f.write(f"原始句子: {original}\n")
        f.write(f"模型 ({GPT_MODEL}) 生成的仿写变体 ({len(variants)}个):\n")
        f.write("-" * 30 + "\n")
        for i, sentence in enumerate(variants):
            f.write(f"  {i+1}. {sentence}\n")
        f.write("\n========== 结束 ==========\n")
        
    print(f"\n✅ 结果已成功写入文件: {OUTPUT_FILENAME}")


if __name__ == '__main__':
    # 示例低语境句子
    low_context_sentence = "她拿着那把伞。"
    # 调用函数生成类似的话语
    similar_sentences = generate_similar_sentences(low_context_sentence, num_variants=10)
    # 将结果写入 TXT 文件
    write_to_txt(low_context_sentence, similar_sentences)
