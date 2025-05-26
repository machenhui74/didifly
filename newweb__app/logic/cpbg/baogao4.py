import os
from docxtpl import DocxTemplate
import sys
from flask import current_app # 导入 current_app

# 添加web_app目录到系统路径以导入config
# sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web_app')) # TODO: 检查此导入的必要性和正确性
# from config import REPORT_OUTPUT_FOLDER, REPORT_TEMPLATE_PATH #移除直接导入

class ReportGenerator:
    def __init__(self):
        # 从 current_app.config 获取配置
        self.output_folder = current_app.config['REPORT_OUTPUT_FOLDER']
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def generate_measurement_report(self, child_name, child_age, measure_date,
                                    vb, vb_eval, vb_target, vb_target_eval,
                                    vd, vd_eval, vd_target, vd_target_eval,
                                    vm, vm_eval, vm_target, vm_target_eval,
                                    vm2, vm2_eval, vm2_target, vm2_target_eval,
                                    training_center, assessor,
                                    ab=None, ab_eval=None, ab_target=None, ab_target_eval=None,
                                    ad=None, ad_eval=None, ad_target=None, ad_target_eval=None,
                                    am=None, am_eval=None, am_target=None, am_target_eval=None,
                                    am2=None, am2_eval=None, am2_target=None, am2_target_eval=None):
        """
        生成测评报告并保存为 Word 格式，使用 docxtpl 模板库。
        新增听力测评参数：
        ab, ab_eval, ab_target, ab_target_eval: 听觉广度
        ad, ad_eval, ad_target, ad_target_eval: 听觉分辨
        am, am_eval, am_target, am_target_eval: 听动统合
        am2, am2_eval, am2_target, am2_target_eval: 听觉记忆
        """
        # 构造报告数据字典
        data = {
            "name": child_name,
            "age": child_age,
            # 如果 measure_date 为 datetime 对象，则使用 isoformat()，否则直接传入
            "date": measure_date.isoformat() if hasattr(measure_date, "isoformat") else measure_date,
            "visual_breadth": vb,
            "visual_breadth_eval": vb_eval,
            "visual_breadth_target": vb_target,
            "visual_breadth_target_eval": vb_target_eval,  # 模板中请使用例如 {{ rT_eval }} 占位符
            "visual_discrimination": vd,
            "visual_discrimination_eval": vd_eval,
            "visual_discrimination_target": vd_target,
            "visual_discrimination_target_eval": vd_target_eval,  # 模板中请使用例如 {{ tT_eval }} 占位符
            "visuo_motor": vm,
            "visuo_motor_eval": vm_eval,
            "visuo_motor_target": vm_target,
            "visuo_motor_target_eval": vm_target_eval,  # 模板中请使用例如 {{ uT_eval }} 占位符
            "visual_memory": vm2,
            "visual_memory_eval": vm2_eval,
            "visual_memory_target": vm2_target,
            "visual_memory_target_eval": vm2_target_eval,  # 模板中请使用例如 {{ yT_eval }} 占位符
            "training_center": training_center,
            "assessor": assessor,
        }
        
        # 添加听力测评数据（如果有）
        if ab is not None:
            data.update({
                "auditory_breadth": ab,
                "auditory_breadth_eval": ab_eval,
                "auditory_breadth_target": ab_target,
                "auditory_breadth_target_eval": ab_target_eval,
            })
        
        if ad is not None:
            data.update({
                "auditory_discrimination": ad,
                "auditory_discrimination_eval": ad_eval, 
                "auditory_discrimination_target": ad_target,
                "auditory_discrimination_target_eval": ad_target_eval,
            })
        
        if am is not None:
            data.update({
                "audio_motor": am,
                "audio_motor_eval": am_eval,
                "audio_motor_target": am_target,
                "audio_motor_target_eval": am_target_eval,
            })
        
        if am2 is not None:
            data.update({
                "auditory_memory": am2,
                "auditory_memory_eval": am2_eval,
                "auditory_memory_target": am2_target,
                "auditory_memory_target_eval": am2_target_eval,
            })

        # 创建文件夹：以"XXX测评记录"为名称
        folder_name = f"{child_name}测评记录"
        folder_path = os.path.join(self.output_folder, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 输出文件名（将文件保存在该文件夹内）
        word_filename = os.path.join(folder_path, f"{child_name}_{measure_date}_测评报告.docx")
        
        # 使用配置的模板路径
        # template_path = REPORT_TEMPLATE_PATH # 旧方式
        template_path = current_app.config['REPORT_TEMPLATE_PATH'] # 新方式

        # 使用 docxtpl 渲染模板
        doc = DocxTemplate(template_path)
        doc.render(data)
        doc.save(word_filename)
        print(f"Word报告已保存为 {word_filename}")

# 使用示例
if __name__ == "__main__":
    # 测试代码：使用环境变量配置而不是硬编码路径
    # 注意：此处的 __main__ 测试块在 Flask 应用上下文中可能无法直接使用 current_app
    # 需要在 Flask app 上下文中使用，或者将配置作为参数传递给 ReportGenerator
    
    # 获取配置路径（优先从环境变量，否则使用相对路径）
    import pathlib
    app_root = pathlib.Path(__file__).parent.parent.parent.absolute()
    
    test_report_output = os.environ.get('REPORT_OUTPUT_FOLDER', 
                                       str(app_root / 'data' / 'reports_test'))
    test_report_template = os.environ.get('REPORT_TEMPLATE_PATH',
                                         str(app_root / 'data' / 'templates' / 'test_report_template.docx'))
    
    class MockAppConfig:
        REPORT_OUTPUT_FOLDER = test_report_output
        REPORT_TEMPLATE_PATH = test_report_template

    class MockCurrentApp:
        config = MockAppConfig()
    
    # 模拟 current_app，仅用于本地测试此脚本
    # 在实际 Flask 应用中，current_app 会自动可用
    # global current_app 
    _original_current_app = current_app
    current_app = MockCurrentApp()

    # 确保测试目录存在
    os.makedirs(test_report_output, exist_ok=True)
    
    # 检查模板文件是否存在
    if not os.path.exists(test_report_template):
        print(f"⚠️  模板文件不存在: {test_report_template}")
        print("请确保模板文件存在，或者设置正确的 REPORT_TEMPLATE_PATH 环境变量")
    else:
        report_gen = ReportGenerator()
        report_gen.generate_measurement_report(
            child_name="张三测试",
            child_age=7,
            measure_date="2025-03-01",
            vb=300, vb_eval="不合格", vb_target=120, vb_target_eval="合格",
            vd=3, vd_eval="合格", vd_target=2, vd_target_eval="优秀",
            vm=16, vm_eval="合格", vm_target=18, vm_target_eval="优秀",
            vm2=1, vm2_eval="极差", vm2_target=3, vm2_target_eval="合格",
            training_center="XX训练中心",
            assessor="李老师",
            ab=6, ab_eval="不合格", ab_target=7, ab_target_eval="合格",
            ad=1, ad_eval="合格", ad_target=0, ad_target_eval="优秀",
            am=25, am_eval="不合格", am_target=29, am_target_eval="优秀",
            am2=2, am2_eval="不合格", am2_target=3, am2_target_eval="合格"
        )
        print("✅ 测试报告生成完成")
    
    current_app = _original_current_app # 恢复 current_app (如果之前有) 