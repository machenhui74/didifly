#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Winston风格日志模块
提供结构化日志记录、日志轮转、性能监控和业务流程追踪功能
"""

import os
import sys
import logging
import logging.handlers
import json
import time
import traceback
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional, Union
from flask import current_app, request, session, g

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# Winston风格的日志级别
WINSTON_LEVELS = {
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'info': logging.INFO,
    'verbose': logging.DEBUG,
    'debug': logging.DEBUG,
    'silly': logging.DEBUG
}

class WinstonFormatter(logging.Formatter):
    """Winston风格的日志格式化器"""
    
    def __init__(self):
        super().__init__()
        
    def format(self, record):
        """格式化日志记录为Winston风格的JSON格式"""
        
        # 基础日志信息
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname.lower(),
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # 添加请求上下文信息（如果在Flask应用上下文中）
        try:
            if current_app:
                log_entry['app'] = current_app.name
                
                # 添加请求信息
                if request:
                    log_entry['request'] = {
                        'method': request.method,
                        'url': request.url,
                        'remote_addr': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent', '')[:100]  # 限制长度
                    }
                    
                # 添加用户信息
                if session and 'user_id' in session:
                    log_entry['user'] = {
                        'user_id': session.get('user_id'),
                        'user_name': session.get('user_name', ''),
                        'user_store': session.get('user_store', '')
                    }
                    
        except RuntimeError:
            # 不在应用上下文中，跳过Flask相关信息
            pass
            
        # 添加异常信息
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # 添加自定义字段
        if hasattr(record, 'extra_data'):
            log_entry['data'] = record.extra_data
            
        # 添加性能信息
        if hasattr(record, 'duration'):
            log_entry['performance'] = {
                'duration_ms': record.duration,
                'memory_usage': getattr(record, 'memory_usage', None)
            }
            
        # 添加业务流程信息
        if hasattr(record, 'business_flow'):
            log_entry['business'] = record.business_flow
            
        return json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))

class WinstonLogger:
    """Winston风格的日志记录器"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        初始化Winston风格日志记录器
        
        Args:
            name: 日志记录器名称
            config: 日志配置字典
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.config = config or {}
        
        # 防止重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()
            
    def _setup_handlers(self):
        """设置日志处理器"""
        
        # 获取配置
        log_level = self.config.get('level', 'INFO')
        log_file = self.config.get('file', './logs/app.log')
        max_bytes = self.config.get('max_bytes', 10 * 1024 * 1024)  # 10MB
        backup_count = self.config.get('backup_count', 5)
        enable_console = self.config.get('console', True)
        
        # 设置日志级别
        self.logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
        
        # 创建格式化器
        formatter = WinstonFormatter()
        
        # 文件处理器（带轮转）
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
                
            # 确保使用绝对路径，避免轮转时路径错误
            abs_log_file = os.path.abspath(log_file)
            
            file_handler = logging.handlers.RotatingFileHandler(
                abs_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"创建文件日志处理器失败: {e}")
            
        # 控制台处理器
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
        # 防止日志传播到根记录器
        self.logger.propagate = False
        
    def _log(self, level: str, message: str, extra_data: Optional[Dict] = None, **kwargs):
        """内部日志记录方法"""
        
        # 创建日志记录
        record_kwargs = {}
        
        if extra_data:
            record_kwargs['extra'] = {'extra_data': extra_data}
            
        # 添加其他自定义字段
        for key, value in kwargs.items():
            if hasattr(logging.LogRecord, key):
                continue  # 跳过内置字段
            record_kwargs.setdefault('extra', {})[key] = value
            
        # 记录日志
        log_method = getattr(self.logger, level.lower())
        log_method(message, **record_kwargs)
        
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """记录错误日志"""
        if error:
            kwargs['exc_info'] = (type(error), error, error.__traceback__)
        self._log('error', message, **kwargs)
        
    def warn(self, message: str, **kwargs):
        """记录警告日志"""
        self._log('warning', message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """记录警告日志（别名）"""
        self.warn(message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self._log('info', message, **kwargs)
        
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self._log('debug', message, **kwargs)
        
    def verbose(self, message: str, **kwargs):
        """记录详细日志"""
        self._log('debug', message, **kwargs)

# 全局日志记录器实例
_loggers: Dict[str, WinstonLogger] = {}

def get_logger(name: str = None, config: Optional[Dict] = None) -> WinstonLogger:
    """
    获取Winston风格的日志记录器
    
    Args:
        name: 日志记录器名称，默认使用调用模块名
        config: 日志配置
        
    Returns:
        WinstonLogger: Winston风格的日志记录器实例
    """
    
    if name is None:
        # 自动获取调用模块名
        frame = sys._getframe(1)
        name = frame.f_globals.get('__name__', 'unknown')
        
    # 使用单例模式
    if name not in _loggers:
        # 获取应用配置
        app_config = {}
        try:
            if current_app:
                app_config = {
                    'level': current_app.config.get('LOG_LEVEL', 'INFO'),
                    'file': current_app.config.get('LOG_FILE', './logs/app.log'),
                    'max_bytes': current_app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024),
                    'backup_count': current_app.config.get('LOG_BACKUP_COUNT', 5),
                    'console': current_app.config.get('LOG_CONSOLE', True)
                }
        except RuntimeError:
            # 不在应用上下文中，使用默认配置
            pass
            
        # 合并配置
        final_config = {**app_config, **(config or {})}
        _loggers[name] = WinstonLogger(name, final_config)
        
    return _loggers[name]

def setup_winston_logger(app):
    """
    为Flask应用设置Winston风格日志系统
    
    Args:
        app: Flask应用实例
    """
    
    # 获取应用日志记录器
    app_logger = get_logger('app')
    
    # 替换Flask默认日志记录器
    app.logger.handlers.clear()
    for handler in app_logger.logger.handlers:
        app.logger.addHandler(handler)
        
    app.logger.setLevel(app_logger.logger.level)
    
    # 记录启动信息
    app_logger.info("🚀 Winston风格日志系统已启动", extra_data={
        'app_name': app.name,
        'debug_mode': app.debug,
        'config_loaded': True
    })

def log_performance(func_name: str = None):
    """
    性能监控装饰器
    
    Args:
        func_name: 函数名称，用于日志记录
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = get_logger()
            
            actual_func_name = func_name or f"{func.__module__}.{func.__name__}"
            
            try:
                # 记录开始
                logger.debug(f"⏱️ 开始执行: {actual_func_name}")
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                duration = (time.time() - start_time) * 1000  # 转换为毫秒
                
                # 记录性能日志
                logger.info(f"✅ 执行完成: {actual_func_name}", 
                          duration=duration,
                          extra_data={'function': actual_func_name, 'success': True})
                
                return result
                
            except Exception as e:
                # 计算执行时间
                duration = (time.time() - start_time) * 1000
                
                # 记录错误和性能
                logger.error(f"❌ 执行失败: {actual_func_name}", 
                           error=e,
                           duration=duration,
                           extra_data={'function': actual_func_name, 'success': False})
                raise
                
        return wrapper
    return decorator

def log_business_flow(flow_name: str, step: str = None):
    """
    业务流程日志装饰器
    
    Args:
        flow_name: 业务流程名称
        step: 流程步骤名称
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            
            step_name = step or func.__name__
            
            # 业务流程信息
            business_info = {
                'flow': flow_name,
                'step': step_name,
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                # 记录流程开始
                logger.info(f"🔄 业务流程开始: {flow_name} -> {step_name}", 
                          business_flow=business_info)
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录流程成功
                business_info['status'] = 'success'
                logger.info(f"✅ 业务流程成功: {flow_name} -> {step_name}", 
                          business_flow=business_info)
                
                return result
                
            except Exception as e:
                # 记录流程失败
                business_info['status'] = 'failed'
                business_info['error'] = str(e)
                logger.error(f"❌ 业务流程失败: {flow_name} -> {step_name}", 
                           error=e,
                           business_flow=business_info)
                raise
                
        return wrapper
    return decorator

# 便捷函数
def log_request_start():
    """记录请求开始"""
    logger = get_logger('request')
    try:
        if request:
            logger.info(f"📥 请求开始: {request.method} {request.path}", extra_data={
                'request_id': getattr(g, 'request_id', None),
                'user_id': session.get('user_id'),
                'ip': request.remote_addr
            })
    except RuntimeError:
        pass

def log_request_end(status_code: int = None):
    """记录请求结束"""
    logger = get_logger('request')
    try:
        if request:
            logger.info(f"📤 请求结束: {request.method} {request.path}", extra_data={
                'request_id': getattr(g, 'request_id', None),
                'status_code': status_code,
                'user_id': session.get('user_id')
            })
    except RuntimeError:
        pass

def log_user_action(action: str, details: Dict[str, Any] = None):
    """记录用户操作"""
    logger = get_logger('user_action')
    
    action_data = {
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'details': details or {}
    }
    
    try:
        if session and 'user_id' in session:
            action_data['user'] = {
                'user_id': session.get('user_id'),
                'user_name': session.get('user_name'),
                'user_store': session.get('user_store')
            }
    except RuntimeError:
        pass
        
    logger.info(f"👤 用户操作: {action}", extra_data=action_data)

# 健康检查和监控
def get_log_stats() -> Dict[str, Any]:
    """获取日志统计信息"""
    stats = {
        'loggers_count': len(_loggers),
        'active_loggers': list(_loggers.keys()),
        'timestamp': datetime.now().isoformat()
    }
    
    return stats

def health_check() -> Dict[str, Any]:
    """日志系统健康检查"""
    try:
        # 测试日志记录
        test_logger = get_logger('health_check')
        test_logger.debug("健康检查测试日志")
        
        return {
            'status': 'healthy',
            'message': '日志系统运行正常',
            'stats': get_log_stats()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'message': f'日志系统异常: {str(e)}',
            'error': str(e)
        } 