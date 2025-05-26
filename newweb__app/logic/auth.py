"""
用户认证和权限管理模块
处理用户登录验证、权限检查、密码加密等功能
"""

import os
import json
import hashlib
import logging
from functools import wraps
from datetime import datetime
from flask import current_app, session, redirect, url_for, flash

# 初始化日志记录器
logger = logging.getLogger(__name__)

# 全局用户数据字典，将在应用初始化时填充
USERS = {}

# -----------------------------
# 权限常量定义
# -----------------------------

class UserRole:
    """用户角色常量"""
    ADMIN = 'admin'        # 管理员：所有功能
    PRINCIPAL = 'principal'  # 校长：管理同训练中心+创建的账户
    ASSESSOR = 'assessor'  # 测评师：现有用户功能
    TEACHER = 'teacher'    # 老师：限制功能

# 权限级别映射（数字越大权限越高）
ROLE_LEVELS = {
    UserRole.TEACHER: 1,
    UserRole.ASSESSOR: 2,
    UserRole.PRINCIPAL: 3,
    UserRole.ADMIN: 4
}

# 权限角色中文名称映射
ROLE_NAMES = {
    UserRole.ADMIN: '管理员',
    UserRole.PRINCIPAL: '校长',
    UserRole.ASSESSOR: '测评师',
    UserRole.TEACHER: '老师'
}

# 默认权限配置
DEFAULT_USER_ROLE = UserRole.ASSESSOR  # 新用户默认为测评师

# -----------------------------
# 密码加密和验证函数
# -----------------------------

def encrypt_password(password):
    """加密密码"""
    # 使用SHA-256加密
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_password, provided_password):
    """验证密码"""
    # 对提供的密码进行加密，然后与存储的密码比较
    provided_hash = encrypt_password(provided_password)
    return provided_hash == stored_password

# -----------------------------
# 权限变更日志管理
# -----------------------------

