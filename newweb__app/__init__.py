#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask 应用工厂函数
使用新的配置系统和Winston风格日志系统
"""

from flask import Flask
import os
import logging

def create_app(config_object=None):
    """
    Flask 应用工厂函数
    
    Args:
        config_object: 配置对象，如果为 None 则使用新的配置系统
    
    Returns:
        Flask: 配置好的 Flask 应用实例
    """
    app = Flask(__name__, instance_relative_config=False)

    # 使用新的配置系统
    if config_object is None:
        # 导入新的配置系统
        from .config import get_app_config
        
        try:
            # 获取完整的应用配置
            config = get_app_config()
            
            # 将配置应用到 Flask 应用
            for key in dir(config):
                if not key.startswith('_'):  # 跳过私有属性
                    value = getattr(config, key)
                    if not callable(value):  # 跳过方法
                        app.config[key] = value
                        
            app.logger.info("✅ 使用新配置系统加载配置")
            
        except Exception as e:
            app.logger.error(f"❌ 配置加载失败: {e}")
            # 如果新配置系统失败，回退到旧的配置
            app.config.from_object('newweb__app.config')
            app.logger.warning("⚠️  回退到旧配置系统")
    else:
        # 使用传入的配置对象（向后兼容）
        app.config.from_object(config_object)
        app.logger.info(f"✅ 使用指定配置对象: {config_object}")

    # 🔥 配置Winston风格日志系统 - 新增
    setup_winston_logging(app)

    # 初始化用户数据 (在注册蓝图和导入路由之前，确保上下文可用)
    try:
        from .logic.auth import init_users_data
        init_users_data(app)  # 传递 app 实例
        app.logger.info("✅ 用户数据初始化完成")
    except Exception as e:
        app.logger.error(f"❌ 用户数据初始化失败: {e}")

    # 注册蓝图 - 使用新的模块化蓝图结构
    try:
        from .routes import register_blueprints
        register_blueprints(app)
        app.logger.info('✅ 所有蓝图注册完成')
    except Exception as e:
        app.logger.error(f"❌ 蓝图注册失败: {e}")
        # 如果新蓝图注册失败，尝试使用旧的方式作为备用
        try:
            from . import routes  # 导入 routes.py
            app.register_blueprint(routes.main_bp)
            app.logger.warning('⚠️  使用旧蓝图注册方式作为备用')
        except Exception as fallback_error:
            app.logger.error(f"❌ 备用蓝图注册也失败: {fallback_error}")

    # 🔥 注册请求日志中间件 - 新增
    register_request_logging(app)

    # 🔥 注册健康检查端点 - 新增
    register_health_check(app)

    @app.context_processor
    def inject_now():
        """注入当前时间到模板上下文"""
        from datetime import datetime
        return {'now': datetime.utcnow()}

    # 注册错误处理器
    register_error_handlers(app)

    app.logger.info('🚀 Flask 应用创建成功')
    return app


def setup_winston_logging(app):
    """
    设置Winston风格日志系统
    
    Args:
        app: Flask 应用实例
    """
    try:
        # 导入Winston日志模块
        from .utils.logger import setup_winston_logger
        
        # 设置Winston风格日志
        setup_winston_logger(app)
        
        app.logger.info("🎯 Winston风格日志系统配置完成")
        
    except Exception as e:
        # 如果Winston日志配置失败，回退到原有日志系统
        app.logger.warning(f"⚠️ Winston日志配置失败，使用传统日志: {e}")
        configure_logging_fallback(app)


def configure_logging_fallback(app):
    """
    备用日志配置（原有的日志系统）
    
    Args:
        app: Flask 应用实例
    """
    try:
        # 获取日志配置
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        log_file = app.config.get('LOG_FILE', './logs/app.log')
        data_folder = app.config.get('DATA_FOLDER', 'data')
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 备用日志文件路径（在数据目录中）
        fallback_log_file = os.path.join(data_folder, 'app.log')
        os.makedirs(os.path.dirname(fallback_log_file), exist_ok=True)
        
        # 配置日志格式
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # 创建日志处理器
        handlers = []
        
        # 文件处理器
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            handlers.append(file_handler)
        except Exception:
            # 如果主日志文件创建失败，使用备用路径
            file_handler = logging.FileHandler(fallback_log_file, encoding='utf-8')
            handlers.append(file_handler)
            app.logger.warning(f"主日志文件创建失败，使用备用路径: {fallback_log_file}")
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        handlers.append(console_handler)
        
        # 应用日志配置
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=handlers,
            force=True  # 强制重新配置日志
        )
        
        app.logger.info(f'✅ 备用日志系统配置完成 - 级别: {app.config.get("LOG_LEVEL", "INFO")}')
        app.logger.info(f'📁 日志文件路径: {log_file}')
        
    except Exception as e:
        # 如果日志配置失败，使用基本配置
        logging.basicConfig(level=logging.INFO)
        app.logger.error(f"❌ 日志配置失败，使用默认配置: {e}")


def register_request_logging(app):
    """
    注册请求日志中间件
    
    Args:
        app: Flask 应用实例
    """
    try:
        from .utils.logger import log_request_start, log_request_end
        
        @app.before_request
        def before_request():
            """请求开始时记录日志"""
            log_request_start()
            
        @app.after_request
        def after_request(response):
            """请求结束时记录日志"""
            log_request_end(response.status_code)
            return response
            
        app.logger.info("📝 请求日志中间件注册完成")
        
    except Exception as e:
        app.logger.warning(f"⚠️ 请求日志中间件注册失败: {e}")


def register_health_check(app):
    """
    注册健康检查端点
    
    Args:
        app: Flask 应用实例
    """
    try:
        from flask import jsonify
        from .utils.logger import health_check, get_log_stats
        
        @app.route('/health')
        def health():
            """健康检查端点"""
            return jsonify(health_check())
            
        @app.route('/health/logs')
        def log_stats():
            """日志统计端点"""
            return jsonify(get_log_stats())
            
        app.logger.info("🏥 健康检查端点注册完成")
        
    except Exception as e:
        app.logger.warning(f"⚠️ 健康检查端点注册失败: {e}")


def register_error_handlers(app):
    """
    注册全局错误处理器
    增强版本，支持更多错误类型和友好的错误页面
    
    Args:
        app: Flask 应用实例
    """
    try:
        from .utils.logger import get_logger
        from .utils.response import is_ajax_request, json_response, ERROR_CODES
        from flask import render_template, request
        
        # 获取错误日志记录器
        error_logger = get_logger('error')
        
        @app.errorhandler(400)
        def bad_request_error(error):
            """处理400错误 - 请求格式错误"""
            error_logger.warn(f"400 错误: {error}", extra_data={
                'error_type': '400',
                'path': request.path if request else 'unknown',
                'method': request.method if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "请求格式错误", error_code='VALIDATION_ERROR')
            
            try:
                return render_template('errors/400.html'), 400
            except:
                return "请求格式错误", 400

        @app.errorhandler(401)
        def unauthorized_error(error):
            """处理401错误 - 未授权"""
            error_logger.warn(f"401 错误: {error}", extra_data={
                'error_type': '401',
                'path': request.path if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "未授权访问", error_code='UNAUTHORIZED')
            
            try:
                return render_template('errors/401.html'), 401
            except:
                return "未授权访问", 401

        @app.errorhandler(403)
        def forbidden_error(error):
            """处理403错误 - 权限不足"""
            error_logger.warn(f"403 错误: {error}", extra_data={
                'error_type': '403',
                'path': request.path if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "权限不足", error_code='FORBIDDEN')
            
            try:
                return render_template('errors/403.html'), 403
            except:
                return "权限不足", 403

        @app.errorhandler(404)
        def not_found_error(error):
            """处理404错误 - 页面未找到"""
            error_logger.warn(f"404 错误: {error}", extra_data={
                'error_type': '404',
                'path': request.path if request else 'unknown',
                'referrer': request.referrer if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "资源未找到", error_code='NOT_FOUND')
            
            try:
                return render_template('errors/404.html'), 404
            except:
                return "页面未找到", 404

        @app.errorhandler(405)
        def method_not_allowed_error(error):
            """处理405错误 - 方法不允许"""
            error_logger.warn(f"405 错误: {error}", extra_data={
                'error_type': '405',
                'path': request.path if request else 'unknown',
                'method': request.method if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "请求方法不允许", error_code='METHOD_NOT_ALLOWED')
            
            try:
                return render_template('errors/405.html'), 405
            except:
                return "请求方法不允许", 405

        @app.errorhandler(413)
        def request_entity_too_large_error(error):
            """处理413错误 - 请求实体过大"""
            error_logger.warn(f"413 错误: {error}", extra_data={
                'error_type': '413',
                'path': request.path if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "上传文件过大", error_code='VALIDATION_ERROR')
            
            try:
                return render_template('errors/413.html'), 413
            except:
                return "上传文件过大", 413

        @app.errorhandler(500)
        def internal_error(error):
            """处理500错误 - 服务器内部错误"""
            error_logger.error(f"500 错误: {error}", error=error, extra_data={
                'error_type': '500',
                'path': request.path if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "服务器内部错误", error_code='INTERNAL_ERROR')
            
            try:
                return render_template('errors/500.html'), 500
            except:
                return "服务器内部错误", 500

        @app.errorhandler(Exception)
        def handle_exception(e):
            """处理未捕获的异常"""
            # 检查是否是HTTP异常
            if hasattr(e, 'code'):
                # 这是一个HTTP异常，让Flask处理
                return e
            
            error_logger.error(f"未捕获的异常: {e}", error=e, extra_data={
                'error_type': 'unhandled_exception',
                'exception_class': e.__class__.__name__,
                'path': request.path if request else 'unknown'
            })
            
            if is_ajax_request():
                return json_response(False, "服务器发生错误", error_code='INTERNAL_ERROR')
            
            try:
                return render_template('errors/500.html'), 500
            except:
                return "服务器发生错误", 500
        
        # 注册自定义异常处理器
        from .config import ConfigValidationError
        
        @app.errorhandler(ConfigValidationError)
        def handle_config_error(e):
            """处理配置验证错误"""
            error_logger.error(f"配置验证错误: {e}", extra_data={
                'error_type': 'config_validation_error'
            })
            
            if is_ajax_request():
                return json_response(False, "系统配置错误", error_code='INTERNAL_ERROR')
            
            try:
                return render_template('errors/config_error.html', error=str(e)), 500
            except:
                return f"系统配置错误: {str(e)}", 500
            
        app.logger.info("🛡️ 增强版错误处理器注册完成")
        
    except Exception as e:
        # 如果Winston日志不可用，使用原有错误处理
        app.logger.warning(f"⚠️ 增强版错误处理器注册失败，使用传统处理: {e}")
        
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 错误: {error}")
        return "页面未找到", 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 错误: {error}")
        return "服务器内部错误", 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"未捕获的异常: {e}", exc_info=True)
        return "服务器发生错误", 500


# 导出主要函数
__all__ = ['create_app'] 