#!/bin/bash
# 生产环境启动脚本

echo "🚀 启动学生评估系统..."

# 加载环境变量
if [ -f .env.prod ]; then
    export $(cat .env.prod | grep -v '^#' | xargs)
    echo "✅ 加载生产环境配置"
else
    echo "⚠️  未找到 .env.prod 文件"
fi

# 启动应用
echo "🌐 启动Web服务器..."
waitress-serve --host=0.0.0.0 --port=8080 start_production:app
