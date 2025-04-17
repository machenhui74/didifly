# 文档转JPG工具

一个简单易用的工具，可以将PDF或Word文档转换为JPG图片格式。

## 功能特点

- 支持PDF文件转JPG
- 支持Word文档(.doc/.docx)转JPG
- 图形用户界面，简单易用
- 可调整输出图片DPI(质量)
- 多页文档自动分页输出
- 实时转换日志显示

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：

```bash
python doc2jpg.py
```

2. 在界面中选择文档文件（PDF或Word）
3. 选择输出目录（可选，默认与源文件相同目录）
4. 调整DPI值（可选，默认300）
5. 点击"开始转换"按钮
6. 等待转换完成，查看输出目录中的JPG文件

## 需求环境

- Python 3.6 或更高版本
- Windows、macOS 或 Linux 系统

## 依赖库

- PyMuPDF - 用于PDF处理
- Pillow - 用于图像处理
- python-docx2pdf - 用于Word转PDF
- tkinter - 用于图形界面（Python标准库）

## 注意事项

1. Word文档转换需要系统安装Microsoft Word或LibreOffice
2. 大文件转换可能需要较长时间
3. 高DPI值会产生更大的图片文件 