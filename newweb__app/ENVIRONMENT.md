# 🔧 **Newweb__app 环境配置完整指南**

*最后更新时间: 2024年12月19日*

---

## 📋 **快速开始**

### 1. 复制环境变量文件
```bash
# 项目已为您创建了 .env 文件
# 如需重新设置，可以从模板复制：
cp env.example .env
```

### 2. 验证 .gitignore 配置
✅ `.env` 文件已在 `.gitignore` 中被正确配置忽略  
✅ 确保 `.env` 文件不会被提交到版本控制系统

---

## 🔐 **核心安全配置**

### `SECRET_KEY`
**用途**: Flask 应用密钥，用于会话加密和安全功能  
**类型**: 字符串  
**必需**: 生产环境必需，开发环境可选  
**默认值**: `dev_secret_key_please_change_in_production_newweb`  

```bash
# 生成强密钥（推荐方法）
python -c "import secrets; print(secrets.token_hex(32))"

# 设置环境变量
export SECRET_KEY="your_generated_secret_key_here"
```

⚠️ **注意**: 生产环境必须设置自定义密钥，否则应用启动失败！

### `FLASK_ENV`
**用途**: 运行环境设置  
**类型**: 字符串  
**可选值**: `development`, `production`, `testing`  
**默认值**: `development`  

```bash
# 开发环境
export FLASK_ENV=development

# 生产环境
export FLASK_ENV=production

# 测试环境
export FLASK_ENV=testing
```

### `FLASK_DEBUG`
**用途**: 调试模式开关  
**类型**: 布尔值  
**默认值**: 根据 `FLASK_ENV` 自动设置  

```bash
# 启用调试模式
export FLASK_DEBUG=true

# 禁用调试模式（生产环境推荐）
export FLASK_DEBUG=false
```

---

## 🌐 **Web 服务器配置**

### `HOST`
**用途**: 服务器监听地址  
**类型**: IP 地址字符串  
**默认值**: `127.0.0.1`  

```bash
# 本地访问
export HOST=127.0.0.1

# 网络访问
export HOST=0.0.0.0
```

### `PORT`
**用途**: 服务器监听端口  
**类型**: 整数  
**默认值**: `5000`  

```bash
export PORT=8080
```

### `SESSION_TIMEOUT_HOURS`
**用途**: Session 超时时间（小时）  
**类型**: 整数  
**默认值**: `2`  

```bash
export SESSION_TIMEOUT_HOURS=4
```

---

## 📁 **数据存储路径配置**

### `DATA_FOLDER`
**用途**: 数据文件夹根目录（用户数据、配置文件存储）  
**类型**: 路径字符串  
**默认值**: `./data`（相对于应用根目录）  

```bash
# 相对路径（推荐）
export DATA_FOLDER=./data

# 绝对路径
export DATA_FOLDER=/app/data
```

### `SOURCE_FOLDER`
**用途**: 源文件夹路径（训练资料来源）  
**类型**: 路径字符串  
**默认值**: `./data/source_materials`  

```bash
# Windows 示例
export SOURCE_FOLDER=D:\\训练资料

# Linux 示例
export SOURCE_FOLDER=/home/user/training_materials
```

### `DESTINATION_FOLDER`
**用途**: 目标文件夹路径（生成的学员训练方案存储位置）  
**类型**: 路径字符串  
**默认值**: `./data/student_training_plans`  

```bash
# Windows 示例
export DESTINATION_FOLDER=D:\\学员训练方案

# Linux 示例
export DESTINATION_FOLDER=/home/user/student_training_plans
```

---

## 📊 **报告和文档配置**

### `REPORT_TEMPLATE_PATH`
**用途**: 报告模板文件路径（.docx 格式）  
**类型**: 文件路径字符串  
**默认值**: `./data/templates/test_report_template.docx`  
**注意**: 确保文件存在且可读  

```bash
export REPORT_TEMPLATE_PATH=./data/templates/test_report_template.docx
```

### `REPORT_OUTPUT_FOLDER`
**用途**: 报告输出文件夹（生成的测评报告存储位置）  
**类型**: 路径字符串  
**默认值**: `./data/reports`  

```bash
export REPORT_OUTPUT_FOLDER=./data/reports
```

---

## 🏃‍♂️ **感统训练方案配置**

### `TRAINING_ACTION_DB_PATH`
**用途**: 训练动作数据库文件路径（.xlsx 格式）  
**类型**: 文件路径字符串  
**默认值**: `./data/action_database.xlsx`  
**说明**: 包含所有可用的训练动作和参数  

```bash
export TRAINING_ACTION_DB_PATH=./data/action_database.xlsx
```

### `TRAINING_PLAN_OUTPUT_FOLDER`
**用途**: 训练方案输出文件夹（生成的个性化训练方案）  
**类型**: 路径字符串  
**默认值**: `./data/training_plans`  

```bash
export TRAINING_PLAN_OUTPUT_FOLDER=./data/training_plans
```

---

## 📝 **日志配置**

