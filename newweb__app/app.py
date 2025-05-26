#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主应用程序入口
运行方法：python app.py
"""

import sys
import os
import logging

# 添加项目根目录到 Python 路径，确保能够正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from newweb__app import create_app
except ImportError:
    # 如果从newweb__app目录内部运行，尝试直接导入
    from __init__ import create_app

app = create_app()

if __name__ == '__main__':
    # 配置日志级别
    logging.basicConfig(level=logging.DEBUG)
    # 启动应用
    print("==============================================")
    print("标签管理系统正在启动...")
    print("请访问：http://127.0.0.1:5000")
    print("==============================================")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"应用启动失败: {e}")
        logging.error(f"应用启动失败: {e}")
        sys.exit(1) 