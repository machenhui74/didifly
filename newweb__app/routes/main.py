"""
主要页面路由
处理首页、通用页面等核心功能
"""

from flask import Blueprint, render_template, session, current_app
from datetime import datetime

from ..logic.auth import login_required, assessor_required, teacher_required, get_user_role, UserRole

# 创建主页面蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/index')
@assessor_required
def index():
    """
    应用主页 - 测评数据输入页面
    """
    user_store = session.get('user_store', '')
    user_name = session.get('user_name', '')
    user_id = session.get('user_id', '')
    
    # 如果是管理员，设置默认值
    if user_id == 'admin':
        user_store = current_app.config.get('ADMIN_DEFAULT_STORE', '台州店') # 示例: 从配置获取
        user_name = current_app.config.get('ADMIN_DEFAULT_NAME', '马老师')  # 示例: 从配置获取
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', 
                         user_store=user_store, 
                         user_name=user_name, 
                         user_id=user_id, 
                         current_date=current_date)

@main_bp.route('/teacher_welcome')
@teacher_required
def teacher_welcome():
    """
    老师欢迎页面 - 显示可用功能
    """
    user_name = session.get('user_name', '')
    user_store = session.get('user_store', '')
    user_role = get_user_role()
    
    return render_template('teacher_welcome.html', 
                         user_name=user_name,
                         user_store=user_store,
                         user_role=user_role) 