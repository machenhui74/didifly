from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import os
from datetime import datetime, timedelta
import sys
import json
import logging
from pathlib import Path
import zipfile
import io

# 导入我们创建的模块
from config import SOURCE_FOLDER, DESTINATION_FOLDER, DATA_FOLDER, STUDENT_PROFILES_FILE
from auth import login_required, admin_required, login_user, USERS
from users import add_user as add_user_func, update_user, delete_user as delete_user_func

# 学生档案数量限制
MAX_STUDENT_PROFILES = 100000  # 最大学生档案数量限制

# Add the parent directory to sys.path to import the required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cpbg.plan_generator import generate_plan
from cpbg.baogao4 import ReportGenerator
from cpbg.target_calculator import calculate_rating_and_target

app = Flask(__name__)

# 配置从环境变量读取，如果不存在则使用默认值
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(DATA_FOLDER, 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -----------------------------
# 学生档案数据管理函数
# -----------------------------

def load_student_profiles(limit=None, page=None):
    """
    加载学生档案数据
    
    参数:
        limit (int, 可选): 限制返回的档案数量，None表示不限制
        page (int, 可选): 分页页码，从1开始，与limit一起使用
    
    返回:
        list: 学生档案列表
    """
    if os.path.exists(STUDENT_PROFILES_FILE):
        try:
            with open(STUDENT_PROFILES_FILE, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
                
                # 如果设置了limit和page，进行分页处理
                if limit is not None and limit > 0:
                    # 默认页码为1
                    current_page = 1 if page is None or page < 1 else page
                    start_idx = (current_page - 1) * limit
                    end_idx = start_idx + limit
                    return profiles[start_idx:end_idx]
                
                return profiles
        except Exception as e:
            logger.error(f"加载学生档案数据时出错: {str(e)}")
    return []

def save_student_profiles(profiles):
    """保存学生档案数据"""
    try:
        with open(STUDENT_PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logger.error(f"保存学生档案数据时出错: {str(e)}")
        return False

def filter_accessible_profiles(all_profiles, user_id, user_store):
    """根据用户权限过滤可访问的学生档案"""
    if user_id == 'admin':
        return all_profiles
    else:
        if not user_store:
            return []
        return [profile for profile in all_profiles if profile.get('training_center', '') == user_store]

def create_csv_content(profiles):
    """根据学生档案列表创建CSV内容"""
    csv_content = "姓名,年龄,出生日期,测评日期,训练中心,测评师,视觉广度分数,视觉广度评级,视觉广度目标,视觉辨别分数,视觉辨别评级,视觉辨别目标,视动统合分数,视动统合评级,视动统合目标,视觉记忆分数,视觉记忆评级,视觉记忆目标,听觉广度分数,听觉广度评级,听觉广度目标,听觉分辨分数,听觉分辨评级,听觉分辨目标,听动统合分数,听动统合评级,听动统合目标,听觉记忆分数,听觉记忆评级,听觉记忆目标,提交人,提交时间\n"
    
    for profile in profiles:
        row = [
            profile.get('name', ''),
            str(profile.get('age', '')),
            profile.get('dob', ''),
            profile.get('test_date', ''),
            profile.get('training_center', ''),
            profile.get('assessor', ''),
            str(profile.get('vb', '')),
            profile.get('vb_current', ''),
            str(profile.get('vb_target', '')),
            str(profile.get('vd', '')),
            profile.get('vd_current', ''),
            str(profile.get('vd_target', '')),
            str(profile.get('vm', '')),
            profile.get('vm_current', ''),
            str(profile.get('vm_target', '')),
            str(profile.get('vm2', '')),
            profile.get('vm2_current', ''),
            str(profile.get('vm2_target', '')),
            str(profile.get('ab', '')),
            profile.get('ab_current', ''),
            str(profile.get('ab_target', '')),
            str(profile.get('ad', '')),
            profile.get('ad_current', ''),
            str(profile.get('ad_target', '')),
            str(profile.get('am', '')),
            profile.get('am_current', ''),
            str(profile.get('am_target', '')),
            str(profile.get('am2', '')),
            profile.get('am2_current', ''),
            str(profile.get('am2_target', '')),
            profile.get('submitted_by', ''),
            profile.get('submitted_at', '')
        ]
        # 处理CSV中的特殊字符
        csv_row = ','.join([f'"{str(item)}"' if ',' in str(item) else str(item) for item in row])
        csv_content += csv_row + "\n"
    
    return csv_content

# -----------------------------
# 路由
# -----------------------------

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data, success = login_user(username, password)
        
        if success:
            session['user_id'] = username
            session['user_name'] = user_data['name']
            session['user_store'] = user_data.get('store', '')
            session.permanent = True  # 设置会话为永久，以便 PERMANENT_SESSION_LIFETIME 生效
            flash(f'欢迎回来，{user_data["name"]}！', 'success')
            return redirect(url_for('index'))
        
        flash('账号或密码错误！', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    # 从session中获取用户门店
    user_store = session.get('user_store', '')
    user_name = session.get('user_name', '')
    user_id = session.get('user_id', '')
    
    # 管理员账号默认值设置
    if user_id == 'admin':
        user_store = '台州店'
        user_name = '马老师'
    
    # 获取当前日期（HTML5日期格式：YYYY-MM-DD）
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', user_store=user_store, user_name=user_name, user_id=user_id, current_date=current_date)

# 管理员后台管理页面
@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html', users=USERS)

# 添加用户
@app.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    new_username = request.form.get('new_username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    new_name = request.form.get('new_name', '').strip()
    new_store = request.form.get('new_store', '').strip()
    
    # 验证输入
    if not new_username or not new_password or not new_name:
        flash('所有字段都是必填的！', 'error')
        return redirect(url_for('admin'))
    
    # 调用 users.py 中的函数添加用户（包含密码验证）
    success, message = add_user_func(new_username, new_password, new_name, new_store)
    flash(message, 'success' if success else 'error')
    
    return redirect(url_for('admin'))

# 编辑用户
@app.route('/edit_user', methods=['POST'])
@admin_required
def edit_user():
    username = request.form.get('username', '').strip()
    new_password = request.form.get('new_password', '').strip()
    new_name = request.form.get('new_name', '').strip()
    new_store = request.form.get('new_store', '').strip()
    
    # 验证输入
    if not username or not new_name:
        flash('账号和用户名是必填的！', 'error')
        return redirect(url_for('admin'))
    
    # 调用 users.py 中的函数更新用户（包含密码验证）
    success, message = update_user(username, new_password, new_name, new_store)
    flash(message, 'success' if success else 'error')
    
    return redirect(url_for('admin'))

# 删除用户
@app.route('/delete_user', methods=['POST'])
@admin_required
def delete_user():
    username = request.form.get('username', '').strip()
    
    # 验证输入
    if not username:
        flash('账号是必填的！', 'error')
        return redirect(url_for('admin'))
    
    success, message = delete_user_func(username)
    flash(message, 'success' if success else 'error')
    
    return redirect(url_for('admin'))

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    try:
        # 获取表单数据
        name = request.form.get('name', '').strip()
        dob_str = request.form.get('dob', '')
        test_date_str = request.form.get('test_date', '')
        training_center = request.form.get('training_center', '').strip()
        assessor = request.form.get('assessor', '').strip()
        
        # 验证必填字段
        if not name or not dob_str or not test_date_str:
            flash('请填写所有必填字段！', 'error')
            return redirect(url_for('index'))
        
        # 解析日期
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            test_date = datetime.strptime(test_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('日期格式无效！', 'error')
            return redirect(url_for('index'))
        
        # 计算年龄
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        # 获取视觉测评数据
        try:
            vb = int(request.form.get('vb', '0'))
            vd = int(request.form.get('vd', '0'))
            vm = int(request.form.get('vm', '0'))
            vm2 = int(request.form.get('vm2', '0'))
        except ValueError:
            flash('请输入有效的视觉测评数据！', 'error')
            return redirect(url_for('index'))
        
        # 获取听力测评数据（可选）
        ab = ad = am = am2 = None
        try:
            if request.form.get('ab', ''):
                ab = int(request.form.get('ab'))
            if request.form.get('ad', ''):
                ad = int(request.form.get('ad'))
            if request.form.get('am', ''):
                am = int(request.form.get('am'))
            if request.form.get('am2', ''):
                am2 = int(request.form.get('am2'))
        except ValueError:
            flash('请输入有效的听力测评数据！', 'error')
            return redirect(url_for('index'))
        
        # 计算视觉能力当前评级及下阶段目标
        vb_current, vb_target, vb_target_eval = calculate_rating_and_target("visual_breadth", age, vb)
        vd_current, vd_target, vd_target_eval = calculate_rating_and_target("visual_discrimination", age, vd)
        vm_current, vm_target, vm_target_eval = calculate_rating_and_target("visuo_motor", age, vm)
        vm2_current, vm2_target, vm2_target_eval = calculate_rating_and_target("visual_memory", age, vm2)
        
        # 计算听力能力当前评级及下阶段目标（如果有数据）
        ab_current = ab_target = ab_target_eval = None
        ad_current = ad_target = ad_target_eval = None
        am_current = am_target = am_target_eval = None
        am2_current = am2_target = am2_target_eval = None
        
        if ab is not None:
            ab_current, ab_target, ab_target_eval = calculate_rating_and_target("auditory_breadth", age, ab)
        if ad is not None:
            ad_current, ad_target, ad_target_eval = calculate_rating_and_target("auditory_discrimination", age, ad)
        if am is not None:
            am_current, am_target, am_target_eval = calculate_rating_and_target("audio_motor", age, am)
        if am2 is not None:
            am2_current, am2_target, am2_target_eval = calculate_rating_and_target("auditory_memory", age, am2)
        
        child_ratings = {
            "visual_breadth": vb_current,
            "visual_discrimination": vd_current,
            "visuo_motor": vm_current,
            "visual_memory": vm2_current
        }
        
        # 添加听力能力评级（如果有）
        if ab is not None:
            child_ratings["auditory_breadth"] = ab_current
        if ad is not None:
            child_ratings["auditory_discrimination"] = ad_current
        if am is not None:
            child_ratings["audio_motor"] = am_current
        if am2 is not None:
            child_ratings["auditory_memory"] = am2_current
        
        # 生成训练方案
        folder_name = generate_plan(name, age, child_ratings, SOURCE_FOLDER, DESTINATION_FOLDER, weeks=1)
        
        # 生成测评报告
        ReportGenerator().generate_measurement_report(
            name, age, test_date,
            vb, vb_current, vb_target, vb_target_eval,
            vd, vd_current, vd_target, vd_target_eval,
            vm, vm_current, vm_target, vm_target_eval,
            vm2, vm2_current, vm2_target, vm2_target_eval,
            training_center, assessor,
            ab, ab_current, ab_target, ab_target_eval,
            ad, ad_current, ad_target, ad_target_eval,
            am, am_current, am_target, am_target_eval,
            am2, am2_current, am2_target, am2_target_eval
        )
        
        # 创建学生档案数据
        student_profile = {
            'name': name,
            'age': age,
            'dob': dob_str,
            'test_date': test_date_str,
            'training_center': training_center,
            'assessor': assessor,
            'submitted_by': session.get('user_id', ''),
            'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vb': vb,
            'vb_current': vb_current,
            'vb_target': vb_target,
            'vb_target_eval': vb_target_eval,
            'vd': vd,
            'vd_current': vd_current,
            'vd_target': vd_target,
            'vd_target_eval': vd_target_eval,
            'vm': vm,
            'vm_current': vm_current,
            'vm_target': vm_target,
            'vm_target_eval': vm_target_eval,
            'vm2': vm2,
            'vm2_current': vm2_current,
            'vm2_target': vm2_target,
            'vm2_target_eval': vm2_target_eval,
            'folder_name': folder_name  # 添加文件夹名称到档案
        }
        
        # 添加听力测评数据（如果有）
        if ab is not None:
            student_profile.update({
                'ab': ab,
                'ab_current': ab_current,
                'ab_target': ab_target,
                'ab_target_eval': ab_target_eval
            })
        
        if ad is not None:
            student_profile.update({
                'ad': ad,
                'ad_current': ad_current,
                'ad_target': ad_target,
                'ad_target_eval': ad_target_eval
            })
            
        if am is not None:
            student_profile.update({
                'am': am,
                'am_current': am_current,
                'am_target': am_target,
                'am_target_eval': am_target_eval
            })
            
        if am2 is not None:
            student_profile.update({
                'am2': am2,
                'am2_current': am2_current,
                'am2_target': am2_target,
                'am2_target_eval': am2_target_eval
            })
        
        # 保存学生档案到数据文件
        profiles = load_student_profiles()
        
        # 检查档案总数是否达到限制
        if len(profiles) >= MAX_STUDENT_PROFILES:
            logger.warning(f"学生档案数量已达到上限 {MAX_STUDENT_PROFILES}，无法添加新档案")
            flash(f'系统已达到最大学生档案数量限制（{MAX_STUDENT_PROFILES}条），请联系管理员处理。', 'error')
            return redirect(url_for('index'))
            
        profiles.append(student_profile)
        save_student_profiles(profiles)
        
        # 保存结果到会话，用于显示结果页面
        session['results'] = {
            'name': name,
            'age': age,
            'test_date': test_date_str,
            'vb': vb,
            'vb_current': vb_current,
            'vb_target': vb_target,
            'vb_target_eval': vb_target_eval,
            'vd': vd,
            'vd_current': vd_current,
            'vd_target': vd_target,
            'vd_target_eval': vd_target_eval,
            'vm': vm,
            'vm_current': vm_current,
            'vm_target': vm_target,
            'vm_target_eval': vm_target_eval,
            'vm2': vm2,
            'vm2_current': vm2_current,
            'vm2_target': vm2_target,
            'vm2_target_eval': vm2_target_eval,
            'training_center': training_center,
            'assessor': assessor
        }
        
        # 添加听力测评结果（如果有）
        if ab is not None:
            session['results']['ab'] = ab
            session['results']['ab_current'] = ab_current
            session['results']['ab_target'] = ab_target
            session['results']['ab_target_eval'] = ab_target_eval
        
        if ad is not None:
            session['results']['ad'] = ad
            session['results']['ad_current'] = ad_current
            session['results']['ad_target'] = ad_target
            session['results']['ad_target_eval'] = ad_target_eval
            
        if am is not None:
            session['results']['am'] = am
            session['results']['am_current'] = am_current
            session['results']['am_target'] = am_target
            session['results']['am_target_eval'] = am_target_eval
            
        if am2 is not None:
            session['results']['am2'] = am2
            session['results']['am2_current'] = am2_current
            session['results']['am2_target'] = am2_target
            session['results']['am2_target_eval'] = am2_target_eval
        
        flash('训练方案和测评报告生成成功！', 'success')
        return redirect(url_for('results'))
    
    except Exception as e:
        logger.error(f'生成过程中出现错误: {str(e)}')
        flash(f'生成过程中出现错误: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results')
@login_required
def results():
    if 'results' not in session:
        flash('请先提交表单！', 'error')
        return redirect(url_for('index'))
    
    return render_template('results.html', results=session['results'])

# 查看学生档案
@app.route('/student_profiles')
@login_required
def student_profiles():
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)  # 默认每页50条
    
    # 加载所有学生档案
    all_profiles = load_student_profiles()
    
    # 获取总记录数
    total_count = len(all_profiles)
    
    # 根据用户权限过滤可访问的学生档案
    user_id = session.get('user_id')
    user_store = session.get('user_store', '')
    accessible_profiles = filter_accessible_profiles(all_profiles, user_id, user_store)
    
    # 进行分页处理
    start_idx = (page - 1) * limit
    end_idx = min(start_idx + limit, len(accessible_profiles))
    paginated_profiles = accessible_profiles[start_idx:end_idx]
    
    # 返回分页数据和分页信息
    return jsonify({
        'profiles': paginated_profiles,
        'pagination': {
            'total': len(accessible_profiles),
            'page': page,
            'limit': limit,
            'pages': (len(accessible_profiles) + limit - 1) // limit
        }
    })

# 学生档案页面
@app.route('/view_student_profiles')
@login_required
def view_student_profiles():
    # 获取当前用户的门店信息
    user_store = session.get('user_store', '')
    return render_template('user_student_profiles.html', user_store=user_store)

# 统一的CSV导出函数
@app.route('/export_profiles')
@login_required
def export_profiles():
    """导出所有学生档案为CSV（仅管理员可用）"""
    # 判断用户权限
    if session.get('user_id') != 'admin':
        flash('您没有权限执行此操作！', 'error')
        return redirect(url_for('admin'))
    
    profiles = load_student_profiles()
    if not profiles:
        flash('没有可导出的学生档案！', 'error')
        return redirect(url_for('admin'))
    
    # 创建CSV内容
    csv_content = create_csv_content(profiles)
    
    # 创建响应
    response = app.response_class(
        response=csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=student_profiles.csv"}
    )
    return response

@app.route('/export_selected_profiles')
@login_required
def export_selected_profiles():
    """导出选中的学生档案为CSV"""
    # 加载所有学生档案
    all_profiles = load_student_profiles()
    
    # 根据用户权限过滤可访问的学生档案
    user_id = session.get('user_id')
    user_store = session.get('user_store', '')
    accessible_profiles = filter_accessible_profiles(all_profiles, user_id, user_store)
    
    if not accessible_profiles:
        flash('没有可导出的学生档案！', 'error')
        return redirect(url_for('admin' if user_id == 'admin' else 'view_student_profiles'))
    
    # 获取选中的档案ID
    selected_ids_str = request.args.get('ids', '')
    if not selected_ids_str:
        flash('未选择任何学生档案！', 'error')
        return redirect(url_for('admin' if user_id == 'admin' else 'view_student_profiles'))
    
    # 解析选中的ID并获取对应档案
    try:
        selected_profiles = []
        selected_ids = selected_ids_str.split(',')
        
        # 使用索引获取选中的档案
        for id_str in selected_ids:
            try:
                index = int(id_str)
                if 0 <= index < len(all_profiles) and all_profiles[index] in accessible_profiles:
                    selected_profiles.append(all_profiles[index])
            except (ValueError, IndexError):
                continue
    except Exception as e:
        logger.error(f'处理选中档案时出错: {str(e)}')
        flash(f'处理选中档案时出错: {str(e)}', 'error')
        return redirect(url_for('admin' if user_id == 'admin' else 'view_student_profiles'))
    
    if not selected_profiles:
        flash('未找到选中的学生档案！', 'error')
        return redirect(url_for('admin' if user_id == 'admin' else 'view_student_profiles'))
    
    # 创建CSV内容
    csv_content = create_csv_content(selected_profiles)
    
    # 创建响应
    filename = "selected_student_profiles.csv"
    if len(selected_profiles) == 1:
        filename = f"{selected_profiles[0].get('name', 'student')}_profile.csv"
    
    # 确保文件名是UTF-8编码
    filename = filename.encode('utf-8').decode('latin-1')
    
    response = app.response_class(
        response=csv_content,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
    return response

# 普通用户个人信息管理
@app.route('/user_profile')
@login_required
def user_profile():
    if session['user_id'] == 'admin':
        return redirect(url_for('admin'))
    
    username = session['user_id']
    name = session['user_name']
    store = session.get('user_store', '')
    
    return render_template('user_profile.html', username=username, name=name, store=store)

# 更新普通用户个人信息
@app.route('/update_user_profile', methods=['POST'])
@login_required
def update_user_profile():
    if session['user_id'] == 'admin':
        return redirect(url_for('admin'))
    
    username = session['user_id']
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # 非管理员用户只能修改密码，不能修改用户名和所属门店
    # 用原来的用户名，不从表单获取
    new_name = session['user_name']
    
    # 验证输入
    if not new_name:
        flash('用户名不能为空！', 'error')
        return redirect(url_for('user_profile'))
    
    # 验证密码
    if new_password:
        # 检查确认密码是否一致
        if new_password != confirm_password:
            flash('两次输入的密码不一致，请重新输入！', 'error')
            return redirect(url_for('user_profile'))
        
        # 使用users.py中的更新函数进行更新（包含密码验证）
        success, message = update_user(username, new_password, new_name)
    else:
        # 如果不更新密码，只更新其他信息
        success, message = update_user(username, None, new_name)
    
    if success:
        flash('个人信息更新成功！', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('user_profile'))

# -----------------------------
# 文件下载相关路由
# -----------------------------

@app.route('/download_report')
@login_required
def download_report():
    """下载测评报告"""
    try:
        if 'results' not in session:
            flash('请先提交表单！', 'error')
            return redirect(url_for('index'))
        
        # 获取学生姓名和测评日期
        name = session['results']['name']
        test_date = session['results']['test_date']
        
        # 构建测评报告文件路径
        report_folder = os.path.join(os.environ.get('OUTPUT_FOLDER', r"D:\备课系统\测评报告"), f"{name}测评记录")
        report_file = os.path.join(report_folder, f"{name}_{test_date}_测评报告.docx")
        
        if not os.path.exists(report_file):
            flash('测评报告文件不存在！', 'error')
            return redirect(url_for('results'))
        
        # 发送文件
        return send_file(report_file, as_attachment=True, download_name=f"{name}_{test_date}_测评报告.docx")
    
    except Exception as e:
        logger.error(f'下载测评报告时出错: {str(e)}')
        flash(f'下载测评报告时出错: {str(e)}', 'error')
        return redirect(url_for('results'))

@app.route('/download_plan', methods=['GET', 'POST'])
@login_required
def download_plan():
    """下载训练方案压缩包"""
    try:
        if 'results' not in session:
            flash('请先提交表单！', 'error')
            return redirect(url_for('index'))
        
        # 获取学生姓名和其他信息
        name = session['results']['name']
        age = session['results']['age']
        
        # 处理POST请求（用户选择了每周课程数）
        if request.method == 'POST':
            try:
                weeks = int(request.form.get('weeks', 1))
                if weeks < 1:
                    weeks = 1
            except ValueError:
                weeks = 1
            
            # 从session获取评级信息，重新生成训练方案
            child_ratings = {
                "visual_breadth": session['results']['vb_current'],
                "visual_discrimination": session['results']['vd_current'],
                "visuo_motor": session['results']['vm_current'],
                "visual_memory": session['results']['vm2_current']
            }
            
            # 添加听力能力评级（如果有）
            if 'ab_current' in session['results']:
                child_ratings["auditory_breadth"] = session['results']['ab_current']
            if 'ad_current' in session['results']:
                child_ratings["auditory_discrimination"] = session['results']['ad_current']
            if 'am_current' in session['results']:
                child_ratings["audio_motor"] = session['results']['am_current']
            if 'am2_current' in session['results']:
                child_ratings["auditory_memory"] = session['results']['am2_current']
            
            # 生成新的训练方案
            folder_name = generate_plan(name, age, child_ratings, SOURCE_FOLDER, DESTINATION_FOLDER, weeks=weeks)
            
            # 更新session中的文件夹名称
            session['results']['folder_name'] = folder_name
            
            # 训练方案文件夹路径
            plan_folder = os.path.join(DESTINATION_FOLDER, folder_name)
        else:
            # GET请求，渲染选择页面
            return render_template('select_weeks.html', name=name)
        
        # 处理文件下载
        if not os.path.exists(plan_folder):
            flash('训练方案文件夹不存在！', 'error')
            return redirect(url_for('results'))
        
        # 创建内存中的ZIP文件
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 递归添加文件夹中的所有文件
            for root, dirs, files in os.walk(plan_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(plan_folder))
                    zipf.write(file_path, arcname)
        
        # 重置文件指针
        memory_file.seek(0)
        
        # 发送ZIP文件
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{name}训练方案.zip"
        )
    
    except Exception as e:
        logger.error(f'下载训练方案时出错: {str(e)}')
        flash(f'下载训练方案时出错: {str(e)}', 'error')
        return redirect(url_for('results'))

if __name__ == '__main__':
    # 检测是否是生产环境
    is_production = os.environ.get('FLASK_ENV') == 'production'
    # 只在非生产环境启用调试模式
    app.run(debug=not is_production) 