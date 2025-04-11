import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.font as tkFont
from ttkbootstrap.dialogs import DatePickerDialog
from plan_generator import generate_plan
from datetime import datetime
from baogao4 import ReportGenerator
from target_calculator import calculate_rating_and_target
import tkinter.messagebox

#默认全屏打开的
# 数据文件夹路径
SOURCE_FOLDER, DESTINATION_FOLDER = r"D:\23", r"D:\学员训练方案"


class BetterDateEntry(ttk.Frame):
    """更可靠的日期选择控件：使用ttkbootstrap内置的DatePickerDialog"""

    def __init__(self, master, date_pattern='%Y-%m-%d', font=None, **kwargs):
        super().__init__(master, **kwargs)
        self.date_pattern = date_pattern
        self.var = tk.StringVar(value=datetime.now().strftime(date_pattern))
        self.entry = ttk.Entry(self, textvariable=self.var, width=20, bootstyle="primary")
        if font: self.entry.configure(font=font)
        self.entry.pack(side=LEFT, fill=X, expand=True)
        self.button = ttk.Button(self, text="📅", command=self._show_calendar, bootstyle="primary-outline")
        self.button.pack(side=LEFT, padx=5)

    def _show_calendar(self):
        try:
            current_date = datetime.strptime(self.var.get(),
                                             self.date_pattern).date() if self.var.get() else datetime.now().date()
        except ValueError:
            current_date = datetime.now().date()
        try:
            date_dialog = DatePickerDialog(parent=self, title="选择日期", firstweekday=6, bootstyle="primary")
            selected_date = date_dialog.date_selected
            if selected_date: self.var.set(selected_date.strftime(self.date_pattern))
        except Exception as e:
            print(f"创建日历错误: {e}")

    def get_date(self):
        date_str = self.var.get().strip()
        if not date_str: return None
        try:
            return datetime.strptime(date_str, self.date_pattern).date()
        except ValueError:
            return None


