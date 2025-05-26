#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一API响应格式模块
基于现有jsonify模式，提供标准化的响应格式和错误处理
"""

from flask import jsonify, request
from typing import Dict, Any, Optional, Union
from .logger import get_logger

logger = get_logger('response')

# 错误码映射表
ERROR_CODES = {
    # 通用错误
    'VALIDATION_ERROR': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'METHOD_NOT_ALLOWED': 405,
    'INTERNAL_ERROR': 500,
    
    # 业务错误
    'MISSING_REQUIRED_FIELDS': 400,
    'INVALID_DATE_FORMAT': 400,
    'INVALID_AGE_RANGE': 400,
    'INVALID_ASSESSMENT_DATA': 400,
    'FILE_NOT_FOUND': 404,
    'GENERATION_FAILED': 500,
    'DATABASE_ERROR': 500,
}

# 错误消息映射
ERROR_MESSAGES = {
    'VALIDATION_ERROR': '数据验证失败',
    'UNAUTHORIZED': '未授权访问',
    'FORBIDDEN': '权限不足',
    'NOT_FOUND': '资源未找到',
    'METHOD_NOT_ALLOWED': '请求方法不允许',
    'INTERNAL_ERROR': '服务器内部错误',
    
    'MISSING_REQUIRED_FIELDS': '请填写所有必填字段',
    'INVALID_DATE_FORMAT': '日期格式无效',
    'INVALID_AGE_RANGE': '年龄必须在4-12岁之间',
    'INVALID_ASSESSMENT_DATA': '测评数据格式无效',
    'FILE_NOT_FOUND': '文件未找到',
    'GENERATION_FAILED': '生成失败',
    'DATABASE_ERROR': '数据库操作失败',
}

def is_ajax_request() -> bool:
    """
    检查是否为AJAX请求
    基于现有的检查逻辑
    """
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        (request.content_type and 'json' in request.content_type)
    )

def success_response(
    message: str = '操作成功',
    data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    创建成功响应
    
    Args:
        message: 成功消息
        data: 响应数据
        **kwargs: 其他响应字段
        
    Returns:
        Dict: 标准化的成功响应
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
        
    # 添加其他字段（保持向后兼容）
    response.update(kwargs)
    
    logger.debug("✅ 成功响应", extra_data={
        'message': message,
        'has_data': data is not None,
        'extra_fields': list(kwargs.keys())
    })
    
    return response

def error_response(
    error_code: str = 'INTERNAL_ERROR',
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> tuple:
    """
    创建错误响应
    
    Args:
        error_code: 错误代码
        message: 自定义错误消息
        details: 错误详情
        **kwargs: 其他响应字段
        
    Returns:
        tuple: (响应字典, HTTP状态码)
    """
    # 获取HTTP状态码
    status_code = ERROR_CODES.get(error_code, 500)
    
    # 获取错误消息
    if message is None:
        message = ERROR_MESSAGES.get(error_code, '未知错误')
    
    response = {
        'success': False,
        'error_code': error_code,
        'message': message
    }
    
    if details:
        response['details'] = details
        
    # 添加其他字段（保持向后兼容）
    response.update(kwargs)
    
    logger.warn("❌ 错误响应", extra_data={
        'error_code': error_code,
        'message': message,
        'status_code': status_code,
        'has_details': details is not None,
        'extra_fields': list(kwargs.keys())
    })
    
    return response, status_code

def api_response(
    success: bool,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None,
    **kwargs
) -> Union[Dict[str, Any], tuple]:
    """
    通用API响应函数
    兼容现有的响应格式
    
    Args:
        success: 是否成功
        message: 响应消息
        data: 响应数据
        error_code: 错误代码（失败时）
        **kwargs: 其他响应字段
        
    Returns:
        成功时返回响应字典，失败时返回(响应字典, 状态码)元组
    """
    if success:
        return success_response(message, data, **kwargs)
    else:
        return error_response(error_code or 'INTERNAL_ERROR', message, data, **kwargs)

def json_response(
    success: bool,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None,
    **kwargs
):
    """
    返回JSON响应
    自动处理状态码设置
    
    Args:
        success: 是否成功
        message: 响应消息
        data: 响应数据
        error_code: 错误代码（失败时）
        **kwargs: 其他响应字段
        
    Returns:
        Flask Response对象
    """
    if success:
        response_data = success_response(message, data, **kwargs)
        return jsonify(response_data)
    else:
        response_data, status_code = error_response(error_code or 'INTERNAL_ERROR', message, data, **kwargs)
        return jsonify(response_data), status_code

def validate_and_respond(
    validation_func,
    success_message: str = '操作成功',
    error_code: str = 'VALIDATION_ERROR'
):
    """
    验证装饰器
    用于路由函数的数据验证
    
    Args:
        validation_func: 验证函数，返回(is_valid, error_message, data)
        success_message: 成功消息
        error_code: 验证失败时的错误代码
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # 执行验证
                is_valid, error_message, validated_data = validation_func()
                
                if not is_valid:
                    if is_ajax_request():
                        return json_response(False, error_message, error_code=error_code)
                    else:
                        # 对于非AJAX请求，继续使用flash消息
                        from flask import flash, redirect, url_for
                        flash(error_message, 'error')
                        return redirect(url_for('main.index'))
                
                # 验证通过，执行原函数
                return func(validated_data, *args, **kwargs)
                
            except Exception as e:
                logger.error("验证装饰器执行失败", error=e)
                if is_ajax_request():
                    return json_response(False, '验证过程中发生错误', error_code='INTERNAL_ERROR')
                else:
                    from flask import flash, redirect, url_for
                    flash('验证过程中发生错误', 'error')
                    return redirect(url_for('main.index'))
                    
        return wrapper
    return decorator 