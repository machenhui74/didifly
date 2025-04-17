import os

# 数据文件夹路径配置
SOURCE_FOLDER = os.environ.get('SOURCE_FOLDER', r"D:\23")
DESTINATION_FOLDER = os.environ.get('DESTINATION_FOLDER', r"D:\学员训练方案")
DATA_FOLDER = os.environ.get('DATA_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')
STUDENT_PROFILES_FILE = os.path.join(DATA_FOLDER, 'student_profiles.json')

# 确保数据文件夹存在
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER) 