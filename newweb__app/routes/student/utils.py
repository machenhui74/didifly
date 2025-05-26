"""
学生模块共享的工具函数
从原student.py中提取的通用辅助函数
"""

from datetime import datetime
import os
import zipfile
import io
from flask import current_app

# ================================
# 常量定义
# ================================

# 字段映射：前端字段名 -> 标准名称
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

# 能力映射：标准名称 -> 前端前缀
ABILITY_PREFIX_MAPPING = {
    'visual_breadth': 'vb',
    'visual_discrimination': 'vd',
    'visuo_motor': 'vm',
    'visual_memory': 'vm2',
    'auditory_breadth': 'ab',
    'auditory_discrimination': 'ad',
    'auditory_motor': 'am',
    'auditory_memory': 'am2'
}

# ================================
# 通用工具函数
# ================================

def validate_date_fields(dob_str, test_date_str):
    """验证日期字段"""
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        test_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
        return True, dob, test_date
    except ValueError:
        return False, None, None

def calculate_age(dob):
    """根据出生日期计算年龄"""
    today = datetime.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def find_report_file(filename):
    """查找报告文件的实际路径"""
    report_folder = current_app.config.get('REPORT_OUTPUT_FOLDER', './reports')
    
    # 从文件名中提取姓名（假设格式为：姓名_日期_测评报告.docx）
    name_part = filename.split('_')[0] if '_' in filename else filename.replace('_测评报告.docx', '')
    
    possible_paths = [
        # 直接在报告文件夹根目录查找
        os.path.join(report_folder, filename),
        # 在{姓名}测评记录子文件夹中查找
        os.path.join(report_folder, f"{name_part}测评记录", filename),
        # 在当前目录查找
        os.path.join('.', filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            current_app.logger.info(f"找到报告文件: {path}")
            return path
    
    # 如果都找不到，记录详细的查找路径
    current_app.logger.error(f"报告文件未找到: {filename}")
    current_app.logger.error(f"已查找路径: {possible_paths}")
    return None

def create_zip_from_folder(folder_path, destination_folder):
    """从文件夹创建ZIP文件并返回内存文件"""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, destination_folder)
                zf.write(file_path, arc_name)
    
    memory_file.seek(0)
    return memory_file

def parse_assessment_data(form_data):
    """解析测评数据，统一字段映射"""
    assessment_data = {}
    for form_field, standard_name in FIELD_MAPPING.items():
        value = form_data.get(form_field, '').strip()
        if value:
            try:
                assessment_data[standard_name] = int(value)
            except ValueError:
                current_app.logger.warning(f"无效的测评数据值: {form_field}={value}")
    return assessment_data

def build_report_kwargs(name, age, test_date, training_center, assessor, rating_results):
    """构建报告生成参数"""
    kwargs = {
        'child_name': name,
        'child_age': age,
        'measure_date': test_date,
        'training_center': training_center,
        'assessor': assessor
    }
    
    # 添加所有能力数据
    for ability_name, result in rating_results.items():
        if ability_name in ABILITY_PREFIX_MAPPING:
            prefix = ABILITY_PREFIX_MAPPING[ability_name]
            kwargs.update({
                prefix: result['current_score'],
                f'{prefix}_eval': result['current_rating'],
                f'{prefix}_target': result['target_score'],
                f'{prefix}_target_eval': result['target_rating']
            })
    
    return kwargs

def build_results_data(name, age, test_date, training_center, assessor, rating_results):
    """构建结果页面数据"""
    results_data = {
        'name': name,
        'age': age,
        'test_date': test_date,
        'training_center': training_center,
        'assessor': assessor
    }
    
    # 添加所有能力数据
    for ability_name, result in rating_results.items():
        if ability_name in ABILITY_PREFIX_MAPPING:
            prefix = ABILITY_PREFIX_MAPPING[ability_name]
            results_data.update({
                prefix: result['current_score'],
                f'{prefix}_current': result['current_rating'],
                f'{prefix}_target': result['target_score'],
                f'{prefix}_target_eval': result['target_rating']
            })
    
    return results_data 