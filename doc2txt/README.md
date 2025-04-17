# Doc2Txt 转换工具

这是一个简单的工具，用于将Word文档(doc/docx文件)转换为纯文本(txt)文件，并保留原有文件名。

## 功能特点

- 支持单个文件转换
- 支持批量转换目录中的所有doc/docx文件
- 支持递归转换子目录中的文件
- 保留原有文件名，仅更改扩展名为.txt

## 安装

1. 确保已安装Python 3.6或更高版本
2. 安装依赖库：

```
pip install -r requirements.txt
```

## 使用方法

### 转换单个文件：

```
python doc2txt.py 文件路径.docx
```

### 转换目录中的所有doc/docx文件：

```
python doc2txt.py 目录路径
```

### 递归转换目录及其子目录中的所有doc/docx文件：

```
python doc2txt.py 目录路径 -r
```

## 示例

```
# 转换单个文件
python doc2txt.py example.docx

# 转换当前目录中的所有doc/docx文件
python doc2txt.py .

# 递归转换docs目录及其子目录中的所有doc/docx文件
python doc2txt.py docs -r
```

## 注意事项

- 本工具只支持.doc和.docx格式的Word文档
- 转换后的txt文件将保存在原文档的相同位置
- 如果已经存在同名的txt文件，将被覆盖 