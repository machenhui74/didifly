#!/bin/bash

# 服务器部署脚本
# 解决Flask应用在云服务器上的部署问题

echo "🚀 开始部署Flask应用到服务器..."

# 1. 检查Python环境
echo "📋 检查Python环境..."
python3 --version
pip3 --version

# 2. 安装必要的依赖
echo "📦 安装Python依赖..."
pip3 install flask waitress

# 如果有requirements.txt，安装所有依赖
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "⚠️  未找到requirements.txt，手动安装基础依赖..."
    pip3 install flask waitress openpyxl python-docx
fi

# 3. 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p data
mkdir -p logs
mkdir -p data/templates
mkdir -p data/reports
mkdir -p data/training_plans
mkdir -p data/source_materials
mkdir -p data/student_training_plans

# 4. 设置文件权限
echo "🔐 设置文件权限..."
chmod +x production_app.py
chmod 755 data
chmod 755 logs

# 5. 检查端口是否被占用
echo "🔍 检查端口8080..."
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  端口8080已被占用，请先停止占用该端口的进程"
    lsof -Pi :8080 -sTCP:LISTEN
    exit 1
fi

# 6. 测试应用是否能正常启动
echo "🧪 测试应用启动..."
timeout 10s python3 production_app.py &
TEST_PID=$!
sleep 5

if kill -0 $TEST_PID 2>/dev/null; then
    echo "✅ 应用测试启动成功"
    kill $TEST_PID
else
    echo "❌ 应用测试启动失败"
    exit 1
fi

# 7. 使用waitress启动应用
echo "🎯 使用Waitress启动生产环境应用..."
echo "访问地址: http://$(hostname -I | awk '{print $1}'):8080"
echo "按 Ctrl+C 停止应用"

# 启动应用
waitress-serve --host=0.0.0.0 --port=8080 production_app:app 