import os
import sys
import docx
import argparse
from pathlib import Path

def doc_to_txt(doc_path):
    """
    将doc/docx文件转换为txt文件
    
    Args:
        doc_path: doc/docx文件路径
    
    Returns:
        转换后的txt文件路径
    """
    try:
        # 打开doc文件
        doc = docx.Document(doc_path)
        
        # 提取文本内容
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        
        # 生成输出文件路径，保持原文件名，只改扩展名为.txt
        output_path = str(Path(doc_path).with_suffix('.txt'))
        
        # 写入txt文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(full_text))
        
        print(f"成功转换: {doc_path} -> {output_path}")
        return output_path
    
    except Exception as e:
        print(f"转换文件 {doc_path} 失败: {str(e)}")
        return None

def batch_convert(directory, recursive=False):
    """
    批量转换目录中的所有doc/docx文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归处理子目录
    """
    processed = 0
    failed = 0
    
    pattern = '**/*.docx' if recursive else '*.docx'
    for doc_file in Path(directory).glob(pattern):
        if doc_to_txt(str(doc_file)):
            processed += 1
        else:
            failed += 1
    
    # 处理.doc文件
    pattern = '**/*.doc' if recursive else '*.doc'
    for doc_file in Path(directory).glob(pattern):
        if doc_to_txt(str(doc_file)):
            processed += 1
        else:
            failed += 1
    
    print(f"\n转换完成: {processed} 个文件成功, {failed} 个文件失败")

def main():
    parser = argparse.ArgumentParser(description='将doc/docx文件转换为txt文件')
    parser.add_argument('input', help='输入的doc/docx文件或包含doc/docx文件的目录')
    parser.add_argument('-r', '--recursive', action='store_true', help='如果输入是目录，是否递归处理子目录')
    
    args = parser.parse_args()
    input_path = args.input
    
    if os.path.isfile(input_path):
        # 处理单个文件
        if input_path.lower().endswith(('.doc', '.docx')):
            doc_to_txt(input_path)
        else:
            print(f"错误: {input_path} 不是有效的doc/docx文件")
    
    elif os.path.isdir(input_path):
        # 处理整个目录
        batch_convert(input_path, args.recursive)
    
    else:
        print(f"错误: 输入路径 {input_path} 不存在")

if __name__ == "__main__":
    main() 