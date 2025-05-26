# newweb__app/routes/__init__.py
"""
路由蓝图包
将原有的大型routes.py文件拆分为多个功能模块，提高代码的可维护性
"""

from .auth import auth_bp
from .admin import admin_bp  
from .student import student_bp
from .api import api_bp
from .main import main_bp

def register_blueprints(app):
    """
    注册所有蓝图到Flask应用
    
    Args:
        app: Flask应用实例
    """
    # 注册各个功能蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    
    # 记录蓝图注册完成
    app.logger.info("✅ 所有蓝图注册完成") 