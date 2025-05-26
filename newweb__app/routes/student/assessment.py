"""
学生测评相关路由
处理测评数据提交、结果显示等功能
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from datetime import datetime

from ...logic.auth import login_required, assessor_required
from ...logic.student_utils import load_student_profiles, save_student_profiles
from ...logic.cpbg.baogao4 import ReportGenerator
from ...logic.cpbg.target_calculator import calculate_rating_and_target
from ...utils.logger import get_logger, log_performance, log_business_flow, log_user_action

# 导入共享工具函数
from .utils import (
    FIELD_MAPPING, ABILITY_PREFIX_MAPPING,
    validate_date_fields, calculate_age,
    parse_assessment_data, build_report_kwargs, build_results_data
)

# 创建测评蓝图
assessment_bp = Blueprint('assessment', __name__)
logger = get_logger('student_assessment')

# ================================
# 数据处理辅助函数
# ================================

def calculate_all_ratings(assessment_data, age):
    """计算所有能力的评级和目标分数"""
    rating_results = {}
    for ability_name, score in assessment_data.items():
        try:
            # 听动统合的函数中命名为audio_motor
            ability_type = ability_name if ability_name != 'auditory_motor' else 'audio_motor'
            current_rating, target_score, target_rating = calculate_rating_and_target(ability_type, age, score)
            rating_results[ability_name] = {
                'current_score': score,
                'current_rating': current_rating,
                'target_score': target_score,
                'target_rating': target_rating
            }
        except Exception as e:
            current_app.logger.error(f"计算能力评级时出错 {ability_name}: {str(e)}")
            rating_results[ability_name] = {
                'current_score': score,
                'current_rating': '未知',
                'target_score': score,
                'target_rating': '未知'
            }
    return rating_results

# ================================
# 路由处理函数
# ================================

@assessment_bp.route('/submit', methods=['POST'])
@assessor_required
@log_business_flow('学生测评', '提交测评数据')
@log_performance('submit_assessment')
def submit():
    """提交学生测评数据"""
    try:
        logger.info("🔄 开始处理学生测评数据提交")
        
        # 获取基本信息
        name = request.form.get('name', '').strip()
        dob_str = request.form.get('dob', '')
        test_date_str = request.form.get('test_date', '')
        training_center = request.form.get('training_center', '').strip()
        assessor = request.form.get('assessor', '').strip()
        
        logger.debug("📝 获取表单数据", extra_data={
            'student_name': name,
            'test_date': test_date_str,
            'training_center': training_center,
            'assessor': assessor
        })
        
        # 验证必填字段
        if not all([name, dob_str, test_date_str]):
            logger.warn("❌ 必填字段验证失败", extra_data={
                'missing_fields': [field for field, value in [
                    ('name', name), ('dob', dob_str), ('test_date', test_date_str)
                ] if not value]
            })
            flash('请填写所有必填字段！', 'error')
            return redirect(url_for('main.index'))
        
        # 解析和验证日期
        valid, dob, test_date = validate_date_fields(dob_str, test_date_str)
        if not valid:
            logger.warn("❌ 日期格式验证失败", extra_data={
                'dob_str': dob_str,
                'test_date_str': test_date_str
            })
            flash('日期格式无效！', 'error')
            return redirect(url_for('main.index'))
        
        # 计算年龄
        age = calculate_age(dob)
        logger.debug("📊 计算学生年龄", extra_data={'age': age})
        
        # 解析测评数据
        assessment_data = parse_assessment_data(request.form)
        if not assessment_data:
            logger.warn("❌ 测评数据为空")
            flash('请至少填写一项测评数据！', 'error')
            return redirect(url_for('main.index'))
        
        logger.info("📊 解析测评数据完成", extra_data={
            'assessment_count': len(assessment_data),
            'abilities': list(assessment_data.keys())
        })
        
        # 计算评级和目标分数
        rating_results = calculate_all_ratings(assessment_data, age)
        logger.info("🎯 评级计算完成", extra_data={
            'rating_count': len(rating_results)
        })
        
        # 生成测评报告
        try:
            logger.info("📄 开始生成测评报告")
            report_generator = ReportGenerator()
            kwargs = build_report_kwargs(name, age, test_date, training_center, assessor, rating_results)
            report_generator.generate_measurement_report(**kwargs)
            filename = f"{name}_{test_date}_测评报告.docx"
            session['last_report'] = filename
            
            logger.info("✅ 测评报告生成成功", extra_data={
                'report_filename': filename
            })
            flash(f'测评报告已生成：{filename}', 'success')
        except Exception as e:
            logger.error("❌ 生成报告失败", error=e, extra_data={
                'student_name': name
            })
            flash(f'生成报告时出错: {str(e)}', 'error')
        
        # 保存学生档案
        try:
            logger.info("💾 开始保存学生档案")
            profiles = load_student_profiles()
            profile_data = {
                'name': name,
                'dob': dob_str,
                'age': age,
                'test_date': test_date_str,
                'training_center': training_center,
                'assessor': assessor,
                'assessment_data': assessment_data,
                'rating_results': rating_results,
                'created_by': session.get('user_name', ''),
                'created_at': datetime.now().isoformat()
            }
            profiles.append(profile_data)
            save_student_profiles(profiles)
            
            logger.info("✅ 学生档案保存成功", extra_data={
                'student_name': name,
                'total_profiles': len(profiles)
            })
            
            # 记录用户操作
            log_user_action('创建学生档案', {
                'student_name': name,
                'training_center': training_center,
                'assessor': assessor
            })
            
        except Exception as e:
            logger.error("❌ 保存学生档案失败", error=e, extra_data={
                'student_name': name
            })
            flash(f'保存学生档案时出错: {str(e)}', 'warning')
        
        # 保存结果数据到session
        results_data = build_results_data(name, age, test_date_str, training_center, assessor, rating_results)
        session['results_data'] = results_data
        
        logger.info("🎉 学生测评流程完成", extra_data={
            'student_name': name,
            'success': True
        })
        
        return redirect(url_for('student.results'))
        
    except Exception as e:
        logger.error("❌ 处理提交数据时发生未预期错误", error=e, extra_data={
            'form_data_keys': list(request.form.keys()) if request.form else []
        })
        flash(f'处理数据时出错: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@assessment_bp.route('/results')
@assessor_required
def results():
    """显示测评结果页面"""
    results_data = session.get('results_data')
    if not results_data:
        current_app.logger.warning("results页面未找到session中的结果数据")
    return render_template('results.html', results_data=results_data)

@assessment_bp.route('/select_weeks')
@login_required
def select_weeks():
    """选择训练周数页面（从测评结果跳转）"""
    results_data = session.get('results_data')
    if not results_data:
        flash('没有找到测评结果数据。请先完成测评。', 'warning')
        return redirect(url_for('main.index'))
    
    return render_template('select_weeks.html', name=results_data.get('name', '学员')) 