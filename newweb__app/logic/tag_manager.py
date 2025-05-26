import json
import os
import logging
from flask import current_app

# 设置日志记录
logger = logging.getLogger(__name__)

# 默认标签列表
DEFAULT_TAGS = [
    '动态平衡', '静态平衡', '视动统合动作', '视觉屏蔽动作', '视觉记忆', '视觉抗干扰', 
    '空间感知', '视觉前庭整合训练', '听动统合动作', '听觉屏蔽动作', '听觉记忆', '听觉抗干扰', 
    '力量', '耐力', '手眼协调', '手脚协调', '双侧', '脚眼', '核心', '精细动作', 
    '触觉精进', '触觉脱敏', '复合二', '复合三', '复合四', '动作企划'
]

def get_tags_file_path():
    """获取标签配置文件路径"""
    data_folder = current_app.config.get('DATA_FOLDER', '')
    return os.path.join(data_folder, 'training_tags.json')

def load_tags():
    """加载标签配置
    
    Returns:
        dict: 包含所有标签和可见性的字典
    """
    tags_file = get_tags_file_path()
    
    # 如果文件不存在，则创建默认配置
    if not os.path.exists(tags_file):
        # 创建默认标签配置，所有标签默认可见
        default_config = {
            "tags": [{"name": tag, "visible": True} for tag in DEFAULT_TAGS]
        }
        save_tags(default_config)
        return default_config
    
    try:
        with open(tags_file, 'r', encoding='utf-8') as f:
            tag_config = json.load(f)
            # 验证格式
            if not isinstance(tag_config, dict) or "tags" not in tag_config:
                logger.warning(f"标签配置文件格式无效: {tags_file}")
                # 创建默认配置
                tag_config = {
                    "tags": [{"name": tag, "visible": True} for tag in DEFAULT_TAGS]
                }
                save_tags(tag_config)
            return tag_config
    except Exception as e:
        logger.error(f"加载标签配置失败: {str(e)}")
        # 返回默认配置
        default_config = {
            "tags": [{"name": tag, "visible": True} for tag in DEFAULT_TAGS]
        }
        return default_config

def save_tags(tag_config):
    """保存标签配置
    
    Args:
        tag_config (dict): 包含所有标签和可见性的字典
    
    Returns:
        bool: 保存是否成功
    """
    tags_file = get_tags_file_path()
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(tags_file), exist_ok=True)
        
        with open(tags_file, 'w', encoding='utf-8') as f:
            json.dump(tag_config, f, ensure_ascii=False, indent=2)
        logger.info(f"标签配置已保存: {tags_file}")
        return True
    except Exception as e:
        logger.error(f"保存标签配置失败: {str(e)}")
        return False

def get_visible_tags():
    """获取所有可见标签的名称列表
    
    Returns:
        list: 可见标签名称列表
    """
    tag_config = load_tags()
    visible_tags = [tag["name"] for tag in tag_config.get("tags", []) if tag.get("visible", True)]
    return visible_tags

def add_tag(tag_name):
    """添加新标签
    
    Args:
        tag_name (str): 标签名称
    
    Returns:
        bool: 操作是否成功
    """
    if not tag_name or not tag_name.strip():
        return False
    
    tag_name = tag_name.strip()
    tag_config = load_tags()
    
    # 检查标签是否已存在
    existing_tags = [tag["name"] for tag in tag_config.get("tags", [])]
    if tag_name in existing_tags:
        return False
    
    # 添加新标签
    tag_config["tags"].append({"name": tag_name, "visible": True})
    return save_tags(tag_config)

def update_tag_visibility(tag_name, visible):
    """更新标签可见性
    
    Args:
        tag_name (str): 标签名称
        visible (bool): 是否可见
    
    Returns:
        bool: 操作是否成功
    """
    tag_config = load_tags()
    
    # 查找并更新标签可见性
    for tag in tag_config.get("tags", []):
        if tag["name"] == tag_name:
            tag["visible"] = bool(visible)
            return save_tags(tag_config)
    
    return False

def rename_tag(old_name, new_name):
    """重命名标签
    
    Args:
        old_name (str): 原标签名称
        new_name (str): 新标签名称
    
    Returns:
        bool: 操作是否成功
    """
    if not old_name or not new_name or not old_name.strip() or not new_name.strip():
        return False, "标签名称不能为空"
    
    old_name = old_name.strip()
    new_name = new_name.strip()
    tag_config = load_tags()
    
    # 检查新名称是否已存在
    existing_tags = [tag["name"] for tag in tag_config.get("tags", [])]
    if new_name in existing_tags:
        return False, f"标签 '{new_name}' 已存在"
    
    # 查找并重命名标签
    found = False
    for tag in tag_config.get("tags", []):
        if tag["name"] == old_name:
            tag["name"] = new_name
            found = True
            break
    
    if not found:
        return False, f"未找到标签 '{old_name}'"
    
    success = save_tags(tag_config)
    if success:
        return True, f"标签已从 '{old_name}' 重命名为 '{new_name}'"
    else:
        return False, "保存标签配置失败"
    
def get_all_tags():
    """获取所有标签及其可见性状态
    
    Returns:
        list: 标签对象列表，每个包含name和visible属性
    """
    tag_config = load_tags()
    return tag_config.get("tags", []) 