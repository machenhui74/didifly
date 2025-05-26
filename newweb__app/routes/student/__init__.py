"""
学生管理模块
将原有的student.py拆分为多个专门的子模块，提高代码可维护性
"""

from flask import Blueprint

# 导入所有子蓝图
from .assessment import assessment_bp
from .profiles import profiles_bp  
from .reports import reports_bp
from .training_plans import training_plans_bp
from .direct_plans import direct_plans_bp
from .user_profile import user_profile_bp

# 创建主学生蓝图
student_bp = Blueprint('student', __name__)

# 为了保持向后兼容，将原有的路由映射到新的子模块
# 导入所有路由函数
from .assessment import submit, results, select_weeks
from .reports import download_report, download_plan, download_plan_direct
from .profiles import student_profiles, view_student_profiles, export_profiles, export_selected_profiles
from .training_plans import training_plan, generate_training_plan, download_training_plan
from .direct_plans import direct_plan, select_weeks_direct
from .user_profile import user_profile, update_user_profile

# 将路由添加到主蓝图以保持兼容性
student_bp.add_url_rule('/submit', 'submit', submit, methods=['POST'])
student_bp.add_url_rule('/results', 'results', results)
student_bp.add_url_rule('/select_weeks', 'select_weeks', select_weeks)
student_bp.add_url_rule('/student_profiles', 'student_profiles', student_profiles)
student_bp.add_url_rule('/view_student_profiles', 'view_student_profiles', view_student_profiles)
student_bp.add_url_rule('/export_profiles', 'export_profiles', export_profiles)
student_bp.add_url_rule('/export_selected_profiles', 'export_selected_profiles', export_selected_profiles)
student_bp.add_url_rule('/download_report', 'download_report', download_report)
student_bp.add_url_rule('/download_plan', 'download_plan', download_plan, methods=['GET', 'POST'])
student_bp.add_url_rule('/download_plan_direct', 'download_plan_direct', download_plan_direct, methods=['POST'])
student_bp.add_url_rule('/training_plan', 'training_plan', training_plan)
student_bp.add_url_rule('/generate_training_plan', 'generate_training_plan', generate_training_plan, methods=['POST'])
student_bp.add_url_rule('/download_training_plan', 'download_training_plan', download_training_plan)
student_bp.add_url_rule('/direct_plan', 'direct_plan', direct_plan)
student_bp.add_url_rule('/select_weeks_direct', 'select_weeks_direct', select_weeks_direct, methods=['GET', 'POST'])
student_bp.add_url_rule('/user_profile', 'user_profile', user_profile)
student_bp.add_url_rule('/update_user_profile', 'update_user_profile', update_user_profile, methods=['POST']) 