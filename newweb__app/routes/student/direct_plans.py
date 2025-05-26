"""
专注力备课相关路由
处理直接训练计划生成
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app

from ...logic.auth import login_required, teacher_required
from ...utils.logger import get_logger

# 创建专注力备课蓝图
direct_plans_bp = Blueprint('direct_plans', __name__)
logger = get_logger('direct_plans')

@direct_plans_bp.route('/plan')
@teacher_required
def direct_plan():
    """直接训练计划生成页面"""
    return render_template('direct_plan.html')

@direct_plans_bp.route('/select_weeks', methods=['GET', 'POST'])
@teacher_required
def select_weeks_direct():
    """选择训练周数页面（专注力备课）"""
    if request.method == 'POST':
        # 处理来自direct_plan.html的表单数据
        try:
            # 获取和验证基本信息
            name = request.form.get('child_name', '').strip()
            age_str = request.form.get('child_age', '').strip()
            
            if not name or not age_str:
                flash('请填写所有必填字段！', 'error')
                return redirect(url_for('student.direct_plan'))
            
            try:
                age = int(age_str)
                if age < 4 or age > 12:
                    flash('年龄必须在4-12岁之间！', 'error')
                    return redirect(url_for('student.direct_plan'))
            except ValueError:
                flash('年龄必须是数字！', 'error')
                return redirect(url_for('student.direct_plan'))
            
            # 获取训练难度选择
            difficulty_fields = ['visual_breadth', 'visual_discrimination', 'visuo_motor', 'visual_memory']
            difficulty_data = {}
            
            for field in difficulty_fields:
                value = request.form.get(field, '').strip()
                if not value:
                    flash('请选择所有训练项目的难度！', 'error')
                    return redirect(url_for('student.direct_plan'))
                difficulty_data[field] = value
            
            # 保存到session
            result_data = {
                'name': name,
                'age': age,
                'difficulty_data': difficulty_data,
                'success': True
            }
            
            session['direct_plan_result'] = result_data
            session['direct_plan_name'] = name
            session['direct_plan_difficulty'] = difficulty_data
            
            logger.info("📋 专注力备课数据已保存", extra_data={
                'student_name': name,
                'student_age': age,
                'difficulty_data': difficulty_data
            })
            
            # 渲染选择周数页面，并传递学生姓名
            return render_template('select_weeks_direct.html', name=name)
            
        except Exception as e:
            current_app.logger.error(f"处理专注力备课数据时出错: {str(e)}")
            flash(f'处理数据时出错: {str(e)}', 'error')
            return redirect(url_for('student.direct_plan'))
    
    # GET请求，检查是否有session数据
    if 'direct_plan_name' in session:
        name = session['direct_plan_name']
        return render_template('select_weeks_direct.html', name=name)
    else:
        flash('请先填写学生信息和选择训练难度！', 'warning')
        return redirect(url_for('student.direct_plan')) 