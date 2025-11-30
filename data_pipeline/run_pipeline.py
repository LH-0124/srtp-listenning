import os
import sys

# 确保能引用同级模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocess import clean_text
from context_scoring import ContextScorer
from llm_augment import generate_similar_sentences
from database_manager import init_db, insert_sentence

def main():
    # 1. 初始化 
    init_db()
    scorer = ContextScorer()
    
    # 定义路径
    raw_path = os.path.join(os.path.dirname(__file__), 'raw_data', 'corpus.txt')
    # 输出 txt 文件的路径
    output_txt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'processed_corpus.txt')

    if not os.path.exists(raw_path):
        print(f"错误: 未找到文件 {raw_path}")
        return

    print(">>> 开始处理数据...")
    
    # 用于收集所有最终句子的列表，方便写入 txt
    final_sentences_list = []

    with open(raw_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        # A. 清洗
        text = clean_text(line)
        if not text: continue
        
        # B. 打分
        score = scorer.calculate_score(text)
        
        # C. 分类 (阈值可调，比如0.5)
        context_type = "HIGH" if score > 0.4 else "LOW" 
        
        # D. 入库 (原始句子)
        insert_sentence(text, context_type, score)
        
        # 添加到列表用于保存txt
        final_sentences_list.append(f"{text}\t{context_type}\t{score:.4f}")
        
        print(f"处理: {text[:10]}... | 分数: {score:.4f} | 类型: {context_type}")
        count += 1
        
        # E. (可选) 低语境句子扩充
        # 注意：这里模拟扩充的句子也应该存入 txt，如果你需要的话
        if context_type == "LOW":
            augmented_list = generate_similar_sentences(text)
            for aug_text in augmented_list:
                # 只有当扩充句子和原句不一样时才保存
                if aug_text != text: 
                    insert_sentence(aug_text, "LOW", score)
                    final_sentences_list.append(f"{aug_text}\tLOW\t{score:.4f}")

    # 保存为 TXT 文件
    print(f"\n>>> 正在导出到文本文件: {output_txt_path}")
    with open(output_txt_path, 'w', encoding='utf-8') as f_out:
        f_out.write("句子内容\t类型\t语境分\n") # 表头
        for item in final_sentences_list:
            f_out.write(item + "\n")

    print(f">>> 数据处理完成！共处理有效句子 {count} 条。")
    print(f">>> 数据库已更新: capd_database.db")
    print(f">>> 文本已导出: processed_corpus.txt")

if __name__ == "__main__":
    main()