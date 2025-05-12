import os

# 数据文件夹路径配置
SOURCE_FOLDER = os.environ.get('SOURCE_FOLDER', r"D:\23")
# 视觉训练资料位置
DESTINATION_FOLDER = os.environ.get('DESTINATION_FOLDER', r"D:\学员训练方案")
#学员训练方案文件夹配置
DATA_FOLDER = os.environ.get('DATA_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
USERS_FILE = os.path.join(DATA_FOLDER, 'users.json')
STUDENT_PROFILES_FILE = os.path.join(DATA_FOLDER, 'student_profiles.json')

# 报告模板和输出路径配置
REPORT_TEMPLATE_PATH = os.environ.get('REPORT_TEMPLATE_PATH', r"D:\备课系统\测试测评\测试报告.docx")
REPORT_OUTPUT_FOLDER = os.environ.get('REPORT_OUTPUT_FOLDER', r"D:\备课系统\测评报告")

# 确保必要的文件夹存在
for folder in [DATA_FOLDER, DESTINATION_FOLDER, REPORT_OUTPUT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True) 