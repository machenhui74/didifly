# newweb__app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
import os
from datetime import datetime, timedelta
# import sys # sys.path manipulation is no longer needed here
import json
import logging
# from pathlib import Path # Not used directly in routes copied
import zipfile
import io
import shutil

# TODO: 从 .config 导入应用配置
# from .config import SOURCE_FOLDER, DESTINATION_FOLDER, DATA_FOLDER, STUDENT_PROFILES_FILE, MAX_STUDENT_PROFILES

# TODO: 从 .logic.auth 导入认证相关的函数和对象
from .logic.auth import login_required, admin_required, login_user as auth_login_user, USERS

# TODO: 从 .logic.users 导入用户管理函数
from .logic.users import add_user as add_user_func, update_user, delete_user as delete_user_func

# TODO: 从 .logic.student_utils 导入学生档案处理函数
from .logic.student_utils import load_student_profiles, save_student_profiles, filter_accessible_profiles, create_csv_content

# TODO: 从 .logic.cpbg.* 导入业务逻辑模块
from .logic.cpbg.plan_generator import generate_plan, generate_direct_plan
from .logic.cpbg.baogao4 import ReportGenerator
from .logic.cpbg.target_calculator import calculate_rating_and_target

# 导入训练方案生成器模块
from .logic.training_plan_generator import WebTrainingPlanGenerator

# 导入标签管理模块
from .logic.tag_manager import get_visible_tags, get_all_tags, add_tag, update_tag_visibility, rename_tag

# 创建一个 Blueprint
# 注意：这里的 'main' 可以是任何你选择的名字，它将用于在应用工厂中注册蓝图
# url_prefix 可以根据需要设置，例如 '/app'
main_bp = Blueprint('main', __name__)

# 使用 current_app.logger 代替局部 logger，或者在 __init__ 中配置好全局 logger
# logger = logging.getLogger(__name__) # 这也可以，但 current_app.logger 是推荐方式

# -----------------------------
# 路由
# -----------------------------