### `LOG_LEVEL`
**用途**: 日志级别设置  
**类型**: 字符串  
**可选值**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`  
**默认值**: `INFO`  

```bash
# 详细调试日志
export LOG_LEVEL=DEBUG

# 生产环境推荐
export LOG_LEVEL=WARNING
```

### `LOG_FILE`
**用途**: 日志文件路径  
**类型**: 文件路径字符串  
**默认值**: `./logs/app.log`  

```bash
export LOG_FILE=./logs/app.log
```

---

## 📤 **文件上传配置**

### `MAX_UPLOAD_SIZE`
**用途**: 文件上传大小限制（MB）  
**类型**: 整数  
**默认值**: `50`  

```bash
export MAX_UPLOAD_SIZE=100
```

---

## 🔧 **环境配置验证**

### 验证环境变量是否正确加载：

```python
# 创建测试脚本 test_config.py
import os
from config import *

print("🔍 环境变量配置检查:")
print(f"SECRET_KEY: {'✅ 已设置' if SECRET_KEY != 'dev_secret_key_please_change_in_production_newweb' else '⚠️ 使用默认值'}")
print(f"DATA_FOLDER: {DATA_FOLDER}")
print(f"SOURCE_FOLDER: {SOURCE_FOLDER}")
print(f"DESTINATION_FOLDER: {DESTINATION_FOLDER}")

# 检查文件夹是否存在
folders = [DATA_FOLDER, DESTINATION_FOLDER, REPORT_OUTPUT_FOLDER, TRAINING_PLAN_OUTPUT_FOLDER]
for folder in folders:
    exists = "✅" if os.path.exists(folder) else "❌"
    print(f"文件夹 {folder}: {exists}")
```

### 运行验证：
```bash
python test_config.py
```

---

## 🚀 **启动应用**

### 开发环境启动：
```bash
# 确保虚拟环境已激活
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 启动应用
python app.py
```

### 生产环境启动：
```bash
# 使用 gunicorn（推荐）
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app

# 或使用 waitress（Windows 推荐）
pip install waitress
waitress-serve --port=5000 app:app
```

---

## 📊 **环境变量优先级**

1. **系统环境变量** （最高优先级）
2. **`.env` 文件**
3. **代码中的默认值** （最低优先级）

### 设置系统环境变量（可选）：

**Windows PowerShell:**
```powershell
$env:SECRET_KEY="your_production_secret_key"
$env:FLASK_ENV="production"
```

**Linux/Mac:**
```bash
export SECRET_KEY="your_production_secret_key"
export FLASK_ENV="production"
```

---

## 🌍 **多环境配置示例**

### 开发环境 (.env.development):
```bash
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=dev_secret_key
HOST=127.0.0.1
PORT=5000
LOG_LEVEL=DEBUG
DATA_FOLDER=./data
```

### 生产环境 (.env.production):
```bash
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your_secure_production_key
HOST=0.0.0.0
PORT=80
LOG_LEVEL=WARNING
DATA_FOLDER=/var/lib/newweb_app
```

### 测试环境 (.env.testing):
```bash
FLASK_ENV=testing
FLASK_DEBUG=false
SECRET_KEY=test_secret_key
HOST=127.0.0.1
PORT=5001
LOG_LEVEL=INFO
DATA_FOLDER=./test_data
```

---

## 🛠️ **故障排除**

### 常见问题：

1. **路径错误** (FileNotFoundError)
   ```bash
   # 检查路径是否存在
   # Windows: 使用双反斜杠 \\
   # Linux: 使用正斜杠 /
   ```

2. **权限错误** (PermissionError)
   ```bash
   # 确保应用有读写权限
   chmod 755 /path/to/directory  # Linux
   ```

3. **SECRET_KEY 警告**
   ```bash
   # 生产环境必须设置自定义密钥
   SECRET_KEY=your_secure_random_key
   ```

4. **端口占用**
   ```bash
   # Windows: 查找占用端口的进程
   netstat -ano | findstr :5000
   
   # 杀死进程
   taskkill /F /PID <进程ID>
   ```

### 调试环境变量：
```python
# 在 Python 中检查环境变量
import os
print("当前环境变量:")
for key, value in os.environ.items():
    if 'SECRET' not in key:  # 不打印敏感信息
        print(f"{key}: {value}")
```

---

## 📝 **最佳实践**

1. **版本控制安全**
   - 永远不要提交 `.env` 文件到版本控制
   - 维护 `env.example` 作为模板

2. **生产环境安全**
   - 使用强随机密钥
   - 禁用调试模式
   - 设置适当的日志级别

3. **路径管理**
   - 使用相对路径便于部署
   - 确保所有必需目录存在
   - 检查文件和目录权限

4. **监控和日志**
   - 定期检查日志文件
   - 设置日志轮转避免文件过大
   - 监控应用性能和错误

---

## 🔄 **环境变量热更新**

⚠️ **重要**: 修改环境变量后需要重启应用才能生效

### 开发环境快速重启：
```bash
# 停止应用 (Ctrl+C)
# 重新启动
python app.py
```

---

**📖 更多信息请参考项目根目录的 `README.md` 和 `PROGRESS_CHECKLIST.md` 文档。** 