class TrainingApp:
    def __init__(self, master):
        self.master = master
        # 创建字体
        self.title_font = tkFont.Font(family="Microsoft YaHei", size=24, weight="bold")
        self.header_font = tkFont.Font(family="Microsoft YaHei", size=18, weight="bold")
        self.input_font = tkFont.Font(family="Microsoft YaHei", size=14)
        self.button_font = tkFont.Font(family="Microsoft YaHei", size=16, weight="bold")
        # 配置主题样式
        style = ttk.Style()
        style.configure("TLabel", font=self.input_font)
        style.configure("TEntry", font=self.input_font)
        style.configure("TButton", font=self.button_font)
        style.configure("Title.TLabel", font=self.title_font, foreground="#4FB0C6")
        style.configure("Header.TLabel", font=self.header_font, foreground="#4FB0C6")
        # 创建UI
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """设置基本布局，确保绝对居中"""
        self.main_frame = ttk.Frame(self.master, padding=20)
        self.main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    def _create_widgets(self):
        """创建UI组件"""
        # 创建标题
        ttk.Label(self.main_frame, text="小马达训练方案生成系统", style="Title.TLabel",
                  foreground="#4FB0C6").pack(pady=(0, 20))

        # 创建选项卡
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 添加选项卡页面
        info_frame = ttk.Frame(self.notebook, padding=20)
        eval_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(info_frame, text="基本信息")
        self.notebook.add(eval_frame, text="测评数据")

        # 个人信息区域
        personal_info_frame = ttk.LabelFrame(info_frame, text="个人信息", padding=15, bootstyle="info")
        personal_info_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 姓名输入
        ttk.Label(personal_info_frame, text="姓名：").grid(row=0, column=0, sticky=W, pady=15, padx=15)
        self.name_entry = ttk.Entry(personal_info_frame, width=25, bootstyle="info")
        self.name_entry.grid(row=0, column=1, pady=15, padx=15, sticky=(W, E))

        # 出生日期
        ttk.Label(personal_info_frame, text="出生日期：").grid(row=1, column=0, sticky=W, pady=15, padx=15)
        self.dob_entry = BetterDateEntry(personal_info_frame, date_pattern='%Y-%m-%d', font=self.input_font)
        self.dob_entry.grid(row=1, column=1, pady=15, padx=15, sticky=(W, E))

        # 测评日期
        ttk.Label(personal_info_frame, text="测评日期：").grid(row=2, column=0, sticky=W, pady=15, padx=15)
        self.test_date_entry = BetterDateEntry(personal_info_frame, date_pattern='%Y-%m-%d', font=self.input_font)
        self.test_date_entry.grid(row=2, column=1, pady=15, padx=15, sticky=(W, E))

        # 测评机构信息
        center_frame = ttk.LabelFrame(info_frame, text="测评机构信息", padding=15, bootstyle="info")
        center_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 训练中心输入
        ttk.Label(center_frame, text="训练中心：").grid(row=0, column=0, sticky=W, pady=15, padx=15)
        self.training_center_entry = ttk.Entry(center_frame, width=25, bootstyle="info")
        self.training_center_entry.grid(row=0, column=1, pady=15, padx=15, sticky=(W, E))

        # 测评师输入
        ttk.Label(center_frame, text="测评师：").grid(row=1, column=0, sticky=W, pady=15, padx=15)
        self.assessor_entry = ttk.Entry(center_frame, width=25, bootstyle="info")
        self.assessor_entry.grid(row=1, column=1, pady=15, padx=15, sticky=(W, E))

        # 测评数据页面
        ttk.Label(eval_frame, text="视觉能力测评数据", style="Header.TLabel").pack(pady=(0, 15), anchor=W)

        # 视觉测评数据输入
        visual_frame = ttk.LabelFrame(eval_frame, text="视觉能力测评", padding=15, bootstyle="info")
        visual_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 测评项说明
        descriptions = [
            "视觉广度测试：评估儿童同时处理多个视觉信息的能力",
            "视觉辨别测试：评估儿童区分相似视觉图形的能力",
            "视动统合测试：评估儿童眼手协调能力",
            "视觉记忆测试：评估儿童短期视觉记忆能力"
        ]

        # 测评数据输入项
        self.vb_entry = self._create_input_field(visual_frame, "视觉广度时间（秒）：", 0, descriptions[0])
        self.vd_entry = self._create_input_field(visual_frame, "视觉辨别丢漏个数：", 1, descriptions[1])
        self.vm_entry = self._create_input_field(visual_frame, "视动统合分数：", 2, descriptions[2])
        self.vm2_entry = self._create_input_field(visual_frame, "视觉记忆分数：", 3, descriptions[3])

        # 底部按钮区域
        button_frame = ttk.Frame(self.main_frame, padding=10)
        button_frame.pack(fill=X, pady=20)

        # 按钮
        ttk.Button(button_frame, text="重置表单", command=self.reset_form,
                   bootstyle="secondary", width=20).pack(side=LEFT, padx=10)
        ttk.Button(button_frame, text="生成训练方案", command=self.on_submit,
                   bootstyle="info", width=20).pack(side=RIGHT, padx=10)

        # 状态栏
        self.status_var = tk.StringVar(value="系统就绪，请填写信息...")
        ttk.Label(self.main_frame, textvariable=self.status_var,
                  relief=tk.SUNKEN, anchor=W).pack(side=BOTTOM, fill=X, pady=(10, 0))

    def _create_input_field(self, parent, label, row, description):
        """创建输入字段辅助函数"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=W, pady=12, padx=12)
        entry = ttk.Entry(parent, width=15, bootstyle="info")
        entry.grid(row=row, column=1, pady=12, padx=12, sticky=W)
        ttk.Label(parent, text=description, foreground="#666666",
                  font=("Microsoft YaHei", 10)).grid(row=row, column=2, sticky=W, pady=12, padx=12)
        return entry

    def reset_form(self):
        """重置所有表单字段"""
        self.name_entry.delete(0, tk.END)
        # 重置日期为今天
        today = datetime.now().strftime('%Y-%m-%d')
        self.dob_entry.var.set(today)
        self.test_date_entry.var.set(today)
        self.training_center_entry.delete(0, tk.END)
        self.assessor_entry.delete(0, tk.END)
        self.vb_entry.delete(0, tk.END)
        self.vd_entry.delete(0, tk.END)
        self.vm_entry.delete(0, tk.END)
        self.vm2_entry.delete(0, tk.END)
        self.status_var.set("表单已重置")

    def _calculate_age(self, dob):
        """计算年龄"""
        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d")
            today = datetime.today()
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except Exception as e:
            print(f"计算年龄错误: {e}")
            return None

    def on_submit(self):
        """提交表单，生成训练方案"""
        # 更新状态
        self.status_var.set("正在处理...")
        self.master.update()

        # 获取并验证输入数据
        name = self.name_entry.get().strip()
        dob = self.dob_entry.get_date()
        test_date = self.test_date_entry.get_date()

        # 验证必填字段
        if not name or dob is None or test_date is None:
            tk.messagebox.showerror("错误", "请填写所有必填字段！")
            self.status_var.set("系统就绪，请填写信息...")
            return

        # 计算年龄并验证数据
        try:
            age = self._calculate_age(dob.strftime("%Y-%m-%d"))
            if age is None: raise ValueError("无法计算年龄")
            vb, vd, vm, vm2 = [int(entry.get().strip()) for entry in
                               [self.vb_entry, self.vd_entry, self.vm_entry, self.vm2_entry]]
        except ValueError:
            tk.messagebox.showerror("错误", "请输入有效的测评数据！")
            self.status_var.set("系统就绪，请填写信息...")
            return

        training_center = self.training_center_entry.get().strip()
        assessor = self.assessor_entry.get().strip()

        # 计算当前评级及下阶段目标
        vb_current, vb_target, vb_target_eval = calculate_rating_and_target("visual_breadth", age, vb)
        vd_current, vd_target, vd_target_eval = calculate_rating_and_target("visual_discrimination", age, vd)
        vm_current, vm_target, vm_target_eval = calculate_rating_and_target("visuo_motor", age, vm)
        vm2_current, vm2_target, vm2_target_eval = calculate_rating_and_target("visual_memory", age, vm2)

        child_ratings = {
            "visual_breadth": vb_current,
            "visual_discrimination": vd_current,
            "visuo_motor": vm_current,
            "visual_memory": vm2_current
        }

        # 创建进度窗口
        progress_window = None
        try:
            # 显示进度对话框
            progress_window = ttk.Toplevel(self.master)
            progress_window.title("处理中")
            progress_window.geometry("300x150")
            progress_window.transient(self.master)
            progress_window.grab_set()
            progress_window.protocol("WM_DELETE_WINDOW", lambda: None)  # 禁用关闭按钮

            ttk.Label(progress_window, text="正在生成训练方案和报告...",
                      font=("Microsoft YaHei", 12)).pack(pady=20)
            progress_bar = ttk.Progressbar(progress_window, bootstyle="info-striped", mode="indeterminate")
            progress_bar.pack(fill=X, padx=20, pady=10)
            progress_bar.start(10)
            self.master.update()

            # 生成训练方案和测评报告
            generate_plan(name, age, child_ratings, SOURCE_FOLDER, DESTINATION_FOLDER)

            # 生成测评报告
            ReportGenerator().generate_measurement_report(
                name, age, test_date,
                vb, vb_current, vb_target, vb_target_eval,
                vd, vd_current, vd_target, vd_target_eval,
                vm, vm_current, vm_target, vm_target_eval,
                vm2, vm2_current, vm2_target, vm2_target_eval,
                training_center, assessor
            )

            # 关闭进度窗口并显示成功消息
            if progress_window and progress_window.winfo_exists(): progress_window.destroy()
            tk.messagebox.showinfo("成功", "训练方案和测评报告生成成功！")
            self.status_var.set(f"已成功为 {name} 生成训练方案和测评报告")

        except Exception as e:
            if progress_window and progress_window.winfo_exists(): progress_window.destroy()
            tk.messagebox.showerror("错误", f"生成过程中出现错误: {str(e)}")
            self.status_var.set("生成过程中出现错误")


def main():
    try:
        # 使用自定义主题
        root = ttk.Window(themename="litera")
        root.title("儿童视觉训练方案生成系统")
        root.state('zoomed')  # 在Windows下全屏
        root.minsize(1024, 768)

        # 定制颜色方案
        style = ttk.Style()
        lake_blue = "#4FB0C6"

        # 定制组件颜色
        style.configure("TButton", background=lake_blue, foreground="white")
        style.configure("info.TButton", background=lake_blue, foreground="white")
        style.configure("info-outline.TButton", background="white", foreground=lake_blue)
        style.configure("info.TLabelframe", bordercolor=lake_blue)
        style.configure("info.TLabelframe.Label", foreground=lake_blue)
        style.configure("TNotebook", background="white")
        style.configure("TNotebook.Tab", background="white", foreground=lake_blue)
        style.map("TNotebook.Tab", background=[("selected", lake_blue)], foreground=[("selected", "white")])
        style.configure("info.Horizontal.TProgressbar", background=lake_blue)
        style.configure("info-striped.Horizontal.TProgressbar", background=lake_blue)

        TrainingApp(root)
        root.mainloop()
    except Exception as e:
        print(f"程序启动错误: {e}")
        try:
            tkinter.messagebox.showerror("系统错误", f"程序启动失败: {str(e)}")
        except:
            pass


if __name__ == "__main__":
    main()