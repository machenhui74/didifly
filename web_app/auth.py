from flask import redirect, url_for, flash, session
import os
import json
import hashlib
import base64
import secrets
import logging
from functools import wraps
from config import DATA_FOLDER, USERS_FILE

# 初始化日志记录器
logger = logging.getLogger(__name__)

# -----------------------------
# 密码管理函数
# -----------------------------

def encrypt_password(password):
    """使用SHA-256哈希算法加盐处理密码"""
    salt = secrets.token_hex(8)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                  salt.encode('utf-8'), 100000)
    pwdhash = base64.b64encode(pwdhash).decode('utf-8')
    return f"{salt}${pwdhash}"

def verify_password(stored_password, provided_password):
    """验证密码"""
    salt, stored_hash = stored_password.split('$')
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), 
                                 salt.encode('utf-8'), 100000)
    pwdhash = base64.b64encode(pwdhash).decode('utf-8')
    return pwdhash == stored_hash

# -----------------------------
# 用户数据管理函数
# -----------------------------

def load_users():
    """加载用户数据"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载用户数据时出错: {str(e)}")
    
    # 默认用户数据
    default_users = {
        'admin': {
            'password': encrypt_password('admin123'),
            'name': '管理员',
            'store': '总部',
            'is_encrypted': True
        }
    }
    
    # 保存默认用户数据
    save_users(default_users)
    return default_users

def save_users(users):
    """保存用户数据"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"保存用户数据时出错: {str(e)}")
        return False

# 加载用户数据
USERS = load_users()

# -----------------------------
# 认证装饰器
# -----------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录！', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['user_id'] != 'admin':
            flash('您没有权限访问此页面！', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------
# 认证路由处理函数
# -----------------------------

def login_user(username, password):
    """用户登录验证"""
    if username in USERS:
        user_data = USERS[username]
        # 检查密码是否已加密
        if user_data.get('is_encrypted', False):
            # 验证加密密码
            if verify_password(user_data['password'], password):
                return user_data, True
        else:
            # 处理旧格式的未加密密码
            if user_data['password'] == password:
                # 更新为加密密码
                USERS[username]['password'] = encrypt_password(password)
                USERS[username]['is_encrypted'] = True
                save_users(USERS)
                return user_data, True
    return None, False 