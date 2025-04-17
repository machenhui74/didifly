#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量转换文档为JPG图片的命令行工具
"""

import os
import sys
import argparse
import glob
from pathlib import Path
from doc2jpg import DocToJpgConverter, logger

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="批量将PDF或Word文档转换为JPG图片")
    
    parser.add_argument(
        "input_path",
        help="输入文件或目录路径"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        help="输出目录路径，默认为与输入文件相同的目录"
    )
    
    parser.add_argument(
        "-d", "--dpi",
        type=int,
        default=300,
        help="输出图片的DPI值，默认为300"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="递归处理子目录中的文件"
    )
    
    parser.add_argument(
        "-e", "--extensions",
        default="pdf,docx,doc",
        help="要处理的文件扩展名，逗号分隔，默认为pdf,docx,doc"
    )
    
    return parser.parse_args()

def find_files(input_path, extensions, recursive=False):
    """查找指定扩展名的文件"""
    files = []
    ext_list = [f".{ext.lower().strip()}" for ext in extensions.split(",")]
    
    # 如果输入路径是文件
    if os.path.isfile(input_path):
        file_path = Path(input_path)
        if file_path.suffix.lower() in ext_list:
            files.append(str(file_path))
        return files
    
    # 如果输入路径是目录
    input_dir = Path(input_path)
    
    # 根据是否递归选择不同的方式查找文件
    if recursive:
        for ext in ext_list:
            # 使用 rglob 递归查找
            for file_path in input_dir.rglob(f"*{ext}"):
                files.append(str(file_path))
    else:
        for ext in ext_list:
            # 使用 glob 只在当前目录查找
            for file_path in input_dir.glob(f"*{ext}"):
                files.append(str(file_path))
    
    return sorted(files)

def main():
    """主函数"""
    args = parse_arguments()
    
    # 创建转换器
    converter = DocToJpgConverter()
    
    # 查找文件
    files = find_files(args.input_path, args.extensions, args.recursive)
    
    if not files:
        logger.error(f"在 {args.input_path} 中未找到任何符合条件的文件")
        return
    
    logger.info(f"找到 {len(files)} 个文件需要转换")
    
    # 设置输出目录
    output_dir = args.output_dir
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 开始批量转换
    total_files = len(files)
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(files, 1):
        logger.info(f"[{i}/{total_files}] 处理文件: {file_path}")
        
        try:
            result_files = converter.convert_file(file_path, output_dir, args.dpi)
            
            if result_files:
                logger.info(f"转换成功，生成了 {len(result_files)} 个JPG文件")
                successful += 1
            else:
                logger.error(f"转换失败")
                failed += 1
        
        except Exception as e:
            logger.error(f"转换出错: {str(e)}")
            failed += 1
    
    # 输出统计信息
    logger.info("=" * 50)
    logger.info(f"批量转换完成:")
    logger.info(f"- 总文件数: {total_files}")
    logger.info(f"- 成功: {successful}")
    logger.info(f"- 失败: {failed}")

if __name__ == "__main__":
    main() 