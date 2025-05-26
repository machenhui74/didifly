#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
故障排除脚本
诊断Flask应用部署问题
"""

import os
import sys
import json
import importlib.util

def check_python_environment():
    """检查Python环境"""
    print("🐍 Python环境检查:")
    print(f"   Python版本: {sys.version}")
    print(f"   Python路径: {sys.executable}")
    print(f"   当前工作目录: {os.getcwd()}")
    print()

def check_required_modules():
    """检查必需的模块"""
    print("📦 模块依赖检查:")
    required_modules = ['flask', 'waitress', 'openpyxl', 'docx']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}: 已安装")
        except ImportError:
            print(f"   ❌ {module}: 未安装")
    print()

def check_file_structure():
    """检查文件结构"""
    print("📁 文件结构检查:")
    
    required_files = [
        'production_app.py',
        'production_config.py',
        'newweb__app/__init__.py',
        'newweb__app/logic/auth.py',
        'newweb__app/routes_original.py'
    ]
    
    required_dirs = [
        'data',
        'logs',
        'newweb__app',
        'newweb__app/logic'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}: 存在")
        else:
            print(f"   ❌ {file_path}: 缺失")
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/: 存在")
        else:
            print(f"   ❌ {dir_path}/: 缺失")
    print()

def check_data_files():
    """检查数据文件"""
    print("💾 数据文件检查:")
    
    data_files = [
        'data/users.json',
        'data/student_profiles.json',
        'data/permission_logs.json'
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"   ✅ {file_path}: 存在且格式正确")
            except Exception as e:
                print(f"   ⚠️  {file_path}: 存在但格式错误 - {e}")
        else:
            print(f"   ❌ {file_path}: 不存在")
    print()

def test_app_import():
    """测试应用导入"""
    print("🧪 应用导入测试:")
    
    try:
        # 测试生产配置导入
        from production_config import get_production_config
        config = get_production_config()
        print("   ✅ 生产配置导入成功")
    except Exception as e:
        print(f"   ❌ 生产配置导入失败: {e}")
        return False
    
    try:
        # 测试应用创建
        from production_app import create_production_app
        app = create_production_app()
        if app:
            print("   ✅ 应用创建成功")
            return True
        else:
            print("   ❌ 应用创建失败")
            return False
    except Exception as e:
        print(f"   ❌ 应用创建异常: {e}")
        return False

def check_port_availability():
    """检查端口可用性"""
    print("🔌 端口检查:")
    
    import socket
    
    def is_port_open(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    
    if is_port_open('localhost', 8080):
        print("   ⚠️  端口8080已被占用")
    else:
        print("   ✅ 端口8080可用")
    print()

def create_minimal_test_app():
    """创建最小测试应用"""
    print("🔧 创建最小测试应用:")
    
    test_app_code = '''
from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_key'

@app.route('/')
def hello():
    return "Hello, World! 应用运行正常"

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
'''
    
    try:
        with open('test_app.py', 'w', encoding='utf-8') as f:
            f.write(test_app_code)
        print("   ✅ 最小测试应用已创建: test_app.py")
        print("   💡 可以运行: python test_app.py 或 waitress-serve --host=0.0.0.0 --port=8080 test_app:app")
    except Exception as e:
        print(f"   ❌ 创建测试应用失败: {e}")
    print()

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 Flask应用部署故障排除")
    print("=" * 60)
    print()
    
    check_python_environment()
    check_required_modules()
    check_file_structure()
    check_data_files()
    check_port_availability()
    
    app_success = test_app_import()
    
    if not app_success:
        create_minimal_test_app()
    
    print("=" * 60)
    print("🎯 故障排除建议:")
    print()
    print("1. 如果模块缺失，运行: pip install flask waitress openpyxl python-docx")
    print("2. 如果文件缺失，确保所有必要文件都已上传到服务器")
    print("3. 如果端口被占用，使用其他端口或停止占用进程")
    print("4. 如果应用导入失败，先测试最小应用: python test_app.py")
    print("5. 检查服务器防火墙设置，确保8080端口开放")
    print()
    print("🆘 如果问题仍然存在，请查看详细错误日志")
    print("=" * 60)

if __name__ == '__main__':
    main() 