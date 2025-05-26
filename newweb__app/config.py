#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用程序配置模块
提供环境检测、配置验证和安全配置管理
"""

import os
import sys
import secrets
import logging
from datetime import timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 配置日志
logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """配置验证错误异常"""
    pass


class BaseConfig:
    """基础配置类 - 包含所有环境通用的配置"""
    
    # 环境检测
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # 核心安全配置
    SECRET_KEY = None  # 将在子类中设置
    
    # Session 配置
    SESSION_TIMEOUT_HOURS = int(os.environ.get('SESSION_TIMEOUT_HOURS', '2'))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=SESSION_TIMEOUT_HOURS)
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', './logs/app.log')
    
    # 文件上传配置
    MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', '50'))  # MB
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE * 1024 * 1024  # 转换为字节
    
    # 学生档案配置
    MAX_STUDENT_PROFILES = int(os.environ.get('MAX_STUDENT_PROFILES', '100000'))
    
    # Web 服务器配置
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', '5000'))
    WORKERS = int(os.environ.get('WORKERS', '4'))


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    
    # 开发环境可以使用默认密钥，但会显示警告
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_please_change_in_production_newweb')
    DEBUG = True
    TESTING = False
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """验证开发环境配置"""
        warnings = []
        
        if cls.SECRET_KEY == 'dev_secret_key_please_change_in_production_newweb':
            warnings.append("⚠️  开发环境正在使用默认 SECRET_KEY，建议设置自定义密钥")
        
        return warnings


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    
    DEBUG = False
    TESTING = False
    
    @property
    def SECRET_KEY(self) -> str:
        """生产环境必须设置自定义 SECRET_KEY"""
        secret_key = os.environ.get('SECRET_KEY')
        
        if not secret_key or secret_key == 'dev_secret_key_please_change_in_production_newweb':
            raise ConfigValidationError(
                "🚨 生产环境必须设置自定义 SECRET_KEY！\n"
                "请在环境变量中设置 SECRET_KEY，可以使用以下命令生成：\n"
                "python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        if len(secret_key) < 32:
            raise ConfigValidationError(
                "🚨 SECRET_KEY 长度不足！生产环境建议使用至少32位的强随机字符串"
            )
        
        return secret_key
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """验证生产环境配置"""
        errors = []
        
        # 验证 SECRET_KEY
        try:
            _ = cls().SECRET_KEY
        except ConfigValidationError as e:
            errors.append(str(e))
        
        return errors


class TestingConfig(BaseConfig):
    """测试环境配置"""
    
    SECRET_KEY = 'testing_secret_key_not_for_production'
    DEBUG = True
    TESTING = True
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """验证测试环境配置"""
        return []  # 测试环境无特殊验证要求


def get_config_class():
    """根据环境变量获取配置类"""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    config_mapping = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_mapping.get(env)
    if not config_class:
        logger.warning(f"未知的 FLASK_ENV: {env}，使用开发环境配置")
        return DevelopmentConfig
    
    return config_class


def get_path_config() -> Dict[str, str]:
    """获取路径配置 - 移除硬编码路径，全部从环境变量读取"""
    
    # 获取应用根目录
    app_root = Path(__file__).parent.absolute()
    
    # 默认路径配置（使用相对路径，避免硬编码）
    default_paths = {
        'DATA_FOLDER': str(app_root / 'data'),
        'SOURCE_FOLDER': str(app_root / 'data' / 'source_materials'),
        'DESTINATION_FOLDER': str(app_root / 'data' / 'student_training_plans'),
        'REPORT_TEMPLATE_PATH': str(app_root / 'data' / 'templates' / 'test_report_template.docx'),
        'REPORT_OUTPUT_FOLDER': str(app_root / 'data' / 'reports'),
        'TRAINING_ACTION_DB_PATH': str(app_root / 'data' / 'action_database.xlsx'),
        'TRAINING_PLAN_OUTPUT_FOLDER': str(app_root / 'data' / 'training_plans'),
    }
    
    # 从环境变量获取路径配置，如果未设置则使用默认值
    path_config = {}
    for key, default_value in default_paths.items():
        path_config[key] = os.environ.get(key, default_value)
    
    return path_config


def create_required_directories(path_config: Dict[str, str]) -> None:
    """创建必需的目录"""
    
    # 获取 LOG_FILE 路径
    log_file = os.environ.get('LOG_FILE', './logs/app.log')
    
    directories_to_create = [
        path_config['DATA_FOLDER'],
        path_config['DESTINATION_FOLDER'],
        path_config['REPORT_OUTPUT_FOLDER'],
        path_config['TRAINING_PLAN_OUTPUT_FOLDER'],
        os.path.dirname(log_file) if os.path.dirname(log_file) else None
    ]
    
    # 创建目录
    for directory in directories_to_create:
        if directory:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"✅ 确保目录存在: {directory}")
            except Exception as e:
                logger.error(f"❌ 创建目录失败 {directory}: {e}")


def get_file_paths(data_folder: str) -> Dict[str, str]:
    """获取文件路径配置"""
    return {
        'USERS_FILE': os.path.join(data_folder, 'users.json'),
        'STUDENT_PROFILES_FILE': os.path.join(data_folder, 'student_profiles.json'),
        'PERMISSION_LOGS_FILE': os.path.join(data_folder, 'permission_logs.json'),
    }


def validate_all_config() -> None:
    """验证所有配置并显示警告/错误"""
    
    config_class = get_config_class()
    
    # 验证配置
    validation_results = config_class.validate_config()
    
    if validation_results:
        for result in validation_results:
            if "🚨" in result:  # 错误
                logger.error(result)
                print(f"配置错误: {result}", file=sys.stderr)
            else:  # 警告
                logger.warning(result)
                print(f"配置警告: {result}")
    
    # 验证路径配置
    path_config = get_path_config()
    
    # 检查关键文件是否存在
    critical_files = ['REPORT_TEMPLATE_PATH', 'TRAINING_ACTION_DB_PATH']
    for file_key in critical_files:
        file_path = path_config.get(file_key)
        if file_path and not os.path.exists(file_path):
            logger.warning(f"⚠️  关键文件不存在: {file_key} = {file_path}")
    
    # 验证关键目录是否可写
    critical_dirs = [
        ('DATA_FOLDER', '数据目录'),
        ('DESTINATION_FOLDER', '学员训练方案输出目录'),
        ('REPORT_OUTPUT_FOLDER', '测评报告输出目录'),
        ('TRAINING_PLAN_OUTPUT_FOLDER', '训练方案输出目录')
    ]
    
    for dir_key, dir_desc in critical_dirs:
        dir_path = path_config.get(dir_key)
        if dir_path:
            if not os.path.exists(dir_path):
                logger.info(f"📁 将创建{dir_desc}: {dir_path}")
            elif not os.access(dir_path, os.W_OK):
                logger.warning(f"⚠️  {dir_desc}不可写: {dir_path}")
    
    # 验证环境变量设置
    validate_environment_variables()


def validate_environment_variables() -> None:
    """验证环境变量设置"""
    
    # 检查重要的环境变量是否设置
    important_env_vars = {
        'FLASK_ENV': '运行环境设置',
        'SECRET_KEY': '应用安全密钥',
        'DATA_FOLDER': '数据存储目录',
        'LOG_LEVEL': '日志级别'
    }
    
    for env_var, description in important_env_vars.items():
        value = os.environ.get(env_var)
        if not value:
            logger.info(f"📝 环境变量未设置，使用默认值: {env_var} ({description})")
        else:
            logger.debug(f"✅ 环境变量已设置: {env_var}")
    
    # 检查路径相关的环境变量
    path_env_vars = [
        'DATA_FOLDER', 'SOURCE_FOLDER', 'DESTINATION_FOLDER',
        'REPORT_TEMPLATE_PATH', 'REPORT_OUTPUT_FOLDER',
        'TRAINING_ACTION_DB_PATH', 'TRAINING_PLAN_OUTPUT_FOLDER'
    ]
    
    custom_paths_count = 0
    for env_var in path_env_vars:
        if os.environ.get(env_var):
            custom_paths_count += 1
    
    if custom_paths_count == 0:
        logger.info("📝 所有路径配置均使用默认值（相对路径）")
    else:
        logger.info(f"📝 {custom_paths_count}/{len(path_env_vars)} 个路径配置使用了自定义环境变量")


def get_environment_summary() -> Dict[str, Any]:
    """获取环境配置摘要"""
    
    config_class = get_config_class()
    path_config = get_path_config()
    
    return {
        'environment': os.environ.get('FLASK_ENV', 'development'),
        'debug_mode': config_class == DevelopmentConfig,
        'custom_secret_key': os.environ.get('SECRET_KEY') is not None,
        'custom_paths_count': len([k for k in path_config.keys() if os.environ.get(k)]),
        'total_paths': len(path_config),
        'log_level': os.environ.get('LOG_LEVEL', 'INFO'),
        'data_folder': path_config.get('DATA_FOLDER'),
        'config_validation_passed': len(config_class.validate_config()) == 0
    }


def get_app_config():
    """获取完整的应用配置"""
    
    # 获取配置类
    config_class = get_config_class()
    config = config_class()
    
    # 获取路径配置
    path_config = get_path_config()
    
    # 获取文件路径
    file_paths = get_file_paths(path_config['DATA_FOLDER'])
    
    # 合并所有配置
    for key, value in path_config.items():
        setattr(config, key, value)
    
    for key, value in file_paths.items():
        setattr(config, key, value)
    
    # 创建必需目录
    create_required_directories(path_config)
    
    # 验证配置
    validate_all_config()
    
    logger.info(f"✅ 配置加载完成 - 环境: {config.FLASK_ENV}")
    
    return config


# 导出配置验证函数供外部使用
__all__ = [
    'get_app_config',
    'validate_all_config',
    'validate_environment_variables',
    'get_environment_summary',
    'get_path_config',
    'create_required_directories',
    'ConfigValidationError',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestingConfig'
] 