@echo off
chcp 65001
echo 🚀 开始部署Flask应用到Windows服务器...

REM 1. 检查Python环境
echo 📋 检查Python环境...
python --version
pip --version

REM 2. 安装必要的依赖
echo 📦 安装Python依赖...
pip install flask waitress

REM 如果有requirements.txt，安装所有依赖
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo ⚠️  未找到requirements.txt，手动安装基础依赖...
    pip install flask waitress openpyxl python-docx
)

REM 3. 创建必要的目录
echo 📁 创建必要目录...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist data\templates mkdir data\templates
if not exist data\reports mkdir data\reports
if not exist data\training_plans mkdir data\training_plans
if not exist data\source_materials mkdir data\source_materials
if not exist data\student_training_plans mkdir data\student_training_plans

REM 4. 测试应用是否能正常启动
echo 🧪 测试应用启动...
start /B python production_app.py
timeout /t 5 /nobreak > nul
taskkill /f /im python.exe > nul 2>&1

REM 5. 使用waitress启动应用
echo 🎯 使用Waitress启动生产环境应用...
echo 访问地址: http://localhost:8080
echo 按 Ctrl+C 停止应用

REM 启动应用
waitress-serve --host=0.0.0.0 --port=8080 production_app:app 