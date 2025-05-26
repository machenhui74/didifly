#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据验证模块
整合现有验证逻辑，提供统一的验证规则和函数
"""

import re
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional, Union
from flask import request
from .logger import get_logger

logger = get_logger('validators')

# ================================
# 基础验证函数
# ================================

def is_not_empty(value: str, field_name: str = "字段") -> Tuple[bool, str]:
    """验证字段不为空"""
    if not value or not value.strip():
        return False, f"{field_name}不能为空"
    return True, ""

def is_valid_date(date_str: str, field_name: str = "日期") -> Tuple[bool, str]:
    """验证日期格式 (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, f"{field_name}格式无效，请使用YYYY-MM-DD格式"

def is_valid_age(age_value: Union[str, int], min_age: int = 4, max_age: int = 12) -> Tuple[bool, str]:
    """验证年龄范围"""
    try:
        age = int(age_value)
        if age < min_age or age > max_age:
            return False, f"年龄必须在{min_age}-{max_age}岁之间"
        return True, ""
    except (ValueError, TypeError):
        return False, "年龄必须是数字"

def is_valid_number(value: Union[str, int], field_name: str = "数值", min_val: int = None, max_val: int = None) -> Tuple[bool, str]:
    """验证数值范围"""
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            return False, f"{field_name}不能小于{min_val}"
        if max_val is not None and num > max_val:
            return False, f"{field_name}不能大于{max_val}"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{field_name}必须是数字"

def is_valid_password(password: str) -> Tuple[bool, str]:
    """
    验证密码强度
    基于现有的密码验证逻辑
    """
    if len(password) < 6:
        return False, "密码长度至少需要6个字符"
    
    # 检查是否包含必要的字符类型
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    # 强密码要求（8位以上且包含多种字符类型）
    if len(password) >= 8 and sum([has_upper, has_lower, has_digit, has_special]) >= 3:
        return True, ""
    
    # 中等密码要求（6位以上）
    if len(password) >= 6:
        return True, ""
    
    return False, "密码必须包含至少8个字符，包括大写字母、小写字母、数字和特殊字符"

# ================================
# 业务验证函数
# ================================

def validate_student_basic_info(form_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    验证学生基本信息
    整合现有的学生信息验证逻辑
    """
    validated_data = {}
    
    # 验证姓名
    name = form_data.get('name', '').strip()
    is_valid, error_msg = is_not_empty(name, "学生姓名")
    if not is_valid:
        return False, error_msg, {}
    validated_data['name'] = name
    
    # 验证出生日期
    dob_str = form_data.get('dob', '').strip()
    is_valid, error_msg = is_not_empty(dob_str, "出生日期")
    if not is_valid:
        return False, error_msg, {}
    
    is_valid, error_msg = is_valid_date(dob_str, "出生日期")
    if not is_valid:
        return False, error_msg, {}
    validated_data['dob'] = dob_str
    
    # 验证测评日期
    test_date_str = form_data.get('test_date', '').strip()
    is_valid, error_msg = is_not_empty(test_date_str, "测评日期")
    if not is_valid:
        return False, error_msg, {}
    
    is_valid, error_msg = is_valid_date(test_date_str, "测评日期")
    if not is_valid:
        return False, error_msg, {}
    validated_data['test_date'] = test_date_str
    
    # 验证训练中心（可选）
    training_center = form_data.get('training_center', '').strip()
    validated_data['training_center'] = training_center
    
    # 验证测评师（可选）
    assessor = form_data.get('assessor', '').strip()
    validated_data['assessor'] = assessor
    
    logger.debug("✅ 学生基本信息验证通过", extra_data={
        'student_name': name,
        'dob': dob_str,
        'test_date': test_date_str
    })
    
    return True, "", validated_data

def validate_assessment_data(form_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    验证测评数据
    基于现有的测评数据验证逻辑
    """
    # 字段映射（来自现有代码）
    FIELD_MAPPING = {
        'vb': 'visual_breadth',
        'vd': 'visual_discrimination', 
        'vm': 'visuo_motor',
        'vm2': 'visual_memory',
        'ab': 'auditory_breadth',
        'ad': 'auditory_discrimination',
        'am': 'auditory_motor',
        'am2': 'auditory_memory'
    }
    
    validated_data = {}
    has_data = False
    
    for form_field, standard_name in FIELD_MAPPING.items():
        value = form_data.get(form_field, '').strip()
        if value:
            is_valid, error_msg = is_valid_number(value, f"测评数据({form_field})", min_val=0)
            if not is_valid:
                return False, error_msg, {}
            validated_data[standard_name] = int(value)
            has_data = True
    
    if not has_data:
        return False, "请至少填写一项测评数据", {}
    
    logger.debug("✅ 测评数据验证通过", extra_data={
        'assessment_count': len(validated_data),
        'abilities': list(validated_data.keys())
    })
    
    return True, "", validated_data

def validate_direct_plan_data(form_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    验证专注力备课数据
    基于现有的专注力备课验证逻辑
    """
    validated_data = {}
    
    # 验证姓名
    name = form_data.get('child_name', '').strip()
    is_valid, error_msg = is_not_empty(name, "学员姓名")
    if not is_valid:
        return False, error_msg, {}
    validated_data['name'] = name
    
    # 验证年龄
    age_str = form_data.get('child_age', '').strip()
    is_valid, error_msg = is_not_empty(age_str, "学员年龄")
    if not is_valid:
        return False, error_msg, {}
    
    is_valid, error_msg = is_valid_age(age_str)
    if not is_valid:
        return False, error_msg, {}
    validated_data['age'] = int(age_str)
    
    # 验证训练难度选择
    difficulty_fields = ['visual_breadth', 'visual_discrimination', 'visuo_motor', 'visual_memory']
    difficulty_data = {}
    
    for field in difficulty_fields:
        value = form_data.get(field, '').strip()
        if not value:
            return False, "请选择所有训练项目的难度", {}
        difficulty_data[field] = value
    
    validated_data['difficulty_data'] = difficulty_data
    
    logger.debug("✅ 专注力备课数据验证通过", extra_data={
        'student_name': name,
        'student_age': validated_data['age'],
        'difficulty_fields': list(difficulty_data.keys())
    })
    
    return True, "", validated_data

def validate_user_data(form_data: Dict[str, Any], is_edit: bool = False) -> Tuple[bool, str, Dict[str, Any]]:
    """
    验证用户数据
    基于现有的用户管理验证逻辑
    """
    validated_data = {}
    
    # 验证用户名
    username = form_data.get('new_username' if not is_edit else 'username', '').strip()
    is_valid, error_msg = is_not_empty(username, "用户账号")
    if not is_valid:
        return False, error_msg, {}
    validated_data['username'] = username
    
    # 验证姓名
    name = form_data.get('new_name', '').strip()
    is_valid, error_msg = is_not_empty(name, "用户姓名")
    if not is_valid:
        return False, error_msg, {}
    validated_data['name'] = name
    
    # 验证密码（新增用户时必填，编辑时可选）
    password = form_data.get('new_password', '').strip()
    if not is_edit and not password:
        return False, "密码不能为空", {}
    
    if password:
        is_valid, error_msg = is_valid_password(password)
        if not is_valid:
            return False, error_msg, {}
        validated_data['password'] = password
    
    # 验证门店（可选）
    store = form_data.get('new_store', '').strip()
    validated_data['store'] = store
    
    logger.debug("✅ 用户数据验证通过", extra_data={
        'username': username,
        'name': name,
        'is_edit': is_edit,
        'has_password': bool(password)
    })
    
    return True, "", validated_data

def validate_training_plan_data(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    验证感统训练计划数据
    基于现有的训练计划验证逻辑
    """
    validated_data = {}
    
    # 验证学员姓名
    student_name = data.get('studentName', '').strip()
    is_valid, error_msg = is_not_empty(student_name, "学员姓名")
    if not is_valid:
        return False, error_msg, {}
    validated_data['student_name'] = student_name
    
    # 验证学员年龄
    student_age = data.get('studentAge', 0)
    is_valid, error_msg = is_valid_age(student_age)
    if not is_valid:
        return False, error_msg, {}
    validated_data['student_age'] = int(student_age)
    
    # 验证选择的标签
    selected_tags = data.get('selectedTags', [])
    if not selected_tags or not isinstance(selected_tags, list):
        return False, "请至少选择一个训练标签", {}
    validated_data['selected_tags'] = selected_tags
    
    logger.debug("✅ 训练计划数据验证通过", extra_data={
        'student_name': student_name,
        'student_age': validated_data['student_age'],
        'tags_count': len(selected_tags)
    })
    
    return True, "", validated_data

# ================================
# 验证装饰器工厂函数
# ================================

def create_validator(validation_func):
    """
    创建验证装饰器
    用于路由函数的数据验证
    """
    def validator():
        """验证函数包装器"""
        try:
            # 获取请求数据
            if request.method == 'POST':
                if request.content_type and 'application/json' in request.content_type:
                    form_data = request.get_json() or {}
                else:
                    form_data = request.form.to_dict()
            else:
                form_data = request.args.to_dict()
            
            # 执行验证
            return validation_func(form_data)
            
        except Exception as e:
            logger.error("数据验证过程中发生错误", error=e)
            return False, "数据验证过程中发生错误", {}
    
    return validator

# ================================
# 预定义验证器
# ================================

# 学生测评验证器
validate_student_submission = create_validator(
    lambda form_data: (
        lambda basic_valid, basic_msg, basic_data: (
            validate_assessment_data(form_data) if basic_valid else (False, basic_msg, {})
        )(*validate_student_basic_info(form_data))
    )
)

# 专注力备课验证器
validate_direct_plan_submission = create_validator(validate_direct_plan_data)

# 用户添加验证器
validate_user_addition = create_validator(lambda form_data: validate_user_data(form_data, is_edit=False))

# 用户编辑验证器
validate_user_edit = create_validator(lambda form_data: validate_user_data(form_data, is_edit=True))

# 训练计划验证器
validate_training_plan_submission = create_validator(validate_training_plan_data) 