@main_bp.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('.index'))
    return redirect(url_for('.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data, success = auth_login_user(username, password) 
        
        if success:
            session['user_id'] = username
            session['user_name'] = user_data['name']
            session['user_store'] = user_data.get('store', '')
            session.permanent = True
            flash(f'欢迎回来，{user_data["name"]}！', 'success')
            return redirect(url_for('.index'))
        
        flash('账号或密码错误！', 'error')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功退出登录。', 'info')
    return redirect(url_for('.login'))

@main_bp.route('/index')
@login_required
def index():
    user_store = session.get('user_store', '')
    user_name = session.get('user_name', '')
    user_id = session.get('user_id', '')
    
    if user_id == 'admin':
        user_store = current_app.config.get('ADMIN_DEFAULT_STORE', '台州店') # 示例: 从配置获取
        user_name = current_app.config.get('ADMIN_DEFAULT_NAME', '马老师')  # 示例: 从配置获取
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', user_store=user_store, user_name=user_name, user_id=user_id, current_date=current_date)

@main_bp.route('/admin')
@admin_required
def admin():
    # USERS 是从 .logic.auth 导入的
    return render_template('admin.html', users=USERS) 

@main_bp.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    new_username = request.form.get('new_username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    new_name = request.form.get('new_name', '').strip()
    new_store = request.form.get('new_store', '').strip()
    
    if not new_username or not new_password or not new_name:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
            response = jsonify({'success': False, 'message': '所有字段都是必填的！', 'reset_form': False})
            response.status_code = 400  # 明确返回400状态码表示请求有问题
            return response
        flash('所有字段都是必填的！', 'error')
        return redirect(url_for('.admin'))
    
    success, message = add_user_func(new_username, new_password, new_name, new_store)
    
    # 如果是AJAX请求或请求期望JSON响应，返回JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
        # 添加reset_form字段，帮助前端判断是否需要重置表单状态
        if not success and "密码" in message:
            # 密码不符合要求的错误，保留用户输入的其他字段
            response = jsonify({'success': False, 'message': message, 'reset_form': False})
            response.status_code = 400
            return response
        response = jsonify({'success': success, 'message': message, 'reset_form': success})
        response.status_code = 200 if success else 400  # 成功返回200，失败返回400
        return response
    
    # 否则使用传统的表单提交响应
    flash(message, 'success' if success else 'error')
    return redirect(url_for('.admin'))

@main_bp.route('/edit_user', methods=['POST'])
@admin_required
def edit_user():
    username = request.form.get('username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    new_name = request.form.get('new_name', '').strip()
    new_store = request.form.get('new_store', '').strip()
    
    if not username or not new_name:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
            return jsonify({'success': False, 'message': '账号和用户名是必填的！', 'reset_form': False})
        flash('账号和用户名是必填的！', 'error')
        return redirect(url_for('.admin'))
    
    success, message = update_user(username, new_password, new_name, new_store)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
        if not success and "密码" in message:
            return jsonify({'success': False, 'message': message, 'reset_form': False})
        return jsonify({'success': success, 'message': message, 'reset_form': success})
    
    flash(message, 'success' if success else 'error')
    return redirect(url_for('.admin'))

@main_bp.route('/delete_user', methods=['POST'])
@admin_required
def delete_user():
    username = request.form.get('username', '').strip()
    
    if not username:
        flash('账号是必填的！', 'error')
        return redirect(url_for('.admin'))
    
    # 使用导入的 delete_user_func
    success, message = delete_user_func(username) 
    flash(message, 'success' if success else 'error')
    
    return redirect(url_for('.admin'))

@main_bp.route('/submit', methods=['POST'])
@login_required
def submit():
    try:
        name = request.form.get('name', '').strip()
        dob_str = request.form.get('dob', '')
        test_date_str = request.form.get('test_date', '')
        training_center = request.form.get('training_center', '').strip()
        assessor = request.form.get('assessor', '').strip()
        
        if not name or not dob_str or not test_date_str:
            flash('请填写所有必填字段！', 'error')
            return redirect(url_for('.index'))
        
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            test_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式无效！', 'error')
            return redirect(url_for('.index'))
        
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        try:
            vb = int(request.form.get('vb', '0'))
            vd = int(request.form.get('vd', '0'))
            vm = int(request.form.get('vm', '0'))
            vm2 = int(request.form.get('vm2', '0'))
        except ValueError:
            flash('请输入有效的视觉测评数据！', 'error')
            return redirect(url_for('.index'))
        
        ab = ad = am = am2 = None
        try:
            if request.form.get('ab', ''): ab = int(request.form.get('ab'))
            if request.form.get('ad', ''): ad = int(request.form.get('ad'))
            if request.form.get('am', ''): am = int(request.form.get('am'))
            if request.form.get('am2', ''): am2 = int(request.form.get('am2'))
        except ValueError:
            flash('请输入有效的听力测评数据！', 'error')
            return redirect(url_for('.index'))
        
        vb_current, vb_target, vb_target_eval = calculate_rating_and_target("visual_breadth", age, vb)
        vd_current, vd_target, vd_target_eval = calculate_rating_and_target("visual_discrimination", age, vd)
        vm_current, vm_target, vm_target_eval = calculate_rating_and_target("visuo_motor", age, vm)
        vm2_current, vm2_target, vm2_target_eval = calculate_rating_and_target("visual_memory", age, vm2)
        
        ab_current, ab_target, ab_target_eval = (None,) * 3
        ad_current, ad_target, ad_target_eval = (None,) * 3
        am_current, am_target, am_target_eval = (None,) * 3
        am2_current, am2_target, am2_target_eval = (None,) * 3
        
        if ab is not None: ab_current, ab_target, ab_target_eval = calculate_rating_and_target("auditory_breadth", age, ab)
        if ad is not None: ad_current, ad_target, ad_target_eval = calculate_rating_and_target("auditory_discrimination", age, ad)
        if am is not None: am_current, am_target, am_target_eval = calculate_rating_and_target("audio_motor", age, am)
        if am2 is not None: am2_current, am2_target, am2_target_eval = calculate_rating_and_target("auditory_memory", age, am2)
        
        child_ratings = {"visual_breadth": vb_current, "visual_discrimination": vd_current, "visuo_motor": vm_current, "visual_memory": vm2_current}
        if ab is not None: child_ratings["auditory_breadth"] = ab_current
        if ad is not None: child_ratings["auditory_discrimination"] = ad_current
        if am is not None: child_ratings["audio_motor"] = am_current
        if am2 is not None: child_ratings["auditory_memory"] = am2_current
        
        source_folder = current_app.config['SOURCE_FOLDER']
        destination_folder = current_app.config['DESTINATION_FOLDER']
        folder_name = generate_plan(name, age, child_ratings, source_folder, destination_folder, weeks=1)
        
        ReportGenerator().generate_measurement_report(
            name, age, test_date,
            vb, vb_current, vb_target, vb_target_eval, vd, vd_current, vd_target, vd_target_eval,
            vm, vm_current, vm_target, vm_target_eval, vm2, vm2_current, vm2_target, vm2_target_eval,
            training_center, assessor,
            ab, ab_current, ab_target, ab_target_eval, ad, ad_current, ad_target, ad_target_eval,
            am, am_current, am_target, am_target_eval, am2, am2_current, am2_target, am2_target_eval
        )
        
        student_profile = {
            'name': name, 'age': age, 'dob': dob_str, 'test_date': test_date_str,
            'training_center': training_center, 'assessor': assessor,
            'submitted_by': session.get('user_id', ''), 'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vb': vb, 'vb_current': vb_current, 'vb_target': vb_target, 'vb_target_eval': vb_target_eval,
            'vd': vd, 'vd_current': vd_current, 'vd_target': vd_target, 'vd_target_eval': vd_target_eval,
            'vm': vm, 'vm_current': vm_current, 'vm_target': vm_target, 'vm_target_eval': vm_target_eval,
            'vm2': vm2, 'vm2_current': vm2_current, 'vm2_target': vm2_target, 'vm2_target_eval': vm2_target_eval,
            'folder_name': folder_name
        }
        if ab is not None: student_profile.update({'ab': ab, 'ab_current': ab_current, 'ab_target': ab_target, 'ab_target_eval': ab_target_eval})
        if ad is not None: student_profile.update({'ad': ad, 'ad_current': ad_current, 'ad_target': ad_target, 'ad_target_eval': ad_target_eval})
        if am is not None: student_profile.update({'am': am, 'am_current': am_current, 'am_target': am_target, 'am_target_eval': am_target_eval})
        if am2 is not None: student_profile.update({'am2': am2, 'am2_current': am2_current, 'am2_target': am2_target, 'am2_target_eval': am2_target_eval})
        
        profiles = load_student_profiles() # From .logic.student_utils
        
        max_profiles = current_app.config.get('MAX_STUDENT_PROFILES', 100000) # 从配置获取
        if len(profiles) >= max_profiles:
            current_app.logger.warning(f"学生档案数量已达到上限 {max_profiles}，无法添加新档案")
            flash(f'系统已达到最大学生档案数量限制（{max_profiles}条），请联系管理员处理。', 'error')
            return redirect(url_for('.index'))
            
        profiles.append(student_profile)
        save_student_profiles(profiles) # From .logic.student_utils
        
        session['results'] = {
            'name': name, 'age': age, 'test_date': test_date_str,
            'vb': vb, 'vb_current': vb_current, 'vb_target': vb_target, 'vb_target_eval': vb_target_eval,
            'vd': vd, 'vd_current': vd_current, 'vd_target': vd_target, 'vd_target_eval': vd_target_eval,
            'vm': vm, 'vm_current': vm_current, 'vm_target': vm_target, 'vm_target_eval': vm_target_eval,
            'vm2': vm2, 'vm2_current': vm2_current, 'vm2_target': vm2_target, 'vm2_target_eval': vm2_target_eval,
            'training_center': training_center, 'assessor': assessor
        }
        if ab is not None: session['results'].update({'ab': ab, 'ab_current': ab_current, 'ab_target': ab_target, 'ab_target_eval': ab_target_eval})
        if ad is not None: session['results'].update({'ad': ad, 'ad_current': ad_current, 'ad_target': ad_target, 'ad_target_eval': ad_target_eval})
        if am is not None: session['results'].update({'am': am, 'am_current': am_current, 'am_target': am_target, 'am_target_eval': am_target_eval})
        if am2 is not None: session['results'].update({'am2': am2, 'am2_current': am2_current, 'am2_target': am2_target, 'am2_target_eval': am2_target_eval})
        
        flash('训练方案和测评报告生成成功！', 'success')
        return redirect(url_for('.results'))
    
    except Exception as e:
        current_app.logger.error(f'生成过程中出现错误: {str(e)}')
        flash(f'生成过程中出现错误: {str(e)}', 'error')
        return redirect(url_for('.index'))

@main_bp.route('/results')
@login_required
def results():
    if 'results' not in session:
        flash('请先提交表单！', 'error')
        return redirect(url_for('.index'))
    
    return render_template('results.html', results_data=session['results'])

@main_bp.route('/student_profiles')
@login_required
def student_profiles():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    search_term = request.args.get('search', '', type=str).strip().lower()
    sort_by = request.args.get('sort_by', 'name', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str).lower()
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'
    filter_stores_str = request.args.get('filter_stores', '', type=str) # Comma-separated store names

    all_profiles_raw = load_student_profiles()
    # Add original_index to each profile for stable ID across client-side operations (filtering, pagination, selection)
    all_profiles_indexed = []
    for i, p in enumerate(all_profiles_raw):
        p_copy = p.copy() # Avoid modifying cached/original data
        p_copy['original_index'] = i
        all_profiles_indexed.append(p_copy)

    user_id = session.get('user_id')
    user_store = session.get('user_store', '')
    accessible_profiles = filter_accessible_profiles(all_profiles_indexed, user_id, user_store)

    # Get unique store names from accessible profiles *before* any search or filter for the filter UI
    # This ensures the filter dropdown always shows all possible stores the user can access, not just currently displayed ones.
    available_stores_for_filter = sorted(list(set(p.get('training_center', '') for p in accessible_profiles if p.get('training_center'))))

    if search_term:
        current_profiles_list = [
            profile for profile in accessible_profiles
            if search_term in str(profile.get('name', '')).lower()
        ]
    else:
        current_profiles_list = accessible_profiles

    # Apply store filter if filter_stores_str is provided
    if filter_stores_str:
        selected_stores_for_filter = {s.strip() for s in filter_stores_str.split(',') if s.strip()}
        if selected_stores_for_filter: # Only filter if there are actual store names selected
            current_profiles_list = [
                profile for profile in current_profiles_list
                if profile.get('training_center', '') in selected_stores_for_filter
            ]

    # Apply sorting
    if sort_by in ['name', 'test_date', 'training_center', 'original_index']:
        # Added 'original_index' as a potential sort key if needed, e.g., for default load order.
        try:
            current_profiles_list.sort(key=lambda p: (p.get(sort_by, None) is None, p.get(sort_by, '')), 
                                   reverse=(sort_order == 'desc'))
        except TypeError: # Handle cases where mixed types might be an issue for None
            current_app.logger.warning(f"TypeError during sorting by {sort_by}. Fallback to unsorted or ensure consistent data types.")
            # Decide on a fallback, e.g., do not sort or sort by a default field like name
    
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, len(current_profiles_list))
    paginated_profiles = current_profiles_list[start_idx:end_idx] if start_idx < len(current_profiles_list) else []
    
    return jsonify({
        'profiles': paginated_profiles,
        'pagination': {
            'total': len(current_profiles_list), # total is based on the list after search and store filter
            'page': page, 'limit': limit,
            'pages': (len(current_profiles_list) + limit - 1) // limit if limit > 0 and len(current_profiles_list) > 0 else 0,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'available_stores': available_stores_for_filter # Add available stores for the filter UI
        }
    })

@main_bp.route('/view_student_profiles')
@login_required
def view_student_profiles():
    user_store = session.get('user_store', '')
    return render_template('user_student_profiles.html', user_store=user_store)

@main_bp.route('/export_profiles')
@login_required
def export_profiles():
    if session.get('user_id') != 'admin':
        flash('您没有权限执行此操作！', 'error')
        return redirect(url_for('.admin')) # Assuming admin route is at blueprint's root
    
    profiles = load_student_profiles()
    if not profiles:
        flash('没有可导出的学生档案！', 'error')
        return redirect(url_for('.admin'))
    
    csv_content = create_csv_content(profiles) # From .logic.student_utils
    
    response = current_app.response_class(
        response=csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=student_profiles.csv"}
    )
    return response

@main_bp.route('/export_selected_profiles')
@login_required
def export_selected_profiles():
    all_profiles_raw = load_student_profiles() # Get all profiles with their original data structure
    user_id = session.get('user_id')
    user_store = session.get('user_store', '')
    
    # We need a way to map unique IDs sent from client to profiles in all_profiles_raw.
    # Assuming each profile in all_profiles_raw has a unique 'id' field (e.g., uuid, or a simple counter if stable).
    # For this example, let's create a temporary mapping if `id` isn't naturally there, or assume it is.
    # If profiles don't have a stable unique ID, this part needs a robust solution.
    # For demonstration, let's assume profile has a field like `profile_unique_id` or we use its index if desperate.
    # To make this work, the /student_profiles endpoint must also return this same unique_id for each profile.

    # Create a dictionary for quick lookup by a presumed unique ID
    # This assumes `load_student_profiles` returns profiles that each have a unique `id` field.
    # If not, this is a placeholder for a more robust ID mechanism.
    # For now, if no `id` field, we might fall back to index, but this is fragile across sessions/data changes.
    # Let's ensure each profile in all_profiles_raw has an 'original_index' for this to work with the JS as last written
    all_profiles_with_original_index = []
    for i, p in enumerate(all_profiles_raw):
        p_copy = p.copy() # Avoid modifying the original data if it's cached or reused
        p_copy['original_index'] = i # This is the ID the JS part is currently set up to send
        all_profiles_with_original_index.append(p_copy)

    profile_map_by_original_index = {str(profile['original_index']): profile for profile in all_profiles_with_original_index}

    accessible_profiles_with_ids = filter_accessible_profiles(all_profiles_with_original_index, user_id, user_store)
    accessible_profile_original_indices = {str(p['original_index']) for p in accessible_profiles_with_ids}

    redirect_url = url_for('.view_student_profiles') # Default redirect
    if user_id == 'admin' and not accessible_profiles_with_ids: # Admin might expect to see all if none accessible otherwise
        redirect_url = url_for('.admin')

    if not accessible_profiles_with_ids:
        flash('没有可供您导出的学生档案！', 'error')
        return redirect(redirect_url)
    
    selected_ids_str = request.args.get('ids', '')
    if not selected_ids_str:
        flash('未选择任何学生档案！', 'error')
        return redirect(redirect_url)
    
    selected_profiles_to_export = []
    try:
        # These are expected to be the 'original_index' values from the JS
        selected_original_indices = selected_ids_str.split(',') 
        
        for original_idx_str in selected_original_indices:
            if original_idx_str in profile_map_by_original_index and original_idx_str in accessible_profile_original_indices:
                selected_profiles_to_export.append(profile_map_by_original_index[original_idx_str])
            else:
                current_app.logger.warning(f"Invalid or inaccessible profile original_index {original_idx_str} requested for export by user {user_id}.")
                
    except Exception as e:
        current_app.logger.error(f'处理选中档案进行导出时出错: {str(e)}')
        flash(f'处理选中档案进行导出时出错: {str(e)}', 'error')
        return redirect(redirect_url)
    
    if not selected_profiles_to_export:
        flash('未找到有效的选中学生档案进行导出！可能它们不再可访问或ID无效。', 'info') # Changed to info as it might not be an error
        return redirect(redirect_url)
    
    csv_content = create_csv_content(selected_profiles_to_export)
    
    filename = "selected_student_profiles.csv"
    if len(selected_profiles_to_export) == 1:
        filename = f"{selected_profiles_to_export[0].get('name', 'student')}_profile.csv"
    
    filename = filename.encode('utf-8').decode('latin-1') # For non-ASCII filenames
    
    response = current_app.response_class(
        response=csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
    return response

@main_bp.route('/user_profile')
@login_required
def user_profile():
    if session['user_id'] == 'admin':
        return redirect(url_for('.admin'))
    
    username = session['user_id']
    name = session['user_name']
    store = session.get('user_store', '')
    
    return render_template('user_profile.html', username=username, name=name, store=store)

@main_bp.route('/update_user_profile', methods=['POST'])
@login_required
def update_user_profile():
    if session['user_id'] == 'admin':
        return redirect(url_for('.admin')) # Should not happen if UI prevents
    
    username = session['user_id']
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    new_name = session['user_name'] # Name cannot be changed by non-admins from this form
    
    # store = session.get('user_store', '') # Store also not changeable here
    
    if new_password:
        if new_password != confirm_password:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
                return jsonify({'success': False, 'message': '两次输入的密码不一致，请重新输入！', 'reset_form': False})
            flash('两次输入的密码不一致，请重新输入！', 'error')
            return redirect(url_for('.user_profile'))
        success, message = update_user(username, new_password, new_name) # Store not passed
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
            if not success and "密码" in message:
                return jsonify({'success': False, 'message': message, 'reset_form': False})
            return jsonify({'success': success, 'message': message, 'reset_form': success})
    else:
        # If password is not changed, no need to call update_user unless other fields were changeable
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type and 'json' in request.content_type:
            return jsonify({'success': False, 'message': '未提供新密码，个人信息未更新。', 'reset_form': False})
        flash('未提供新密码，个人信息未更新。', 'info')
        return redirect(url_for('.user_profile'))

    if success:
        flash('个人信息更新成功！', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('.user_profile'))

@main_bp.route('/download_report')
@login_required
def download_report():
    try:
        if 'results' not in session:
            flash('请先提交表单！', 'error')
            return redirect(url_for('.index'))
        
        name = session['results']['name']
        test_date = session['results']['test_date']
        
        report_output_folder = current_app.config['REPORT_OUTPUT_FOLDER']
        # The original used os.environ.get directly here, now it's from config
        # report_folder = os.path.join(os.environ.get('OUTPUT_FOLDER', r"D:\备课系统\测评报告"), f"{name}测评记录")
        report_folder = os.path.join(report_output_folder, f"{name}测评记录")
        report_file = os.path.join(report_folder, f"{name}_{test_date}_测评报告.docx")
        
        if not os.path.exists(report_file):
            flash('测评报告文件不存在！', 'error')
            current_app.logger.error(f"Report file not found: {report_file}")
            return redirect(url_for('.results'))
        
        return send_file(report_file, as_attachment=True, download_name=f"{name}_{test_date}_测评报告.docx")
    
    except Exception as e:
        current_app.logger.error(f'下载测评报告时出错: {str(e)}')
        flash(f'下载测评报告时出错: {str(e)}', 'error')
        return redirect(url_for('.results'))

@main_bp.route('/direct_plan')
@login_required
def direct_plan():
    """无测评直接生成训练方案页面"""
    return render_template('direct_plan.html')

@main_bp.route('/process_direct_plan', methods=['POST'])
@login_required
def process_direct_plan():
    """处理无测评直接生成训练方案的表单数据"""
    try:
        # 获取表单数据
        name = request.form.get('child_name', '').strip()
        age = int(request.form.get('child_age', 0))
        
        # 获取选择的训练难度级别
        visual_breadth = request.form.get('visual_breadth')
        visual_discrimination = request.form.get('visual_discrimination')
        visuo_motor = request.form.get('visuo_motor')
        visual_memory = request.form.get('visual_memory')
        
        # 验证输入
        if not name or age < 4 or age > 12:
            flash('请填写有效的姓名和年龄信息(4-12岁)', 'error')
            return redirect(url_for('.direct_plan'))
        
        if not visual_breadth or not visual_discrimination or not visuo_motor or not visual_memory:
            flash('请为每个训练项目选择难度级别', 'error')
            return redirect(url_for('.direct_plan'))
        
        # 创建一个特殊的结果对象，存储在session中供download_plan使用
        session['results'] = {
            'name': name,
            'age': age,
            # 将选择的难度级别存储为相应的评级
            'vb_current': '用户选择',  # 这些值不会被实际使用，因为我们会覆盖下面的target_difficulties
            'vd_current': '用户选择',
            'vm_current': '用户选择',
            'vm2_current': '用户选择',
            # 存储实际选择的难度级别
            'direct_plan': True,
            'target_difficulties': {
                'visual_breadth': visual_breadth,
                'visual_discrimination': visual_discrimination,
                'visuo_motor': visuo_motor,
                'visual_memory': visual_memory
            }
        }
        
        # 重定向到选择周数页面
        return render_template('select_weeks.html', name=name)
        
    except Exception as e:
        current_app.logger.error(f'处理无测评训练方案请求时出错: {str(e)}')
        flash(f'处理请求时出错: {str(e)}', 'error')
        return redirect(url_for('.direct_plan'))

@main_bp.route('/download_plan', methods=['GET', 'POST'])
@login_required
def download_plan():
    try:
        if 'results' not in session:
            flash('请先提交表单！', 'error')
            return redirect(url_for('.index'))
        
        name = session['results']['name']
        age = session['results']['age']
        
        source_folder = current_app.config['SOURCE_FOLDER']
        destination_folder = current_app.config['DESTINATION_FOLDER']
            
        if request.method == 'POST':
            try:
                weeks = int(request.form.get('weeks', 1))
                if weeks < 1: weeks = 1
            except ValueError:
                weeks = 1
            
            # 检查是否为直接生成方案的请求
            if session['results'].get('direct_plan', False):
                # 使用用户直接选择的难度级别
                target_difficulties = session['results']['target_difficulties']
                
                # 为每个训练类别创建一个虚拟的评级
                child_ratings = {
                    "visual_breadth": "合格",
                    "visual_discrimination": "合格",
                    "visuo_motor": "合格",
                    "visual_memory": "合格"
                }
                
                # 创建一个修改后的generate_plan函数
                folder_name = generate_direct_plan(
                    name, age, child_ratings, 
                    target_difficulties, 
                    source_folder, destination_folder, 
                    weeks=weeks
                )
            else:
                # 原有的基于测评结果的生成方式
                child_ratings = {
                    "visual_breadth": session['results']['vb_current'],
                    "visual_discrimination": session['results']['vd_current'],
                    "visuo_motor": session['results']['vm_current'],
                    "visual_memory": session['results']['vm2_current']
                }
                if 'ab_current' in session['results']: child_ratings["auditory_breadth"] = session['results']['ab_current']
                if 'ad_current' in session['results']: child_ratings["auditory_discrimination"] = session['results']['ad_current']
                if 'am_current' in session['results']: child_ratings["audio_motor"] = session['results']['am_current']
                if 'am2_current' in session['results']: child_ratings["auditory_memory"] = session['results']['am2_current']
                
                folder_name = generate_plan(name, age, child_ratings, source_folder, destination_folder, weeks=weeks)
            
            session['results']['folder_name'] = folder_name # Update session
            plan_folder_path = os.path.join(destination_folder, folder_name)
        else: # GET request
            return render_template('select_weeks.html', name=name) # This template needs to be created
        
        # 原有的返回文件逻辑保持不变
        if not os.path.exists(plan_folder_path):
            flash('训练方案文件夹不存在！', 'error')
            current_app.logger.error(f"Plan folder not found: {plan_folder_path}")
            return redirect(url_for('.results'))
        
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(plan_folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(plan_folder_path))
                    zipf.write(file_path, arcname)
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{name}训练方案.zip"
        )
    
    except Exception as e:
        current_app.logger.error(f'下载训练方案时出错: {str(e)}')
        flash(f'下载训练方案时出错: {str(e)}', 'error')
        return redirect(url_for('.results'))

@main_bp.route('/training_plan')
@login_required
def training_plan():
    """感统备课训练方案生成页面"""
    is_admin = session.get('user_id') == 'admin'
    return render_template('training_plan.html', is_admin=is_admin)

@main_bp.route('/api/training_tags', methods=['GET'])
@login_required
def get_training_tags():
    """获取训练标签API"""
    is_admin = session.get('user_id') == 'admin'
    
    if is_admin:
        # 管理员可以看到所有标签及其可见性
        tags = get_all_tags()
        return jsonify({"tags": tags, "is_admin": True})
    else:
        # 普通用户只能看到可见标签
        visible_tags = get_visible_tags()
        return jsonify({"tags": visible_tags, "is_admin": False})

@main_bp.route('/api/training_tags/add', methods=['POST'])
@admin_required
def add_training_tag():
    """添加新训练标签API (仅管理员)"""
    tag_name = request.json.get('tag_name', '').strip()
    
    if not tag_name:
        return jsonify({"success": False, "message": "标签名称不能为空"}), 400
    
    success = add_tag(tag_name)
    
    if success:
        return jsonify({"success": True, "message": f"标签 '{tag_name}' 添加成功"})
    else:
        return jsonify({"success": False, "message": f"标签 '{tag_name}' 已存在或添加失败"}), 400

@main_bp.route('/api/training_tags/visibility', methods=['POST'])
@admin_required
def update_training_tag_visibility():
    """更新标签可见性API (仅管理员)"""
    tag_name = request.json.get('tag_name', '').strip()
    visible = request.json.get('visible', True)
    
    if not tag_name:
        return jsonify({"success": False, "message": "标签名称不能为空"}), 400
    
    success = update_tag_visibility(tag_name, visible)
    
    if success:
        status = "显示" if visible else "隐藏"
        return jsonify({"success": True, "message": f"标签 '{tag_name}' 已{status}"})
    else:
        return jsonify({"success": False, "message": f"标签 '{tag_name}' 不存在或更新失败"}), 400

@main_bp.route('/api/training_tags/rename', methods=['POST'])
@admin_required
def rename_training_tag():
    """重命名标签API (仅管理员)"""
    old_name = request.json.get('old_name', '').strip()
    new_name = request.json.get('new_name', '').strip()
    
    if not old_name or not new_name:
        return jsonify({"success": False, "message": "原标签名和新标签名都不能为空"}), 400
    
    success, message = rename_tag(old_name, new_name)
    
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 400

@main_bp.route('/generate_training_plan', methods=['POST'])
@login_required
def generate_training_plan():
    """生成训练方案处理"""
    try:
        # 获取表单数据
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '').strip()
        selected_tags_json = request.form.get('selected_tags', '[]')
        
        # 验证输入
        if not name or not age or not age.isdigit():
            flash('请填写有效的姓名和年龄信息', 'error')
            return redirect(url_for('.training_plan'))
        
        try:
            selected_tags = json.loads(selected_tags_json)
            if not selected_tags:
                flash('请至少选择一个训练标签', 'error')
                return redirect(url_for('.training_plan'))
        except json.JSONDecodeError:
            flash('标签数据格式错误', 'error')
            return redirect(url_for('.training_plan'))
        
        # 获取动作库路径
        action_db_path = current_app.config.get('TRAINING_ACTION_DB_PATH')
        
        # 检查动作库文件是否存在，如果不存在则复制原始文件
        if not os.path.exists(action_db_path):
            # 确保目录存在
            os.makedirs(os.path.dirname(action_db_path), exist_ok=True)
            
            # 获取原始动作库路径
            original_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                          '训练方案生成器', 'action_database.xlsx')
            
            if os.path.exists(original_db_path):
                # 复制文件
                shutil.copy2(original_db_path, action_db_path)
                current_app.logger.info(f"已从 {original_db_path} 复制动作库到 {action_db_path}")
            else:
                flash('动作库文件不存在，请联系管理员', 'error')
                current_app.logger.error(f"无法找到原始动作库文件: {original_db_path}")
                return redirect(url_for('.training_plan'))
        
        # 创建训练方案生成器实例并生成方案
        generator = WebTrainingPlanGenerator()
        doc_data, error_msg = generator.generate_training_plan(name, age, selected_tags, action_db_path)
        
        if error_msg:
            flash(f'生成训练方案失败: {error_msg}', 'error')
            return redirect(url_for('.training_plan'))
        
        if not doc_data:
            flash('生成训练方案失败，未返回有效数据', 'error')
            return redirect(url_for('.training_plan'))
        
        # 为文件命名
        filename = f"{name}_{age}岁_训练方案_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
        
        # 创建内存中的文件流并返回
        document_stream = io.BytesIO(doc_data)
        document_stream.seek(0)
        
        # 设置响应头，让浏览器下载文件
        return send_file(
            document_stream,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.exception(f"生成训练方案时发生错误: {str(e)}")
        flash(f'生成训练方案时发生错误: {str(e)}', 'error')
        return redirect(url_for('.training_plan'))

# The __main__ block from old app.py is not needed here as app is run via factory. 