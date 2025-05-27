# newweb__app/routes/auth.py
"""
认证相关路由
处理用户登录、登出和会话管理
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask_wtf import FlaskForm

from ..logic.auth import login_user as auth_login_user, UserRole

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    """
    首页路由 - 根据用户登录状态和权限重定向
    """
    if 'user_id' in session:
        user_role = session.get('user_role', 'assessor')
        # 根据用户权限重定向到不同页面
        if user_role == UserRole.TEACHER:
            return redirect(url_for('main.teacher_welcome'))
        else:
            return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录页面
    GET: 显示登录表单
    POST: 处理登录请求
    """
    form = LoginForm()
    if 'user_id' in session:
        user_role = session.get('user_role', 'assessor')
        if user_role == UserRole.TEACHER:
            return redirect(url_for('main.teacher_welcome'))
        else:
            return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data, success = auth_login_user(username, password) 
        
        if success:
            session['user_id'] = username
            session['user_name'] = user_data['name']
            session['user_store'] = user_data.get('store', '')
            session['user_role'] = user_data.get('role', 'assessor')
            session.permanent = True
            flash(f'欢迎回来，{user_data["name"]}！', 'success')
            
            # 根据用户权限重定向到不同页面
            user_role = user_data.get('role', 'assessor')
            if user_role == UserRole.TEACHER:
                return redirect(url_for('main.teacher_welcome'))
            else:
                return redirect(url_for('main.index'))
        
        flash('账号或密码错误！', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    """
    用户登出
    """
    user_name = session.get('user_name', '用户')
    session.clear()
    flash(f'再见，{user_name}！', 'info')
    return redirect(url_for('auth.login')) 

# 定义一个简单的登录表单类
class LoginForm(FlaskForm):
    pass 