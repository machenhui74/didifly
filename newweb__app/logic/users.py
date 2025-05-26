"""
用户管理相关功能
处理用户的增删改查操作
"""

import re
from .auth import (USERS, save_users, encrypt_password, UserRole, DEFAULT_USER_ROLE, 
                   log_permission_change, can_modify_user_role, ROLE_NAMES, 
                   can_create_user, get_user_role, update_created_users_count)
from ..utils.logger import get_logger

logger = get_logger('users')

def validate_password_strength(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    
    if len(password) > 20:
        return False, "密码长度不能超过20位"
    
    # 检查是否包含字母和数字
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not (has_letter and has_digit):
        return False, "密码必须包含字母和数字"
    
    return True, ""

def add_user(username, password, name, store='', role=None, operator_id=None):
    """
    添加新用户
    
    Args:
        username: 用户账号
        password: 密码
        name: 用户姓名
        store: 训练中心
        role: 用户权限角色，默认为测评师
        operator_id: 操作者ID（用于校长创建限制检查）
    """
    if username in USERS:
        return False, "用户已存在！"
    
    # 检查操作者是否有创建用户的权限
    if operator_id:
        can_create, error_msg = can_create_user(operator_id)
        if not can_create:
            return False, error_msg
    
    # 验证密码强度
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return False, error_msg
    
    # 设置默认权限
    if role is None:
        role = DEFAULT_USER_ROLE
    
    # 验证权限角色
    if role not in [UserRole.ADMIN, UserRole.PRINCIPAL, UserRole.ASSESSOR, UserRole.TEACHER]:
        return False, f"无效的权限角色: {role}"
    
    # 校长权限限制：只能创建测评师和老师
    if operator_id and get_user_role(operator_id) == UserRole.PRINCIPAL:
        if role not in [UserRole.ASSESSOR, UserRole.TEACHER]:
            return False, "校长只能创建测评师和老师账户"
    
    # 管理员权限限制：不能创建管理员账户
    if operator_id and get_user_role(operator_id) == UserRole.ADMIN:
        if role == UserRole.ADMIN:
            return False, "管理员不能创建其他管理员账户"
    
    # 初始化用户数据结构
    user_data = {
        'password': encrypt_password(password),
        'name': name,
        'store': store,
        'role': role,
        'is_encrypted': True
    }
    
    # 如果是校长角色，初始化创建用户相关字段
    if role == UserRole.PRINCIPAL:
        user_data['created_users_count'] = 0
        user_data['created_users_list'] = []
    
    USERS[username] = user_data
    
    if save_users(USERS):
        logger.info(f"新用户添加成功: {username} ({name}) - 权限: {role}")
        
        # 更新校长创建用户计数
        if operator_id:
            update_created_users_count(operator_id, username)
            save_users(USERS)  # 保存更新后的计数
        
        # 记录权限分配日志（新用户）
        log_permission_change(username, None, role, operator_id)
        
        return True, "用户添加成功！"
    
    return False, "用户添加失败，无法保存数据！"

def update_user(username, password=None, name=None, store=None, role=None, operator_id=None):
    """
    更新用户信息
    
    Args:
        username: 用户账号
        password: 新密码（可选）
        name: 新姓名（可选）
        store: 新训练中心（可选）
        role: 新权限角色（可选）
        operator_id: 操作者ID（用于权限检查和日志记录）
    """
    if username not in USERS:
        return False, "用户不存在！"
    
    # 更新密码
    if password:
        # 验证密码强度
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return False, error_msg
            
        USERS[username]['password'] = encrypt_password(password)
        USERS[username]['is_encrypted'] = True
    
    # 更新姓名
    if name:
        USERS[username]['name'] = name
    
    # 更新训练中心
    if store is not None:  # 允许空字符串作为商店名
        USERS[username]['store'] = store
    
    # 更新权限角色
    if role is not None:
        # 验证权限角色
        if role not in [UserRole.ADMIN, UserRole.PRINCIPAL, UserRole.ASSESSOR, UserRole.TEACHER]:
            return False, f"无效的权限角色: {role}"
        
        # 检查权限修改权限
        if operator_id:
            can_modify, error_msg = can_modify_user_role(operator_id, username)
            if not can_modify:
                return False, error_msg
        
        old_role = USERS[username].get('role', DEFAULT_USER_ROLE)
        
        # 只有权限真正发生变化时才记录日志
        if old_role != role:
            USERS[username]['role'] = role
            
            # 记录权限变更日志
            log_permission_change(username, old_role, role, operator_id)
            
            logger.info(f"用户 {username} 权限变更: {old_role} -> {role} (操作人: {operator_id})")
    
    if save_users(USERS):
        logger.info(f"用户信息更新成功: {username}")
        return True, "用户信息更新成功！"
    
    return False, "用户信息更新失败，无法保存数据！"

def update_user_role(username, new_role, operator_id):
    """
    专门用于更新用户权限的函数
    
    Args:
        username: 目标用户账号
        new_role: 新的权限角色
        operator_id: 操作者ID
    """
    if username not in USERS:
        return False, "用户不存在！"
    
    # 验证权限角色
    if new_role not in [UserRole.ADMIN, UserRole.PRINCIPAL, UserRole.ASSESSOR, UserRole.TEACHER]:
        return False, f"无效的权限角色: {new_role}"
    
    # 检查权限修改权限
    can_modify, error_msg = can_modify_user_role(operator_id, username)
    if not can_modify:
        return False, error_msg
    
    # 额外的管理员权限控制验证
    operator_role = get_user_role(operator_id)
    if operator_role == UserRole.ADMIN and new_role == UserRole.ADMIN:
        return False, "管理员不能将其他用户提升为管理员级别"
    
    # 校长权限控制验证
    if operator_role == UserRole.PRINCIPAL and new_role in [UserRole.ADMIN, UserRole.PRINCIPAL]:
        return False, "校长不能将用户提升为管理员或校长级别"
    
    old_role = USERS[username].get('role', DEFAULT_USER_ROLE)
    
    # 如果权限没有变化，直接返回成功
    if old_role == new_role:
        return True, f"用户权限已经是{ROLE_NAMES.get(new_role, new_role)}，无需修改"
    
    # 更新权限
    USERS[username]['role'] = new_role
    
    if save_users(USERS):
        # 记录权限变更日志
        log_permission_change(username, old_role, new_role, operator_id)
        
        logger.info(f"用户 {username} 权限变更成功: {old_role} -> {new_role} (操作人: {operator_id})")
        return True, f"用户权限已更新为{ROLE_NAMES.get(new_role, new_role)}"
    
    return False, "权限更新失败，无法保存数据！"

def delete_user(username):
    """删除用户"""
    if username not in USERS:
        return False, "用户不存在！"
    
    if username == 'admin':
        return False, "不能删除管理员账号！"
    
    user_info = USERS[username]
    del USERS[username]
    
    if save_users(USERS):
        logger.info(f"用户删除成功: {username} ({user_info.get('name', '')})")
        return True, "用户删除成功！"
    
    return False, "用户删除失败，无法保存数据！" 

def get_user_info(username):
    """获取用户信息"""
    if username not in USERS:
        return None
    
    user_data = USERS[username].copy()
    # 不返回密码信息
    user_data.pop('password', None)
    user_data.pop('is_encrypted', None)
    
    return user_data

def list_users():
    """获取所有用户列表"""
    users_list = []
    for username, user_data in USERS.items():
        user_info = {
            'username': username,
            'name': user_data.get('name', ''),
            'store': user_data.get('store', ''),
            'role': user_data.get('role', DEFAULT_USER_ROLE),
            'role_name': ROLE_NAMES.get(user_data.get('role', DEFAULT_USER_ROLE), '未知')
        }
        users_list.append(user_info)
    
    return users_list

def get_available_roles(operator_role=None):
    """获取可用的权限角色列表"""
    all_roles = [
        {'value': UserRole.ADMIN, 'name': ROLE_NAMES[UserRole.ADMIN]},
        {'value': UserRole.PRINCIPAL, 'name': ROLE_NAMES[UserRole.PRINCIPAL]},
        {'value': UserRole.ASSESSOR, 'name': ROLE_NAMES[UserRole.ASSESSOR]},
        {'value': UserRole.TEACHER, 'name': ROLE_NAMES[UserRole.TEACHER]}
    ]
    
    # 根据操作者权限过滤可选角色
    if operator_role == UserRole.PRINCIPAL:
        # 校长只能创建/修改测评师和老师
        return [role for role in all_roles if role['value'] in [UserRole.ASSESSOR, UserRole.TEACHER]]
    elif operator_role == UserRole.ADMIN:
        # 管理员不能将其他用户提升为管理员
        return [role for role in all_roles if role['value'] != UserRole.ADMIN]
    
    return all_roles

def filter_manageable_users(operator_id):
    """根据操作者权限过滤可管理的用户列表"""
    operator_role = get_user_role(operator_id)
    
    # 管理员可以管理所有用户
    if operator_role == UserRole.ADMIN:
        return USERS
    
    # 校长只能管理同训练中心的用户和自己创建的用户
    if operator_role == UserRole.PRINCIPAL:
        operator_store = USERS.get(operator_id, {}).get('store', '')
        created_users = USERS.get(operator_id, {}).get('created_users_list', [])
        
        filtered_users = {}
        for username, user_data in USERS.items():
            # 跳过自己
            if username == operator_id:
                continue
            
            # 跳过管理员和其他校长
            user_role = user_data.get('role', UserRole.ASSESSOR)
            if user_role in [UserRole.ADMIN, UserRole.PRINCIPAL]:
                continue
            
            # 同训练中心或自己创建的用户
            user_store = user_data.get('store', '')
            if user_store == operator_store or username in created_users:
                filtered_users[username] = user_data
        
        return filtered_users
    
    # 其他角色不能管理用户
    return {}