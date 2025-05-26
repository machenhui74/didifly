"""
学生相关工具函数
处理学生档案数据的过滤、搜索、排序等功能
"""

import os
import json
from datetime import datetime
from flask import current_app

from ..utils.logger import get_logger
from .auth import UserRole, get_user_role, get_user_training_center

# TODO: 从 ..config 导入配置, 例如 STUDENT_PROFILES_FILE
# from ..config import STUDENT_PROFILES_FILE 

logger = get_logger('student_utils')

def load_student_profiles():
    """加载学生档案数据"""
    profiles_file = current_app.config['STUDENT_PROFILES_FILE']
    if os.path.exists(profiles_file):
        try:
            with open(profiles_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载学生档案时出错: {str(e)}")
            return []
    return []

def save_student_profiles(profiles):
    """保存学生档案数据"""
    try:
        profiles_file = current_app.config['STUDENT_PROFILES_FILE']
        with open(profiles_file, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存学生档案时出错: {str(e)}")
        return False

def filter_accessible_profiles(all_profiles, user_id, user_store=None):
    """
    根据用户权限过滤可访问的学生档案
    
    Args:
        all_profiles: 所有学生档案列表
        user_id: 用户ID
        user_store: 用户所属训练中心（可选，会自动获取）
    
    Returns:
        过滤后的学生档案列表
    """
    user_role = get_user_role(user_id)
    
    # 管理员可以查看所有档案
    if user_role == UserRole.ADMIN:
        logger.debug(f"管理员 {user_id} 访问所有学生档案")
        return all_profiles
    
    # 校长只能查看同训练中心的档案
    if user_role == UserRole.PRINCIPAL:
        if user_store is None:
            user_store = get_user_training_center(user_id)
        
        if not user_store:
            logger.warning(f"校长 {user_id} 没有关联的训练中心，无法访问学生档案")
            return []
        
        filtered_profiles = [
            profile for profile in all_profiles 
            if profile.get('training_center', '') == user_store
        ]
        
        logger.debug(f"校长 {user_id} 访问训练中心 {user_store} 的 {len(filtered_profiles)} 条学生档案")
        return filtered_profiles
    
    # 测评师可以查看所有档案
    if user_role == UserRole.ASSESSOR:
        logger.debug(f"测评师 {user_id} 访问所有学生档案")
        return all_profiles
    
    # 老师只能查看同训练中心的档案
    if user_role == UserRole.TEACHER:
        if user_store is None:
            user_store = get_user_training_center(user_id)
        
        if not user_store:
            logger.warning(f"老师 {user_id} 没有关联的训练中心，无法访问学生档案")
            return []
        
        filtered_profiles = [
            profile for profile in all_profiles 
            if profile.get('training_center', '') == user_store
        ]
        
        logger.debug(f"老师 {user_id} 访问训练中心 {user_store} 的 {len(filtered_profiles)} 条学生档案")
        return filtered_profiles
    
    # 未知权限或未登录用户
    logger.warning(f"用户 {user_id} 权限不足或未知，无法访问学生档案")
    return []

def search_profiles(profiles, search_name='', search_assessor=''):
    """搜索学生档案"""
    if not search_name and not search_assessor:
        return profiles
    
    filtered = []
    for profile in profiles:
        name_match = not search_name or search_name.lower() in profile.get('name', '').lower()
        assessor_match = not search_assessor or search_assessor.lower() in profile.get('assessor', '').lower()
        
        if name_match and assessor_match:
            filtered.append(profile)
    
    return filtered

def sort_profiles(profiles, sort_by='name', sort_order='asc'):
    """排序学生档案"""
    reverse = sort_order == 'desc'
    
    def get_sort_key(profile):
        value = profile.get(sort_by, '')
        
        # 处理数字字段
        if sort_by in ['age', 'vb', 'vd', 'vm', 'vm2', 'ab', 'ad', 'am', 'am2']:
            try:
                return int(value) if value else 0
            except (ValueError, TypeError):
                return 0
        
        # 处理日期字段
        if sort_by == 'test_date':
            try:
                return datetime.strptime(value, '%Y-%m-%d') if value else datetime.min
            except (ValueError, TypeError):
                return datetime.min
        
        # 处理字符串字段
        return str(value).lower()
    
    return sorted(profiles, key=get_sort_key, reverse=reverse)

def paginate_profiles(profiles, page=1, limit=50):
    """分页处理学生档案"""
    total_count = len(profiles)
    total_pages = (total_count + limit - 1) // limit
    
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    paginated_profiles = profiles[start_index:end_index]
    
    return {
        'profiles': paginated_profiles,
        'pagination': {
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    }

def create_csv_content(profiles):
    """根据学生档案列表创建CSV内容"""
    csv_content = "姓名,年龄,出生日期,测评日期,训练中心,测评师,视觉广度分数,视觉广度评级,视觉广度目标,视觉辨别分数,视觉辨别评级,视觉辨别目标,视动统合分数,视动统合评级,视动统合目标,视觉记忆分数,视觉记忆评级,视觉记忆目标,听觉广度分数,听觉广度评级,听觉广度目标,听觉分辨分数,听觉分辨评级,听觉分辨目标,听动统合分数,听动统合评级,听动统合目标,听觉记忆分数,听觉记忆评级,听觉记忆目标,提交人,提交时间\n"
    
    # 字段映射：完整字段名 -> 简化字段名
    field_mapping = {
        'visual_breadth': 'vb',
        'visual_discrimination': 'vd', 
        'visuo_motor': 'vm',
        'visual_memory': 'vm2',
        'auditory_breadth': 'ab',
        'auditory_discrimination': 'ad',
        'auditory_motor': 'am',
        'auditory_memory': 'am2'
    }
    
    def get_score_value(profile, field_key):
        """获取测评分数值，兼容新旧数据格式"""
        # 首先尝试直接获取（旧格式）
        value = profile.get(field_key)
        if value is not None:
            return str(value)
        
        # 然后尝试从assessment_data获取（新格式）
        assessment_data = profile.get('assessment_data', {})
        # 找到对应的完整字段名
        full_field_name = None
        for full_field, short_field in field_mapping.items():
            if short_field == field_key:
                full_field_name = full_field
                break
        
        if full_field_name:
            value = assessment_data.get(full_field_name)
            if value is not None:
                return str(value)
        
        return ''
    
    def get_rating_value(profile, field_key, rating_type):
        """获取评级值，兼容新旧数据格式"""
        # 构造评级字段名
        rating_field = f"{field_key}_{rating_type}"
        
        # 首先尝试直接获取（旧格式）
        value = profile.get(rating_field)
        if value is not None:
            return str(value)
        
        # 然后尝试从rating_results获取（新格式）
        rating_results = profile.get('rating_results', {})
        # 找到对应的完整字段名
        full_field_name = None
        for full_field, short_field in field_mapping.items():
            if short_field == field_key:
                full_field_name = full_field
                break
        
        if full_field_name and full_field_name in rating_results:
            rating_data = rating_results[full_field_name]
            if rating_type == 'current':
                return rating_data.get('current_rating', '')
            elif rating_type == 'target':
                return str(rating_data.get('target_score', ''))
            elif rating_type == 'target_eval':
                return rating_data.get('target_rating', '')
        
        return ''
    
    for profile in profiles:
        row = [
            profile.get('name', ''),
            str(profile.get('age', '')),
            profile.get('dob', ''),
            profile.get('test_date', ''),
            profile.get('training_center', ''),
            profile.get('assessor', ''),
            # 视觉广度
            get_score_value(profile, 'vb'),
            get_rating_value(profile, 'vb', 'current'),
            get_rating_value(profile, 'vb', 'target'),
            # 视觉辨别
            get_score_value(profile, 'vd'),
            get_rating_value(profile, 'vd', 'current'),
            get_rating_value(profile, 'vd', 'target'),
            # 视动统合
            get_score_value(profile, 'vm'),
            get_rating_value(profile, 'vm', 'current'),
            get_rating_value(profile, 'vm', 'target'),
            # 视觉记忆
            get_score_value(profile, 'vm2'),
            get_rating_value(profile, 'vm2', 'current'),
            get_rating_value(profile, 'vm2', 'target'),
            # 听觉广度
            get_score_value(profile, 'ab'),
            get_rating_value(profile, 'ab', 'current'),
            get_rating_value(profile, 'ab', 'target'),
            # 听觉分辨
            get_score_value(profile, 'ad'),
            get_rating_value(profile, 'ad', 'current'),
            get_rating_value(profile, 'ad', 'target'),
            # 听动统合
            get_score_value(profile, 'am'),
            get_rating_value(profile, 'am', 'current'),
            get_rating_value(profile, 'am', 'target'),
            # 听觉记忆
            get_score_value(profile, 'am2'),
            get_rating_value(profile, 'am2', 'current'),
            get_rating_value(profile, 'am2', 'target'),
            # 提交信息
            profile.get('submitted_by', profile.get('created_by', '')),
            profile.get('submitted_at', profile.get('created_at', ''))
        ]
        csv_row = ','.join([f'"{str(item)}"' if ',' in str(item) else str(item) for item in row])
        csv_content += csv_row + "\n"
    
    return csv_content 