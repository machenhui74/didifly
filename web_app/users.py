from auth import USERS, save_users, encrypt_password

def add_user(username, password, name, store):
    """添加新用户"""
    if username in USERS:
        return False, "账号已存在！"
    
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