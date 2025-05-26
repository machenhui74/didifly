#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生产环境应用入口
简化配置，避免部署问题
"""

import os
import sys
import logging
from flask import Flask

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def create_production_app():
    """创建生产环境Flask应用"""
    
    # 创建Flask应用
    app = Flask(__name__)
    
    # 导入生产环境配置
    from production_config import get_production_config
    config = get_production_config()
    
    # 应用配置
    for key in dir(config):
        if not key.startswith('_') and not callable(getattr(config, key)):
            app.config[key] = getattr(config, key)
    
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'production'
    
    # 简化日志配置
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('./logs/production.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 确保必要目录存在
    os.makedirs('./data', exist_ok=True)
    os.makedirs('./logs', exist_ok=True)
    
    try:
        # 初始化用户数据
        from newweb__app.logic.auth import init_users_data
        with app.app_context():
            init_users_data(app)
        app.logger.info("✅ 用户数据初始化完成")
    except Exception as e:
        app.logger.error(f"❌ 用户数据初始化失败: {e}")
        # 创建基本用户数据
        import json
        import hashlib
        
        users_file = './data/users.json'
        if not os.path.exists(users_file):
            default_users = {
                'admin': {
                    'password': hashlib.sha256('admin123'.encode('utf-8')).hexdigest(),
                    'name': '管理员',
                    'store': '总部',
                    'role': 'admin',
                    'is_encrypted': True
                }
            }
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump(default_users, f, ensure_ascii=False, indent=4)
    
    try:
        # 注册蓝图 - 使用简化方式
        from newweb__app.routes_original import main_bp
        app.register_blueprint(main_bp)
        app.logger.info("✅ 蓝图注册完成")
    except Exception as e:
        app.logger.error(f"❌ 蓝图注册失败: {e}")
        return None
    
    # 添加基本错误处理
    @app.errorhandler(404)
    def not_found(error):
        return "页面未找到", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return "服务器内部错误", 500
    
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': '应用运行正常'}
    
    app.logger.info("🚀 生产环境应用创建成功")
    return app

# 创建应用实例
app = create_production_app()

if __name__ == '__main__':
    if app:
        print("==============================================")
        print("生产环境应用启动中...")
        print("访问地址：http://your-server-ip:8080")
        print("==============================================")
        app.run(host='0.0.0.0', port=8080, debug=False)
    else:
        print("❌ 应用创建失败")
        sys.exit(1) 