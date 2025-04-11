import os
from docxtpl import DocxTemplate

OUTPUT_FOLDER = r"D:\备课系统\测评报告"  # 根据需要修改为存放生成报告的文件夹

class ReportGenerator:
    def __init__(self, output_folder=OUTPUT_FOLDER):
        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def generate_measurement_report(self, child_name, child_age, measure_date,
                                    vb, vb_eval, vb_target, vb_target_eval,
                                    vd, vd_eval, vd_target, vd_target_eval,
                                    vm, vm_eval, vm_target, vm_target_eval,
                                    vm2, vm2_eval, vm2_target, vm2_target_eval,
                                    training_center, assessor):
        """
        生成测评报告并保存为 Word 格式，使用 docxtpl 模板库。
        请确保你的 Word 模板中使用 Jinja2 占位符，如：
          - 姓名: {{ name }}
          - 年龄: {{ age }}
          - 日期: {{ date }}
          - 视觉广度: {{ visual_breadth }}
          - 视觉广度评估: {{ visual_breadth_eval }}
          - 视觉广度目标评分: {{ visual_breadth_target }} （新占位符）
          - 视觉广度目标评级: {{ rT_eval }} （新占位符）
          - 其他字段依此类推……
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

        # 创建文件夹：以"XXX测评记录"为名称
        folder_name = f"{child_name}测评记录"
        folder_path = os.path.join(self.output_folder, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # 输出文件名（将文件保存在该文件夹内）
        word_filename = os.path.join(folder_path, f"{child_name}_{measure_date}_测评报告.docx")
        template_path = r"D:\备课系统\测试测评\测试报告.docx"  # 模板文件路径，请根据实际情况修改

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
        assessor="李老师"
    )
