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
    # ContextScorer 会自动加载 WWM BERT 模型和 LTP 分词工具
    scorer = ContextScorer() 
    
    # 定义原始文本/语料库 文件(的路径)：raw_path = raw_data/corpus.txt
    raw_path = os.path.join(os.path.dirname(__file__), 'raw_data', 'corpus.txt')
    # 输出 txt 文件的路径
    output_txt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'processed_corpus.txt')

    # 错误检测
    if not os.path.exists(raw_path):
        print(f"错误: 未找到文件 {raw_path}")
        return

    print(">>> 开始处理数据...")
    
    # 用于收集所有最终句子的列表，方便写入 txt
    final_sentences_list = []

    with open(raw_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 记录处理数量
    count = 0

    # 开始循环处理每一行，但是开销大，后续可考虑多线程或分布式处理
    for line in lines:
        # A. 清洗
        text = clean_text(line)
        if not text: continue
        
        #  A'. 取消原始句子异常检测
        #if scorer.detect_anomaly(text, threshold = 35.0):
        #    print(f"警告: 原始句子 '{text[:10]}...' PPL过高，判定为异常，跳过处理。")
        #    continue
        
        # B. 打分
        score = scorer.calculate_score(text)
        
        # C. 分类 (阈值可调，新 WWM 分数可能偏低，注意调整阈值)
        context_type = "HIGH" if score > 0.4 else "LOW" 
        
        # D. 入库 (原始句子)
        insert_sentence(text, context_type, score)
        
        # 添加到列表用于保存txt
        final_sentences_list.append(f"{text}\t{context_type}\t{score:.4f}")
        
        print(f"处理: {text[:10]}... | 分数: {score:.4f} | 类型: {context_type}")
        count += 1
        
        # E. 低语境句子扩充
        if context_type == "LOW":
            augmented_list = generate_similar_sentences(text,num_variants=3)    # ▲可调参数：num_variants
            
            valid_augmented_count = 0
            for aug_text in augmented_list:
                # E'. 对AI生成句子进行异常检测
                if scorer.detect_anomaly(aug_text, threshold = 35.0):   # ▲可以调整threshold阈值
                     print(f"    -> 警告: 扩充句子 '{aug_text[:10]}...' PPL过高，判定为异常，跳过入库。")
                     continue
                
                # 只有当扩充句子和原句不一样时才保存
                if aug_text != text: 
                    # 扩充句子的分数和类型沿用原句
                    insert_sentence(aug_text, "LOW", score)
                    final_sentences_list.append(f"{aug_text}\tLOW\t{score:.4f}")
                    valid_augmented_count += 1
            
            if valid_augmented_count > 0:
                print(f"    -> 成功扩充并入库 {valid_augmented_count} 条有效低语境句子。")


    # 保存为 TXT 文件
    print(f"\n>>> 正在导出到文本文件: {output_txt_path}")
    with open(output_txt_path, 'w', encoding='utf-8') as f_out:
        f_out.write("句子内容\t类型\t语境分\n") # 表头
        for item in final_sentences_list:
            f_out.write(item + "\n")

    print(f">>> 数据处理完成！共处理有效原始句子 {count} 条。")
    print(f">>> 数据库已更新: capd_database.db")
    print(f">>> 文本已导出: processed_corpus.txt")

if __name__ == "__main__":
    main()