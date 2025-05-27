#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
以 UTF-8 编码重新写入 requirements.txt 文件，解决编码问题。
移除所有中文注释，仅保留包名和版本号。
"""

requirements_content = """
Flask==3.1.0
docxtpl==0.20.0
python-dotenv==1.1.0
pandas==2.2.3
python-docx==1.1.2
openpyxl==3.1.5
Flask-WTF==1.2.1
# Dependencies of the above packages, with fixed versions
Babel==2.17.0
blinker==1.9.0
click==8.2.0
itsdangerous==2.2.0
Jinja2==3.1.6
lxml==5.4.0
MarkupSafe==3.0.2
numpy==2.2.6
python-dateutil==2.9.0.post0
pytz==2025.2
six==1.17.0
Werkzeug==3.1.3
et_xmlfile==2.0.0 # openpyxl dependency
# colorama, setuptools are usually not direct app dependencies, typing_extensions is for type hinting
"""

def main():
    try:
        with open("requirements.txt", "w", encoding="utf-8", newline="\n") as f: # Explicitly set newline to LF
            f.write(requirements_content.strip() + "\n") # strip() 移除可能的前后空白，并确保末尾有换行
        print("✅ requirements.txt 文件已成功以 UTF-8 编码重写 (无中文注释)。")
    except Exception as e:
        print(f"❌ 重写 requirements.txt 文件失败: {e}")

if __name__ == "__main__":
    main() 