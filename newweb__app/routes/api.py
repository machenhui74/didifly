# newweb__app/routes/api.py
"""
API相关路由
处理AJAX请求和RESTful API接口
"""

from flask import Blueprint, jsonify, request, current_app, session

from ..logic.auth import login_required, admin_required
from ..logic.tag_manager import get_visible_tags, get_all_tags, add_tag, update_tag_visibility, rename_tag

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/training_tags', methods=['GET'])
@login_required
def get_training_tags():
    """
    获取训练标签列表
    管理员可以看到所有标签，普通用户只能看到可见标签
    """
    try:
        is_admin = session.get('user_id') == 'admin'
        
        if is_admin:
            tags = get_all_tags()
            return jsonify({'success': True, 'tags': tags, 'is_admin': True})
        else:
            tags = get_visible_tags()
            return jsonify({'success': True, 'tags': tags, 'is_admin': False})
        
    except Exception as e:
        current_app.logger.error(f"获取训练标签时出错: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/training_tags/add', methods=['POST'])
@admin_required
def add_training_tag():
    """
    添加新的训练标签（仅管理员）
    """
    try:
        data = request.get_json()
        tag_name = data.get('tag_name', '').strip()
        
        if not tag_name:
            return jsonify({'success': False, 'message': '标签名称不能为空'})
        
        success = add_tag(tag_name)
        if success:
            return jsonify({'success': True, 'message': f"标签 '{tag_name}' 添加成功"})
        else:
            return jsonify({'success': False, 'message': f"标签 '{tag_name}' 已存在或添加失败"})
        
    except Exception as e:
        current_app.logger.error(f"添加训练标签时出错: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/training_tags/visibility', methods=['POST'])
@admin_required
def update_training_tag_visibility():
    """
    更新训练标签可见性（仅管理员）
    """
    try:
        data = request.get_json()
        tag_name = data.get('tag_name', '').strip()
        is_visible = data.get('visible', True)
        
        if not tag_name:
            return jsonify({'success': False, 'message': '标签名称不能为空'})
        
        success = update_tag_visibility(tag_name, is_visible)
        if success:
            status = "显示" if is_visible else "隐藏"
            return jsonify({'success': True, 'message': f"标签 '{tag_name}' 已{status}"})
        else:
            return jsonify({'success': False, 'message': f"标签 '{tag_name}' 不存在或更新失败"})
        
    except Exception as e:
        current_app.logger.error(f"更新标签可见性时出错: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/training_tags/rename', methods=['POST'])
@admin_required
def rename_training_tag():
    """
    重命名训练标签（仅管理员）
    """
    try:
        data = request.get_json()
        old_name = data.get('old_name', '').strip()
        new_name = data.get('new_name', '').strip()
        
        if not old_name or not new_name:
            return jsonify({'success': False, 'message': '标签名称不能为空'})
        
        success, message = rename_tag(old_name, new_name)
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        current_app.logger.error(f"重命名标签时出错: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500 