def load_permission_logs():
    """加载权限变更日志"""
    logs_file_path = current_app.config.get('PERMISSION_LOGS_FILE', 'data/permission_logs.json')
    if os.path.exists(logs_file_path):
        try:
            with open(logs_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载权限变更日志时出错: {str(e)}")
    return []

def save_permission_logs(logs):
    """保存权限变更日志"""
    try:
        logs_file_path = current_app.config.get('PERMISSION_LOGS_FILE', 'data/permission_logs.json')
        # 确保目录存在
        os.makedirs(os.path.dirname(logs_file_path), exist_ok=True)
        
        with open(logs_file_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存权限变更日志时出错: {str(e)}")
        return False

def log_permission_change(target_user, old_role, new_role, operator_user=None):
    """记录权限变更日志"""
    if operator_user is None:
        operator_user = session.get('user_id', 'system')
    
    # 获取操作者角色信息，用于安全审计
    operator_role = get_user_role(operator_user)
    operator_role_name = ROLE_NAMES.get(operator_role, operator_role)
    
    log_entry = {
        'id': f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{target_user}",
        'timestamp': datetime.now().isoformat(),
        'target_user': target_user,
        'target_user_name': USERS.get(target_user, {}).get('name', ''),
        'old_role': old_role,
        'new_role': new_role,
        'old_role_name': ROLE_NAMES.get(old_role, old_role) if old_role else '新用户',
        'new_role_name': ROLE_NAMES.get(new_role, new_role),
        'operator_user': operator_user,
        'operator_name': USERS.get(operator_user, {}).get('name', ''),
        'operator_role': operator_role,
        'operator_role_name': operator_role_name,
        'action': 'role_change' if old_role else 'user_create'
    }
    
    logs = load_permission_logs()
    logs.insert(0, log_entry)  # 最新的记录在前面
    
    # 保留最近100条记录
    if len(logs) > 100:
        logs = logs[:100]
    
    if save_permission_logs(logs):
        action_desc = "权限变更" if old_role else "用户创建"
        logger.info(f"{action_desc}日志记录成功: {target_user} {old_role or '新用户'} -> {new_role} (操作人: {operator_user}[{operator_role_name}])")
        return True
    
    return False

def get_permission_logs(limit=50):
    """获取权限变更日志"""
    logs = load_permission_logs()
    return logs[:limit] if limit else logs

def get_user_permission_logs(user_id, limit=20):
    """获取指定用户的权限变更日志"""
    all_logs = load_permission_logs()
    user_logs = [log for log in all_logs if log.get('target_user') == user_id]
    return user_logs[:limit] if limit else user_logs

# -----------------------------
# 用户数据管理函数
# -----------------------------

def load_users():
    """加载用户数据"""
    users_file_path = current_app.config['USERS_FILE']
    if os.path.exists(users_file_path):
        try:
            with open(users_file_path, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                
                # 为现有用户添加默认权限（向后兼容）
                for username, user_info in users_data.items():
                    if 'role' not in user_info:
                        # admin用户设为管理员，其他用户设为测评师
                        user_info['role'] = UserRole.ADMIN if username == 'admin' else UserRole.ASSESSOR
                        logger.info(f"为用户 {username} 添加默认权限: {user_info['role']}")
                
                # 保存更新后的用户数据
                save_users(users_data)
                return users_data
        except Exception as e:
            logger.error(f"加载用户数据时出错: {str(e)}")
    
    # 默认用户数据
    default_users = {
        'admin': {
            'password': encrypt_password('admin123'),
            'name': '管理员',
            'store': '总部',
            'role': UserRole.ADMIN,
            'is_encrypted': True
        }
    }
    
    # 保存默认用户数据
    save_users(default_users)
    return default_users

def save_users(users):
    """保存用户数据"""
    users_file_path = current_app.config['USERS_FILE']
    try:
        with open(users_file_path, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"保存用户数据时出错: {str(e)}")
        return False

# 新增：用于在应用上下文中初始化用户数据的函数
def init_users_data(app_instance):
    """在 Flask 应用上下文中加载和初始化全局 USERS 字典"""
    global USERS
    with app_instance.app_context():
        loaded_users = load_users() # load_users 内部使用 current_app
        USERS.clear() # 清除旧数据（如果应用重载等情况）
        USERS.update(loaded_users)
        logger.info("User data initialized.")

# -----------------------------
# 权限验证函数
# -----------------------------

def get_user_role(user_id=None):
    """获取用户权限角色"""
    if user_id is None:
        user_id = session.get('user_id')
    
    if not user_id or user_id not in USERS:
        return None
    
    return USERS[user_id].get('role', UserRole.ASSESSOR)

def has_permission(required_role, user_id=None):
    """检查用户是否有指定权限"""
    user_role = get_user_role(user_id)
    if not user_role:
        return False
    
    user_level = ROLE_LEVELS.get(user_role, 0)
    required_level = ROLE_LEVELS.get(required_role, 0)
    
    return user_level >= required_level

def can_modify_user_role(operator_id, target_user_id):
    """检查操作者是否可以修改目标用户的权限"""
    operator_role = get_user_role(operator_id)
    target_role = get_user_role(target_user_id)
    
    # 管理员和校长可以修改权限
    if operator_role not in [UserRole.ADMIN, UserRole.PRINCIPAL]:
        return False, "只有管理员或校长可以修改用户权限"
    
    # 不能修改自己的权限
    if operator_id == target_user_id:
        return False, "不能修改自己的权限"
    
    # 校长权限限制
    if operator_role == UserRole.PRINCIPAL:
        # 校长不能修改管理员和其他校长的权限
        if target_role in [UserRole.ADMIN, UserRole.PRINCIPAL]:
            return False, "校长不能修改管理员或其他校长的权限"
        
        # 校长只能管理同训练中心的用户或自己创建的用户
        operator_store = USERS.get(operator_id, {}).get('store', '')
        target_store = USERS.get(target_user_id, {}).get('store', '')
        created_users = USERS.get(operator_id, {}).get('created_users_list', [])
        
        if target_store != operator_store and target_user_id not in created_users:
            return False, "校长只能管理同训练中心的用户或自己创建的用户"
    
    # 管理员权限限制
    if operator_role == UserRole.ADMIN:
        # 不能修改其他管理员的权限（除非是超级管理员逻辑，这里暂不实现）
        if target_role == UserRole.ADMIN and target_user_id != 'admin':
            return False, "不能修改其他管理员的权限"
        
        # 管理员不能将其他用户提升为管理员（防止权限滥用）
        # 这个检查将在update_user_role函数中进行，这里只是记录日志
    
    return True, ""

def can_create_user(operator_id):
    """检查操作者是否可以创建新用户"""
    operator_role = get_user_role(operator_id)
    
    # 管理员可以无限制创建用户
    if operator_role == UserRole.ADMIN:
        return True, ""
    
    # 校长有创建限制
    if operator_role == UserRole.PRINCIPAL:
        created_count = USERS.get(operator_id, {}).get('created_users_count', 0)
        if created_count >= 10:
            return False, "校长最多只能创建10个账户"
        return True, ""
    
    # 其他角色不能创建用户
    return False, "您没有权限创建新用户"

def update_created_users_count(operator_id, new_user_id):
    """更新校长创建的用户计数和列表"""
    if operator_id not in USERS:
        return False
    
    operator_role = get_user_role(operator_id)
    if operator_role != UserRole.PRINCIPAL:
        return True  # 非校长用户不需要更新计数
    
    # 更新创建用户计数
    current_count = USERS[operator_id].get('created_users_count', 0)
    USERS[operator_id]['created_users_count'] = current_count + 1
    
    # 更新创建用户列表
    created_users = USERS[operator_id].get('created_users_list', [])
    if new_user_id not in created_users:
        created_users.append(new_user_id)
        USERS[operator_id]['created_users_list'] = created_users
    
    return True

def get_user_training_center(user_id=None):
    """获取用户所属训练中心"""
    if user_id is None:
        user_id = session.get('user_id')
    
    if not user_id or user_id not in USERS:
        return None
    
    return USERS[user_id].get('store', '')

# -----------------------------
# 认证装饰器
# -----------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录！', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not has_permission(UserRole.ADMIN):
            flash('您没有权限访问此页面！', 'error')
            # 根据用户权限重定向到合适的页面
            user_role = session.get('user_role', 'assessor')
            if user_role == UserRole.TEACHER:
                return redirect(url_for('main.teacher_welcome'))
            else:
                return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def principal_required(f):
    """校长权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not has_permission(UserRole.PRINCIPAL):
            flash('您没有权限访问此页面！', 'error')
            # 根据用户权限重定向到合适的页面
            user_role = session.get('user_role', 'assessor')
            if user_role == UserRole.TEACHER:
                return redirect(url_for('main.teacher_welcome'))
            else:
                return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """角色权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_permission(required_role):
                flash('您没有权限访问此页面！', 'error')
                # 根据用户权限重定向到合适的页面
                user_role = session.get('user_role', 'assessor')
                if user_role == UserRole.TEACHER:
                    return redirect(url_for('main.teacher_welcome'))
                else:
                    return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def assessor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not has_permission(UserRole.ASSESSOR):
            flash('您没有权限访问此页面！', 'error')
            # 根据用户权限重定向到合适的页面
            user_role = session.get('user_role', 'assessor')
            if user_role == UserRole.TEACHER:
                return redirect(url_for('main.teacher_welcome'))
            else:
                return redirect(url_for('auth.login'))  # 如果连测评师权限都没有，重定向到登录页
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """老师及以上权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not has_permission(UserRole.TEACHER):
            flash('您没有权限访问此页面！', 'error')
            return redirect(url_for('auth.login'))  # 如果连老师权限都没有，重定向到登录页
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