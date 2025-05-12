from auth import USERS, save_users, encrypt_password
import re

def validate_password_strength(password):
    """
    验证密码强度
    
    要求:
    - 至少8位长度
    - 包含大写字母
    - 包含小写字母
    - 包含数字
    - 包含特殊字符
    
    返回: (bool, str) - (是否通过验证, 错误信息)
    """
    if len(password) < 8:
        return False, "密码长度必须至少为8位！"
    
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母！"
    
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母！"
    
    if not re.search(r'[0-9]', password):
        return False, "密码必须包含至少一个数字！"
    
    if not re.search(r'[^A-Za-z0-9]', password):
        return False, "密码必须包含至少一个特殊字符！"
    
    return True, ""

def add_user(username, password, name, store):
    """添加新用户"""
    if username in USERS:
        return False, "账号已存在！"
    
    # 验证密码强度
    if password:
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return False, error_msg
    
    USERS[username] = {
        'password': encrypt_password(password),
        'name': name,
        'store': store,
        'is_encrypted': True
    }
    
    if save_users(USERS):
        return True, "用户添加成功！"
    return False, "用户添加失败，无法保存数据！"

def update_user(username, password=None, name=None, store=None):
    """更新用户信息"""
    if username not in USERS:
        return False, "用户不存在！"
    
    if password:
        # 验证密码强度
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return False, error_msg
            
        USERS[username]['password'] = encrypt_password(password)
        USERS[username]['is_encrypted'] = True
    
    if name:
        USERS[username]['name'] = name
    
    if store is not None:  # 允许空字符串作为商店名
        USERS[username]['store'] = store
    
    if save_users(USERS):
        return True, "用户信息更新成功！"
    return False, "用户信息更新失败，无法保存数据！"

def delete_user(username):
    """删除用户"""
    if username not in USERS:
        return False, "用户不存在！"
    
    if username == 'admin':
        return False, "不能删除管理员账号！"
    
    del USERS[username]
    
    if save_users(USERS):
        return True, "用户删除成功！"
    return False, "用户删除失败，无法保存数据！" 