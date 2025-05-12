import os
from docxtpl import DocxTemplate
import sys

# 添加web_app目录到系统路径以导入config
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web_app'))
from config import REPORT_OUTPUT_FOLDER, REPORT_TEMPLATE_PATH

class ReportGenerator:
    def __init__(self, output_folder=REPORT_OUTPUT_FOLDER):
        self.output_folder = output_folder
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
        template_path = REPORT_TEMPLATE_PATH

        # 使用 docxtpl 渲染模板
        doc = DocxTemplate(template_path)
        doc.render(data)
        doc.save(word_filename)
        print(f"Word报告已保存为 {word_filename}")

# 使用示例
if __name__ == "__main__":
    # 假设以下测试数据（请根据实际情况修改）
    report_gen = ReportGenerator()
    report_gen.generate_measurement_report(
        child_name="张三",
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
