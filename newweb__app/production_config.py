#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生产环境专用配置
解决云服务器部署问题
"""

import os
import sys
import secrets
from datetime import timedelta

class ProductionConfig:
    """生产环境配置类"""
    
    # 基础配置
    DEBUG = False
    TESTING = False
    
    # 安全配置 - 生成固定的SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY', 'prod_fixed_key_' + secrets.token_hex(32))
    
    # 会话配置 - 延长会话时间
    SESSION_TIMEOUT_HOURS = int(os.environ.get('SESSION_TIMEOUT_HOURS', '24'))  # 24小时
    PERMANENT_SESSION_LIFETIME = timedelta(hours=SESSION_TIMEOUT_HOURS)
    SESSION_COOKIE_SECURE = False  # 如果使用HTTPS，设置为True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 日志配置 - 简化日志避免编码问题
    LOG_LEVEL = 'WARNING'  # 减少日志输出
    LOG_FILE = './logs/production.log'
    
    # 文件路径配置
    DATA_FOLDER = './data'
    SOURCE_FOLDER = './data/source_materials'
    DESTINATION_FOLDER = './data/student_training_plans'
    REPORT_TEMPLATE_PATH = './data/templates/test_report_template.docx'
    REPORT_OUTPUT_FOLDER = './data/reports'
    TRAINING_ACTION_DB_PATH = './data/action_database.xlsx'
    TRAINING_PLAN_OUTPUT_FOLDER = './data/training_plans'
    
    # 文件路径
    USERS_FILE = './data/users.json'
    STUDENT_PROFILES_FILE = './data/student_profiles.json'
    PERMISSION_LOGS_FILE = './data/permission_logs.json'
    
    # 上传配置
    MAX_UPLOAD_SIZE = 50
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    
    # 学生档案配置
    MAX_STUDENT_PROFILES = 100000
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 8080
    WORKERS = 4

def get_production_config():
    """获取生产环境配置"""
    return ProductionConfig() 