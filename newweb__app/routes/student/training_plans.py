"""
感统训练计划相关路由
处理基于标签的训练计划生成
"""

from flask import Blueprint, render_template, request, jsonify, session, send_file, current_app
from datetime import datetime
import json
import os
import tempfile
import uuid

from ...logic.auth import login_required, teacher_required
from ...logic.training_plan_generator import WebTrainingPlanGenerator
from ...utils.logger import get_logger, log_performance, log_business_flow, log_user_action

# 创建训练计划蓝图
training_plans_bp = Blueprint('training_plans', __name__)
logger = get_logger('training_plans')

@training_plans_bp.route('/plan')
@teacher_required
def training_plan():
    """感统训练计划生成页面"""
    is_admin = session.get('user_id') == 'admin'
    return render_template('training_plan.html', is_admin=is_admin)

@training_plans_bp.route('/generate', methods=['POST'])
@teacher_required
@log_business_flow('感统训练', '生成训练方案')
@log_performance('generate_training_plan')
def generate_training_plan():
    """基于标签生成感统训练计划"""
    try:
        logger.info("🔄 开始生成感统训练计划")
        
        # 解析请求数据
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            student_name = data.get('studentName', '').strip()
            selected_tags = data.get('selectedTags', [])
            student_age = data.get('studentAge', 6)
        else:
            student_name = request.form.get('name', '').strip()
            selected_tags_json = request.form.get('selected_tags', '[]')
            student_age = request.form.get('age', 6)
            try:
                selected_tags = json.loads(selected_tags_json)
                student_age = int(student_age)
            except:
                selected_tags = []
                student_age = 6
        
        logger.debug("📝 解析请求数据", extra_data={
            'student_name': student_name,
            'student_age': student_age,
            'selected_tags_count': len(selected_tags),
            'selected_tags': selected_tags
        })
        
        # 验证输入
        if not student_name:
            logger.warn("❌ 学员姓名为空")
            return jsonify({'success': False, 'message': '请输入学员姓名'})
        if not selected_tags:
            logger.warn("❌ 未选择训练标签")
            return jsonify({'success': False, 'message': '请至少选择一个训练标签'})
        
        # 检查动作库文件
        action_db_path = os.path.join(current_app.root_path, 'data', 'action_database.xlsx')
        if not os.path.exists(action_db_path):
            logger.error("❌ 动作库文件不存在", extra_data={
                'action_db_path': action_db_path
            })
            return jsonify({'success': False, 'message': '动作库文件不存在，请联系管理员'})
        
        logger.info("📚 动作库文件检查通过", extra_data={
            'action_db_path': action_db_path
        })
        
        # 生成训练计划
        logger.info("🎯 开始生成训练计划")
        generator = WebTrainingPlanGenerator()
        document_data, error_message = generator.generate_training_plan(
            student_name, student_age, selected_tags, action_db_path
        )
        
        if document_data:
            # 保存到临时文件
            file_id = str(uuid.uuid4())
            filename = f"{student_name}_感统训练方案_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            file_path = os.path.join(tempfile.gettempdir(), f"{file_id}_{filename}")
            
            with open(file_path, 'wb') as f:
                f.write(document_data)
            
            # 保存到session
            session['training_plan_file'] = {
                'file_path': file_path,
                'filename': filename,
                'student_name': student_name,
                'selected_tags': selected_tags
            }
            
            logger.info("✅ 感统训练方案生成成功", extra_data={
                'student_name': student_name,
                'filename': filename,
                'file_size_bytes': len(document_data),
                'tags_count': len(selected_tags)
            })
            
            # 记录用户操作
            log_user_action('生成感统训练方案', {
                'student_name': student_name,
                'student_age': student_age,
                'selected_tags': selected_tags,
                'filename': filename
            })
            
            return jsonify({
                'success': True, 
                'message': f"成功为{student_name}生成感统训练方案",
                'file_path': file_path,
                'file_name': filename
            })
        else:
            logger.error("❌ 感统训练方案生成失败", extra_data={
                'student_name': student_name,
                'error_message': error_message
            })
            return jsonify({'success': False, 'message': error_message or '生成失败'})
            
    except Exception as e:
        logger.error("❌ 生成训练计划时发生未预期错误", error=e, extra_data={
            'student_name': student_name if 'student_name' in locals() else 'unknown',
            'request_content_type': request.content_type
        })
        return jsonify({'success': False, 'message': f'生成训练计划时出错: {str(e)}'})

@training_plans_bp.route('/download')
@teacher_required
def download_training_plan():
    """下载感统训练方案"""
    try:
        file_info = session.get('training_plan_file')
        if not file_info:
            flash('没有可下载的训练方案。请先生成方案。', 'warning')
            return redirect(url_for('student.training_plan'))
        
        file_path = file_info.get('file_path')
        filename = file_info.get('filename')
        
        if not file_path or not os.path.exists(file_path):
            flash('训练方案文件不存在或已过期。请重新生成。', 'error')
            return redirect(url_for('student.training_plan'))
        
        return send_file(
            file_path,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"下载感统训练方案时出错: {str(e)}")
        flash(f'下载失败: {str(e)}', 'error')
        return redirect(url_for('student.training_plan')) 