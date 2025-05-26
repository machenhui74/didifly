"""
学生档案管理相关路由
处理档案查看、导出等功能
"""

from flask import Blueprint, render_template, request, jsonify, session, send_file, current_app, redirect, url_for, flash
from datetime import datetime
import io

from ...logic.auth import login_required, teacher_required
from ...logic.student_utils import load_student_profiles, filter_accessible_profiles, create_csv_content
from ...utils.logger import get_logger

# 创建档案管理蓝图
profiles_bp = Blueprint('profiles', __name__)
logger = get_logger('student_profiles')

# ================================
# 档案管理路由
# ================================

@profiles_bp.route('/student_profiles')
@teacher_required
def student_profiles():
    """学生档案API接口 - 支持分页、排序、搜索"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search_name = request.args.get('search_name', '').strip()
        search_assessor = request.args.get('search_assessor', '').strip()
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        
        # 新增筛选参数
        filter_stores = request.args.get('filter_stores', '').strip()
        filter_assessors = request.args.get('filter_assessors', '').strip()
        min_age = request.args.get('min_age', '').strip()
        max_age = request.args.get('max_age', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        
        logger.debug("📊 学生档案API请求", extra_data={
            'page': page,
            'limit': limit,
            'search_name': search_name,
            'search_assessor': search_assessor,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'filter_stores': filter_stores,
            'filter_assessors': filter_assessors,
            'min_age': min_age,
            'max_age': max_age,
            'start_date': start_date,
            'end_date': end_date
        })
        
        # 加载和过滤档案
        all_profiles = load_student_profiles()
        profiles = filter_accessible_profiles(all_profiles, session.get('user_id', ''), session.get('user_store', ''))
        
        logger.info("📋 加载学生档案", extra_data={
            'total_profiles': len(all_profiles),
            'accessible_profiles': len(profiles)
        })
        
        # 搜索过滤
        if search_name:
            profiles = [p for p in profiles if search_name.lower() in p.get('name', '').lower()]
        
        if search_assessor:
            profiles = [p for p in profiles if search_assessor.lower() in p.get('assessor', '').lower()]
        
        # 训练中心筛选
        if filter_stores:
            selected_stores = [s.strip() for s in filter_stores.split(',') if s.strip()]
            if selected_stores:
                profiles = [p for p in profiles if p.get('training_center', '') in selected_stores]
        
        # 测评师筛选
        if filter_assessors:
            selected_assessors = [a.strip() for a in filter_assessors.split(',') if a.strip()]
            if selected_assessors:
                profiles = [p for p in profiles if p.get('assessor', '') in selected_assessors]
        
        # 年龄筛选
        if min_age:
            min_age_val = int(min_age) if min_age.isdigit() else 0
            profiles = [p for p in profiles if p.get('age', 0) >= min_age_val]
        
        if max_age:
            max_age_val = int(max_age) if max_age.isdigit() else 999
            if max_age_val == 10:  # "10岁以上"的特殊处理
                profiles = [p for p in profiles if p.get('age', 0) >= 10]
            else:
                profiles = [p for p in profiles if p.get('age', 0) <= max_age_val]
        
        # 时间段筛选
        if start_date:
            profiles = [p for p in profiles if p.get('test_date', '') >= start_date]
        
        if end_date:
            profiles = [p for p in profiles if p.get('test_date', '') <= end_date]
        
        # 排序
        reverse_order = sort_order == 'desc'
        if sort_by == 'age':
            profiles.sort(key=lambda x: x.get('age', 0), reverse=reverse_order)
        elif sort_by == 'test_date':
            profiles.sort(key=lambda x: x.get('test_date', ''), reverse=reverse_order)
        elif sort_by in ['name', 'training_center', 'assessor']:
            profiles.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse_order)
        
        # 分页
        total_count = len(profiles)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_profiles = profiles[start_idx:end_idx]
        
        # 处理数据格式
        processed_profiles = []
        
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
        
        for i, profile in enumerate(paginated_profiles):
            processed_profile = {
                'id': start_idx + i,
                'name': profile.get('name', ''),
                'age': profile.get('age', ''),
                'test_date': profile.get('test_date', ''),
                'training_center': profile.get('training_center', ''),
                'assessor': profile.get('assessor', '')
            }
            
            # 添加测评数据，使用字段映射处理新旧格式
            assessment_data = profile.get('assessment_data', {})
            for full_field, short_field in field_mapping.items():
                # 优先从新格式获取，如果没有则从旧格式获取
                value = assessment_data.get(full_field, profile.get(short_field, '-'))
                processed_profile[short_field] = value
            
            processed_profiles.append(processed_profile)
        
        # 获取可用的筛选选项
        available_stores = sorted(list(set(p.get('training_center', '') for p in profiles if p.get('training_center'))))
        available_assessors = sorted(list(set(p.get('assessor', '') for p in profiles if p.get('assessor'))))
        
        logger.info("✅ 学生档案API响应成功", extra_data={
            'returned_profiles': len(processed_profiles),
            'total_count': total_count,
            'page': page
        })
        
        return jsonify({
            'profiles': processed_profiles,
            'pagination': {
                'total_count': total_count,
                'page': page,
                'limit': limit,
                'pages': (total_count + limit - 1) // limit,
                'available_stores': available_stores,
                'available_assessors': available_assessors
            }
        })
        
    except Exception as e:
        logger.error("❌ 获取学生档案时出错", error=e)
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/view_student_profiles')
@teacher_required
def view_student_profiles():
    """查看学生档案页面"""
    return render_template('user_student_profiles.html')

@profiles_bp.route('/export')
@teacher_required
def export_profiles():
    """导出所有学生档案为CSV文件"""
    return _export_profiles_helper()

@profiles_bp.route('/export_selected')
@teacher_required  
def export_selected_profiles():
    """导出选中的学生档案"""
    return _export_profiles_helper(selected_only=True)

def _export_profiles_helper(selected_only=False):
    """导出档案的通用辅助函数"""
    try:
        all_profiles = load_student_profiles()
        profiles = filter_accessible_profiles(all_profiles, session.get('user_id', ''), session.get('user_store', ''))
        
        # 检查是否是下载筛选结果
        download_filtered = request.args.get('download_filtered', 'false').lower() == 'true'
        
        if download_filtered:
            # 应用与前端相同的筛选逻辑
            search_name = request.args.get('search_name', '').strip()
            filter_stores = request.args.get('filter_stores', '').strip()
            filter_assessors = request.args.get('filter_assessors', '').strip()
            min_age = request.args.get('min_age', '').strip()
            max_age = request.args.get('max_age', '').strip()
            start_date = request.args.get('start_date', '').strip()
            end_date = request.args.get('end_date', '').strip()
            
            # 应用筛选条件
            if search_name:
                profiles = [p for p in profiles if search_name.lower() in p.get('name', '').lower()]
            
            if filter_stores:
                selected_stores = [s.strip() for s in filter_stores.split(',') if s.strip()]
                if selected_stores:
                    profiles = [p for p in profiles if p.get('training_center', '') in selected_stores]
            
            if filter_assessors:
                selected_assessors = [a.strip() for a in filter_assessors.split(',') if a.strip()]
                if selected_assessors:
                    profiles = [p for p in profiles if p.get('assessor', '') in selected_assessors]
            
            if min_age:
                min_age_val = int(min_age) if min_age.isdigit() else 0
                profiles = [p for p in profiles if p.get('age', 0) >= min_age_val]
            
            if max_age:
                max_age_val = int(max_age) if max_age.isdigit() else 999
                if max_age_val == 10:
                    profiles = [p for p in profiles if p.get('age', 0) >= 10]
                else:
                    profiles = [p for p in profiles if p.get('age', 0) <= max_age_val]
            
            if start_date:
                profiles = [p for p in profiles if p.get('test_date', '') >= start_date]
            
            if end_date:
                profiles = [p for p in profiles if p.get('test_date', '') <= end_date]
            
            logger.info("📥 导出筛选结果", extra_data={
                'filtered_count': len(profiles),
                'filters': {
                    'search_name': search_name,
                    'filter_stores': filter_stores,
                    'filter_assessors': filter_assessors,
                    'min_age': min_age,
                    'max_age': max_age,
                    'start_date': start_date,
                    'end_date': end_date
                }
            })
            
        elif selected_only:
            # 获取选中的ID列表
            ids_param = request.args.get('ids', '')
            if not ids_param:
                flash('请先选择要导出的学生档案。', 'warning')
                return redirect(url_for('student.view_student_profiles'))
            
            selected_ids = [int(id_str.strip()) for id_str in ids_param.split(',') if id_str.strip().isdigit()]
            if not selected_ids:
                flash('未选择有效的学生档案。', 'warning')
                return redirect(url_for('student.view_student_profiles'))
            
            # 根据ID选择档案
            profiles = [profiles[idx] for idx in selected_ids if 0 <= idx < len(profiles)]
        
        if not profiles:
            flash('没有可导出的学生档案。', 'warning')
            return redirect(url_for('student.view_student_profiles'))
        
        # 创建CSV内容
        csv_content = create_csv_content(profiles)
        
        # 创建内存文件
        output = io.StringIO()
        output.write(csv_content)
        output.seek(0)
        
        byte_output = io.BytesIO()
        byte_output.write(output.getvalue().encode('utf-8-sig'))
        byte_output.seek(0)
        
        # 根据导出类型确定文件名
        if download_filtered:
            filename_prefix = 'filtered_profiles'
        elif selected_only:
            filename_prefix = 'selected_profiles'
        else:
            filename_prefix = 'student_profiles'
            
        return send_file(
            byte_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{filename_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        current_app.logger.error(f"导出学生档案时出错: {str(e)}")
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('student.view_student_profiles')) 