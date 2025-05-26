#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具模块包
提供日志记录、响应格式化、数据验证等通用功能
"""

__version__ = '1.0.0'
__author__ = 'newweb__app team'

# 导入主要工具模块
from .logger import (
    get_logger,
    log_performance,
    log_business_flow,
    log_user_action,
    log_request_start,
    log_request_end,
    health_check,
    get_log_stats,
    setup_winston_logger
)

# 导入响应格式化模块
from .response import (
    success_response,
    error_response,
    api_response,
    json_response,
    is_ajax_request,
    validate_and_respond,
    ERROR_CODES,
    ERROR_MESSAGES
)

# 导入数据验证模块
from .validators import (
    # 基础验证函数
    is_not_empty,
    is_valid_date,
    is_valid_age,
    is_valid_number,
    is_valid_password,
    
    # 业务验证函数
    validate_student_basic_info,
    validate_assessment_data,
    validate_direct_plan_data,
    validate_user_data,
    validate_training_plan_data,
    
    # 预定义验证器
    validate_student_submission,
    validate_direct_plan_submission,
    validate_user_addition,
    validate_user_edit,
    validate_training_plan_submission,
    
    # 验证装饰器工厂
    create_validator
)

__all__ = [
    # 日志功能
    'get_logger',
    'log_performance', 
    'log_business_flow',
    'log_user_action',
    'log_request_start',
    'log_request_end',
    'health_check',
    'get_log_stats',
    'setup_winston_logger',
    
    # 响应功能
    'success_response',
    'error_response',
    'api_response',
    'json_response',
    'is_ajax_request',
    'validate_and_respond',
    'ERROR_CODES',
    'ERROR_MESSAGES',
    
    # 验证功能
    'is_not_empty',
    'is_valid_date',
    'is_valid_age',
    'is_valid_number',
    'is_valid_password',
    'validate_student_basic_info',
    'validate_assessment_data',
    'validate_direct_plan_data',
    'validate_user_data',
    'validate_training_plan_data',
    'validate_student_submission',
    'validate_direct_plan_submission',
    'validate_user_addition',
    'validate_user_edit',
    'validate_training_plan_submission',
    'create_validator'
] 