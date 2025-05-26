"""
用户个人信息管理相关路由
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app

from ...logic.auth import login_required
from ...utils.logger import get_logger

# 创建用户信息蓝图
user_profile_bp = Blueprint('user_profile', __name__)
logger = get_logger('user_profile')

@user_profile_bp.route('/profile')
@login_required
def user_profile():
    """用户个人资料页面"""
    return render_template('user_profile.html', 
                         username=session.get('user_id'), 
                         name=session.get('user_name', ''), 
                         store=session.get('user_store', ''))

@user_profile_bp.route('/update_profile', methods=['POST'])
@login_required
def update_user_profile():
    """更新用户个人资料"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # 验证密码
    if new_password and new_password != confirm_password:
        flash('两次输入的密码不一致，请重新输入！', 'error')
        return redirect(url_for('student.user_profile'))
    
    if not new_password:
        flash('请输入新密码以更新个人信息。', 'info')
        return redirect(url_for('student.user_profile'))
    
    try:
        from ...logic.users import update_user
        from ...logic.auth import UserRole
        
        # 校长权限限制：只能修改密码，不能修改其他信息
        if user_role == UserRole.PRINCIPAL:
            # 校长只能修改密码，其他信息保持不变
            success, message = update_user(
                user_id, 
                password=new_password,  # 只传递密码参数
                name=None,  # 不修改姓名
                store=None,  # 不修改训练中心
                role=None,  # 不修改权限
                operator_id=user_id
            )
        else:
            # 其他角色可以修改所有信息（如果需要的话）
            success, message = update_user(
                user_id, new_password, 
                session.get('user_name', ''), 
                session.get('user_store', ''),
                operator_id=user_id
            )
        
        flash('密码更新成功！' if success else f'更新失败: {message}', 
              'success' if success else 'error')
              
    except Exception as e:
        current_app.logger.error(f"更新用户信息时出错: {str(e)}")
        flash(f'更新失败: {str(e)}', 'error')
    
    return redirect(url_for('student.user_profile')) 