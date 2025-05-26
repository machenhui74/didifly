"""
管理员功能路由
处理用户管理、权限控制等管理员专用功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session

from ..logic.auth import admin_required, principal_required, role_required, USERS, get_permission_logs, get_user_permission_logs, UserRole, ROLE_NAMES, get_user_role
from ..logic.users import (add_user as add_user_func, update_user, delete_user as delete_user_func, 
                          update_user_role, get_available_roles, filter_manageable_users)

# 创建管理员蓝图
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@role_required(UserRole.PRINCIPAL)  # 校长及以上权限可访问
def admin():
    """
    管理员主页 - 用户管理界面
    """
    current_user_id = session.get('user_id')
    current_user_role = get_user_role(current_user_id)
    
    # 根据用户权限过滤可管理的用户
    manageable_users = filter_manageable_users(current_user_id)
    
    # 获取用户列表，包含权限信息
    users_with_roles = {}
    for username, user_data in manageable_users.items():
        users_with_roles[username] = user_data.copy()
        users_with_roles[username]['role_name'] = ROLE_NAMES.get(user_data.get('role', 'assessor'), '未知')
    
    # 获取可用权限角色（根据当前用户权限过滤）
    available_roles = get_available_roles(current_user_role)
    
    # 获取最近的权限变更日志
    recent_logs = get_permission_logs(limit=20)
    
    return render_template('admin.html', 
                         users=users_with_roles, 
                         available_roles=available_roles,
                         permission_logs=recent_logs,
                         current_user_id=current_user_id,
                         current_user_role=current_user_role)

@admin_bp.route('/add_user', methods=['POST'])
@role_required(UserRole.PRINCIPAL)  # 校长及以上权限可访问
def add_user():
    """
    添加新用户
    支持AJAX和表单提交两种方式
    """
    new_username = request.form.get('new_username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    new_name = request.form.get('new_name', '').strip()
    new_store = request.form.get('new_store', '').strip()
    new_role = request.form.get('new_role', 'assessor').strip()  # 默认为测评师
    
    if not new_username or not new_password or not new_name:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
            response = jsonify({'success': False, 'message': '所有字段都是必填的！', 'reset_form': False})
            response.status_code = 400  # 明确返回400状态码表示请求有问题
            return response
        flash('所有字段都是必填的！', 'error')
        return redirect(url_for('admin.admin'))
    
    # 传递操作者ID用于权限检查和创建限制
    operator_id = session.get('user_id')
    success, message = add_user_func(new_username, new_password, new_name, new_store, new_role, operator_id)
    
    # 如果是AJAX请求或请求期望JSON响应，返回JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
        # 添加reset_form字段，帮助前端判断是否需要重置表单状态
        if not success and "密码" in message:
            # 密码不符合要求的错误，保留用户输入的其他字段
            response = jsonify({'success': False, 'message': message, 'reset_form': False})
            response.status_code = 400
            return response
        response = jsonify({'success': success, 'message': message, 'reset_form': success})
        response.status_code = 200 if success else 400  # 成功返回200，失败返回400
        return response
    
    # 否则使用传统的表单提交响应
    flash(message, 'success' if success else 'error')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/edit_user', methods=['POST'])
@role_required(UserRole.PRINCIPAL)  # 校长及以上权限可访问
def edit_user():
    """
    编辑用户信息
    支持AJAX和表单提交两种方式
    """
    username = request.form.get('username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    new_name = request.form.get('new_name', '').strip()
    new_store = request.form.get('new_store', '').strip()
    
    if not username or not new_name:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
            return jsonify({'success': False, 'message': '账号和用户名是必填的！', 'reset_form': False})
        flash('账号和用户名是必填的！', 'error')
        return redirect(url_for('admin.admin'))
    
    # 传递操作者ID用于权限检查和日志记录
    operator_id = session.get('user_id')
    success, message = update_user(username, new_password, new_name, new_store, operator_id=operator_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
        if not success and "密码" in message:
            return jsonify({'success': False, 'message': message, 'reset_form': False})
        return jsonify({'success': success, 'message': message, 'reset_form': success})
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/update_user_role', methods=['POST'])
@role_required(UserRole.PRINCIPAL)  # 校长及以上权限可访问
def update_role():
    """
    更新用户权限
    """
    username = request.form.get('username', '').strip()
    new_role = request.form.get('new_role', '').strip()
    
    if not username or not new_role:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': '用户名和权限角色是必填的！'})
        flash('用户名和权限角色是必填的！', 'error')
        return redirect(url_for('admin.admin'))
    
    # 获取操作者ID
    operator_id = session.get('user_id')
    
    success, message = update_user_role(username, new_role, operator_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success, 'message': message})
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/permission_logs')
@role_required(UserRole.PRINCIPAL)  # 校长及以上权限可访问
def permission_logs():
    """
    查看权限变更日志
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    user_filter = request.args.get('user', '').strip()
    
    if user_filter:
        # 查看特定用户的权限变更日志
        logs = get_user_permission_logs(user_filter, limit=limit * page)
        title = f"用户 {user_filter} 的权限变更日志"
    else:
        # 查看所有权限变更日志
        logs = get_permission_logs(limit=limit * page)
        title = "权限变更日志"
    
    # 简单分页处理
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_logs = logs[start_index:end_index]
    
    has_next = len(logs) > end_index
    has_prev = page > 1
    
    return render_template('permission_logs.html',
                         logs=paginated_logs,
                         title=title,
                         page=page,
                         has_next=has_next,
                         has_prev=has_prev,
                         user_filter=user_filter)

@admin_bp.route('/delete_user', methods=['POST'])
@role_required(UserRole.PRINCIPAL)  # 校长及以上权限可访问
def delete_user():
    """
    删除用户
    """
    username = request.form.get('username', '').strip()
    
    if not username:
        flash('账号是必填的！', 'error')
        return redirect(url_for('admin.admin'))
    
    # 使用导入的 delete_user_func
    success, message = delete_user_func(username) 
    flash(message, 'success' if success else 'error')
    
    return redirect(url_for('admin.admin')) 