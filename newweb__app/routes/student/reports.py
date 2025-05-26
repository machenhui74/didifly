"""
报告和文件下载相关路由
处理各种文件下载功能
"""

from flask import Blueprint, request, send_file, flash, redirect, url_for, session, current_app
from datetime import datetime
import os
import shutil

from ...logic.auth import login_required, assessor_required, teacher_required
from ...logic.cpbg.plan_generator import generate_plan, generate_direct_plan
from ...utils.logger import get_logger, log_performance, log_business_flow, log_user_action

# 导入共享工具函数
from .utils import ABILITY_PREFIX_MAPPING, find_report_file, create_zip_from_folder

# 创建报告下载蓝图
reports_bp = Blueprint('reports', __name__)
logger = get_logger('student_reports')

# ================================
# 报告下载路由
# ================================

@reports_bp.route('/download_report')
@assessor_required
def download_report():
    """下载最新生成的报告"""
    try:
        last_report = session.get('last_report')
        if not last_report:
            flash('没有可下载的报告。请先完成测评。', 'warning')
            return redirect(url_for('student.results'))
        
        # 查找报告文件
        report_path = find_report_file(last_report)
        if not report_path:
            current_app.logger.error(f"报告文件不存在: {last_report}")
            flash(f'报告文件不存在: {last_report}', 'error')
            return redirect(url_for('student.results'))
        
        return send_file(report_path, as_attachment=True, download_name=last_report)
        
    except Exception as e:
        current_app.logger.error(f"下载报告时出错: {str(e)}")
        flash(f'下载失败: {str(e)}', 'error')
        return redirect(url_for('student.results'))

# ================================
# 训练计划下载路由
# ================================

@reports_bp.route('/download_plan', methods=['GET', 'POST'])
@teacher_required
def download_plan():
    """下载训练计划（测评结果模式）"""
    if request.method == 'GET':
        return redirect(url_for('student.select_weeks'))
    
    return _download_plan_helper('assessment')

@reports_bp.route('/download_plan_direct', methods=['POST'])
@teacher_required
def download_plan_direct():
    """下载专注力备课训练计划"""
    return _download_plan_helper('direct')

@log_business_flow('训练方案下载', '生成ZIP文件')
@log_performance('download_plan_helper')
def _download_plan_helper(plan_type):
    """训练计划下载的通用辅助函数"""
    folder_path = None  # 用于记录需要删除的文件夹路径
    try:
        logger.info(f"🔄 开始处理训练方案下载: {plan_type}")
        
        # 获取周数
        weeks = int(request.form.get('weeks', '1'))
        logger.debug("📊 获取下载参数", extra_data={
            'plan_type': plan_type,
            'weeks': weeks
        })
        
        # 获取配置
        source_folder = current_app.config.get('SOURCE_FOLDER', './training_files')
        destination_folder = current_app.config.get('DESTINATION_FOLDER', './generated_plans')
        
        if plan_type == 'assessment':
            # 测评结果模式
            results_data = session.get('results_data')
            if not results_data:
                logger.warn("❌ 测评结果数据不存在")
                flash('没有找到测评结果数据。请先完成测评。', 'warning')
                return redirect(url_for('main.index'))
            
            name = results_data.get('name', '学员')
            age = results_data.get('age', 6)
            
            logger.info("📋 处理测评结果模式", extra_data={
                'student_name': name,
                'student_age': age,
                'weeks': weeks
            })
            
            # 构建训练参数
            child_ratings = {}
            for prefix, ability_name in [(k, v) for k, v in ABILITY_PREFIX_MAPPING.items() if k.startswith('visual')]:
                if f'{ABILITY_PREFIX_MAPPING[prefix]}_current' in results_data:
                    child_ratings[prefix] = results_data[f'{ABILITY_PREFIX_MAPPING[prefix]}_current']
            
            # 生成训练方案
            folder_name = generate_plan(name, age, child_ratings, source_folder, destination_folder, weeks)
            zip_filename = f"{name}_测评训练方案_{weeks}周_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            redirect_url = 'student.select_weeks'
            
        else:
            # 专注力备课模式
            result_data = session.get('direct_plan_result')
            difficulty_data = session.get('direct_plan_difficulty', {})
            
            if not result_data:
                logger.warn("❌ 专注力备课数据不存在")
                flash('没有可下载的训练计划。请先生成计划。', 'warning')
                return redirect(url_for('student.direct_plan'))
            
            name = result_data.get('name', '学员')
            age = result_data.get('age', 6)
            
            logger.info("📋 处理专注力备课模式", extra_data={
                'student_name': name,
                'student_age': age,
                'weeks': weeks,
                'difficulty_data': difficulty_data
            })
            
            # 构建参数
            target_difficulties = difficulty_data
            child_ratings = {key: "中等" for key in target_difficulties.keys()}
            
            # 生成训练方案
            folder_name = generate_direct_plan(
                name, age, child_ratings, target_difficulties, 
                source_folder, destination_folder, weeks
            )
            
            difficulty_str = '_'.join([f"{k}_{v}" for k, v in difficulty_data.items()])
            zip_filename = f"{name}_专注力训练计划_{difficulty_str}_{weeks}周_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            redirect_url = 'student.select_weeks_direct'
        
        # 记录生成的文件夹路径，用于后续删除
        folder_path = os.path.join(destination_folder, folder_name)
        logger.info("📁 训练方案生成完成", extra_data={
            'folder_name': folder_name,
            'folder_path': folder_path
        })
        
        # 创建ZIP文件
        logger.info("📦 开始创建ZIP文件")
        memory_file = create_zip_from_folder(folder_path, destination_folder)
        
        # 在发送文件前删除原始文件夹以节省存储空间
        try:
            if folder_path and os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                logger.info("🗑️ 已删除训练方案文件夹", extra_data={
                    'folder_path': folder_path
                })
        except Exception as delete_error:
            logger.warn("⚠️ 删除训练方案文件夹失败", error=delete_error, extra_data={
                'folder_path': folder_path
            })
        
        logger.info("✅ 训练方案下载准备完成", extra_data={
            'zip_filename': zip_filename,
            'plan_type': plan_type
        })
        
        # 记录用户操作
        log_user_action('下载训练方案', {
            'plan_type': plan_type,
            'student_name': name if 'name' in locals() else 'unknown',
            'weeks': weeks,
            'filename': zip_filename
        })
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
        
    except Exception as e:
        logger.error("❌ 下载训练计划时发生错误", error=e, extra_data={
            'plan_type': plan_type,
            'folder_path': folder_path
        })
        
        # 如果出错且文件夹已生成，尝试清理
        if folder_path and os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                logger.info("🔧 错误处理：已删除训练方案文件夹", extra_data={
                    'folder_path': folder_path
                })
            except Exception as cleanup_error:
                logger.warn("⚠️ 错误处理：删除文件夹失败", error=cleanup_error, extra_data={
                    'folder_path': folder_path
                })
        
        flash(f'下载失败: {str(e)}', 'error')
        return redirect(url_for(redirect_url if 'redirect_url' in locals() else 'main.index')) 