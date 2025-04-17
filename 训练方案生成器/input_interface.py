import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import sys
# 延迟导入TrainingPlanGenerator
# from report_generator import TrainingPlanGenerator

class InputInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("训练方案生成器")
        self.root.geometry("900x600")
        
        # 设置窗口图标
        try:
            self.base_dir = self.get_base_dir()
            icon_path = os.path.join(self.base_dir, "app_icon.png")
            if os.path.exists(icon_path):
                try:
                    # Windows系统
                    self.root.iconbitmap(default=icon_path.replace(".png", ".ico"))
                except:
                    pass
                    
                try:
                    # Linux/Mac系统
                    from PIL import Image, ImageTk
                    icon_img = ImageTk.PhotoImage(file=icon_path)
                    self.root.tk.call('wm', 'iconphoto', self.root._w, icon_img)
                except:
                    pass
        except Exception as e:
            print(f"设置图标失败: {str(e)}")
        
        # 设置变量
        self.name_var, self.age_var, self.tag_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        
        # 路径配置文件
        self.paths_config_path = os.path.join(self.base_dir, "paths_config.json")
        
        # 默认路径
        default_output_dir = os.path.join(self.base_dir, "输出方案")
        default_action_db = os.path.join(self.base_dir, "action_database.xlsx")
        
        # 加载上次使用的路径
        saved_paths = self.load_paths()
        self.output_dir = tk.StringVar(value=self.validate_path(saved_paths.get("output_dir", default_output_dir), default_output_dir))
        self.action_db_path = tk.StringVar(value=self.validate_path(saved_paths.get("action_db_path", default_action_db), default_action_db))
        self.tags_config_path = os.path.join(self.base_dir, "tags_config.json")
        
        # 标签相关
        self.selected_tags = []
        self.default_tags = ['动态平衡', '静态平衡', '视动统合动作', '视觉屏蔽动作', '视觉记忆', '视觉抗干扰', 
                             '空间感知', '视觉前庭整合训练', '听动统合动作', '听觉屏蔽动作', '听觉记忆', '听觉抗干扰', 
                             '力量', '耐力', '手眼协调', '手脚协调', '双侧', '脚眼', '核心', '精细动作', 
                             '触觉精进', '触觉脱敏', '复合二', '复合三', '复合四', '动作企划']
        self.predefined_tags = self.load_tags()
        self.tag_buttons = {}
        
        # 创建界面
        self.create_widgets()
        
        # 立即创建标签按钮
        self.create_tag_buttons()
        
        # 绑定窗口大小改变事件
        self.root.bind("<Configure>", self.on_window_resize)
        self.last_width = self.root.winfo_width()
        self.is_resizing = False
    
    def get_base_dir(self):
        """获取应用基础目录，兼容打包和非打包环境"""
        # 尝试获取打包后的目录
        if getattr(sys, 'frozen', False):
            # 运行于PyInstaller打包环境
            return os.path.dirname(sys.executable)
        else:
            # 运行于普通Python环境
            return os.path.dirname(os.path.abspath(__file__))
    
    def validate_path(self, path, default_path):
        """验证路径是否有效，无效则返回默认路径"""
        if path and (os.path.exists(path) or os.path.exists(os.path.dirname(path))):
            return path
        return default_path
    
    def load_paths(self):
        """加载上次使用的路径"""
        try:
            if os.path.exists(self.paths_config_path):
                with open(self.paths_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            # 加载失败时不显示警告，直接返回空字典
            print(f"无法加载路径配置: {str(e)}")
            return {}
    
    def save_paths(self):
        """保存当前使用的路径"""
        try:
            paths_data = {
                "output_dir": self.output_dir.get(),
                "action_db_path": self.action_db_path.get()
            }
            os.makedirs(os.path.dirname(self.paths_config_path), exist_ok=True)
            with open(self.paths_config_path, 'w', encoding='utf-8') as f:
                json.dump(paths_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning("警告", f"无法保存路径配置: {str(e)}")
    
    def load_tags(self):
        """加载标签"""
        try:
            if os.path.exists(self.tags_config_path):
                with open(self.tags_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get('tags', self.default_tags)
            return self.default_tags
        except Exception as e:
            # 加载失败时不显示警告
            print(f"无法加载标签配置: {str(e)}")
            return self.default_tags
    
    def save_tags(self):
        """保存标签"""
        try:
            os.makedirs(os.path.dirname(self.tags_config_path), exist_ok=True)
            with open(self.tags_config_path, 'w', encoding='utf-8') as f:
                json.dump({'tags': self.predefined_tags}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning("警告", f"无法保存标签配置: {str(e)}")
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== 基本信息区域 =====
        info_frame = ttk.LabelFrame(main_frame, text="基本信息", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        
        # 姓名和年龄输入
        ttk.Label(info_frame, text="姓名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(info_frame, text="年龄:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.age_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 按钮区
        button_frame = ttk.Frame(info_frame)
        button_frame.grid(row=0, column=2, rowspan=2, padx=20, pady=5, sticky=tk.E)
        
        # 生成按钮和重置按钮
        btn_args = {'font': ('Arial', 14, 'bold'), 'width': 15, 'height': 2}
        tk.Button(button_frame, text="生成训练方案", command=self.generate_plan, 
                  bg='#4CAF50', fg='white', **btn_args).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="重置信息", command=self.reset_form,
                  bg='#f44336', fg='white', **btn_args).pack(side=tk.LEFT)
        
        # ===== 标签区域 =====
        tag_frame = ttk.LabelFrame(main_frame, text="训练标签", padding=10)
        tag_frame.pack(fill=tk.X, pady=5)
        
        # 标签按钮区域 - 使用FlowFrame使按钮自动换行
        self.tags_container = ttk.Frame(tag_frame)
        self.tags_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 自定义标签区域
        custom_frame = ttk.Frame(tag_frame)
        custom_frame.pack(fill=tk.X, pady=5)
        ttk.Label(custom_frame, text="添加自定义标签:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(custom_frame, textvariable=self.tag_var).pack(side=tk.LEFT, padx=5)
        ttk.Button(custom_frame, text="添加", command=self.add_custom_tag).pack(side=tk.LEFT, padx=5)
        
        # 已选标签显示
        self.selected_label = ttk.Label(tag_frame, text="已选标签: 无")
        self.selected_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # ===== 文件路径区域 =====
        path_header = ttk.Frame(main_frame)
        path_header.pack(fill=tk.X, pady=(5,0))
        ttk.Label(path_header, text="文件路径", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # 文件路径内容
        self.path_frame = ttk.LabelFrame(main_frame, padding=10)
        self.path_frame.pack(fill=tk.X, pady=(0,5))
        
        # 动作库路径和输出目录
        paths = [("动作库路径:", self.action_db_path, self.browse_file), 
                 ("输出目录:", self.output_dir, self.browse_directory)]
        for row, (label, var, cmd) in enumerate(paths):
            ttk.Label(self.path_frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(self.path_frame, textvariable=var).grid(row=row, column=1, sticky=tk.EW, padx=5, pady=5)
            ttk.Button(self.path_frame, text="浏览", command=lambda v=var, c=cmd: c(v)).grid(row=row, column=2, padx=5, pady=5)
        self.path_frame.columnconfigure(1, weight=1)
    
    def on_window_resize(self, event):
        """窗口大小改变时重新排列标签"""
        # 只在宽度变化时重新布局，并添加防抖动延迟
        if event.widget == self.root and self.last_width != self.root.winfo_width():
            self.last_width = self.root.winfo_width()
            
            # 防抖动：取消之前的延迟重画，并设置新的延迟
            if self.is_resizing:
                self.root.after_cancel(self.is_resizing)
            
            # 100毫秒后重新布局标签按钮
            self.is_resizing = self.root.after(100, self.create_tag_buttons)
    
    def create_tag_buttons(self):
        # 设置不在调整大小状态
        self.is_resizing = False
        
        # 清除现有标签按钮
        for widget in self.tags_container.winfo_children():
            widget.destroy()
        
        # 计算可用宽度和每个按钮的宽度
        container_width = self.tags_container.winfo_width()
        if container_width <= 1:  # 窗口未完全初始化
            container_width = self.root.winfo_width() - 40  # 估计值
        
        btn_width = 100  # 按钮基础宽度(像素)
        padding = 10     # 按钮间距
        
        # 计算每行能放多少个按钮
        buttons_per_row = max(1, (container_width) // (btn_width + padding))
        
        # 创建按钮容器框架
        flow_frame = ttk.Frame(self.tags_container)
        flow_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建新的标签按钮
        self.tag_buttons = {}
        row, col = 0, 0
        
        for tag in self.predefined_tags:
            if col >= buttons_per_row:
                col = 0
                row += 1
            
            # 创建标签按钮
            btn = tk.Button(flow_frame, text=tag, width=12, relief=tk.RAISED,
                          bg='#4CAF50' if tag in self.selected_tags else 'SystemButtonFace',
                          fg='white' if tag in self.selected_tags else 'black',
                          command=lambda t=tag: self.toggle_tag(t))
            
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.tag_buttons[tag] = btn
            
            # 添加右键菜单
            self.add_right_click_menu(btn, tag)
            
            col += 1
        
        # 让按钮可以拉伸
        for i in range(buttons_per_row):
            flow_frame.columnconfigure(i, weight=1)
        
        # 更新已选标签显示
        self.update_selected_tags_display()
    
    def add_right_click_menu(self, button, tag):
        """为标签按钮添加右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="重命名", command=lambda: self.rename_tag(tag))
        menu.add_command(label="删除", command=lambda: self.delete_tag(tag))
        
        # 绑定右键事件
        button.bind("<Button-3>", lambda event, m=menu: m.post(event.x_root, event.y_root))
    
    def rename_tag(self, tag):
        """重命名标签"""
        dialog = tk.Toplevel(self.root)
        dialog.title("重命名标签")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示对话框
        dialog.withdraw()  # 先隐藏
        dialog.update_idletasks()
        
        # 计算居中位置
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.deiconify()  # 显示对话框
        
        ttk.Label(dialog, text="请输入新的标签名称:").pack(pady=(10, 5))
        new_name_var = tk.StringVar(value=tag)
        entry = ttk.Entry(dialog, textvariable=new_name_var, width=30)
        entry.pack(pady=5, padx=10)
        entry.select_range(0, tk.END)
        entry.focus_set()
        
        def on_rename():
            new_name = new_name_var.get().strip()
            if not new_name:
                messagebox.showwarning("警告", "标签名称不能为空", parent=dialog)
                return
            
            if new_name == tag:
                dialog.destroy()
                return
                
            if new_name in self.predefined_tags:
                messagebox.showwarning("警告", f"标签 '{new_name}' 已存在", parent=dialog)
                return
            
            # 更新标签名称
            index = self.predefined_tags.index(tag)
            self.predefined_tags[index] = new_name
            
            # 如果标签在已选列表中，也更新
            if tag in self.selected_tags:
                index = self.selected_tags.index(tag)
                self.selected_tags[index] = new_name
            
            self.save_tags()
            self.create_tag_buttons()
            self.update_selected_tags_display()
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="确定", command=on_rename).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT)
        
        # 按回车确认
        dialog.bind("<Return>", lambda event: on_rename())
        dialog.bind("<Escape>", lambda event: dialog.destroy())
    
    def delete_tag(self, tag):
        """删除标签"""
        if messagebox.askyesno("确认", f"确定要删除标签 '{tag}' 吗?"):
            # 从预定义标签中删除
            if tag in self.predefined_tags:
                self.predefined_tags.remove(tag)
            
            # 从已选标签中删除
            if tag in self.selected_tags:
                self.selected_tags.remove(tag)
            
            self.save_tags()
            self.create_tag_buttons()
            self.update_selected_tags_display()
    
    def toggle_tag(self, tag):
        """切换标签选中状态"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
        else:
            self.selected_tags.append(tag)
        
        # 更新按钮样式
        self.tag_buttons[tag].config(
            bg='#4CAF50' if tag in self.selected_tags else 'SystemButtonFace',
            fg='white' if tag in self.selected_tags else 'black'
        )
        self.update_selected_tags_display()
    
    def add_custom_tag(self):
        """添加自定义标签"""
        tag = self.tag_var.get().strip()
        if not tag:
            return
        
        if tag not in self.predefined_tags:
            self.predefined_tags.append(tag)
            self.save_tags()
            self.create_tag_buttons()
            messagebox.showinfo("成功", f"已添加新标签: {tag}")
        else:
            messagebox.showinfo("提示", f"标签 '{tag}' 已存在")
        
        if tag not in self.selected_tags:
            self.selected_tags.append(tag)
            self.update_selected_tags_display()
        self.tag_var.set("")
    
    def update_selected_tags_display(self):
        """更新已选标签显示"""
        text = "已选标签: " + (", ".join(self.selected_tags) if self.selected_tags else "无")
        self.selected_label.config(text=text)
    
    def browse_file(self, var):
        """选择文件"""
        filename = filedialog.askopenfilename(filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")])
        if filename:
            var.set(filename)
            self.save_paths()  # 保存路径设置
    
    def browse_directory(self, var):
        """选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)
            self.save_paths()  # 保存路径设置
    
    def reset_form(self):
        """重置表单"""
        self.name_var.set("")
        self.age_var.set("")
        self.selected_tags = []
        self.update_selected_tags_display()
        self.create_tag_buttons()
        messagebox.showinfo("提示", "已重置所有信息")
    
    def generate_plan(self):
        """生成训练方案"""
        name, age = self.name_var.get().strip(), self.age_var.get().strip()
        
        # 获取动作库路径
        action_db_path = self.action_db_path.get()
        
        # 验证输入
        if not all([name, age, age.isdigit(), self.selected_tags]):
            for condition, msg in [
                (not name, "请输入姓名"),
                (not age or not age.isdigit(), "请输入有效年龄"),
                (not self.selected_tags, "请至少选择一个训练标签")
            ]:
                if condition:
                    messagebox.showwarning("警告", msg)
                    return
        
        # 验证动作库文件是否存在
        if not os.path.exists(action_db_path):
            messagebox.showwarning("警告", "动作库文件不存在，请选择有效的动作库文件")
            return
            
        # 确保输出目录存在
        output_dir = self.output_dir.get()
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            messagebox.showwarning("警告", f"无法创建输出目录: {str(e)}")
            return
        
        # 保存当前路径设置
        self.save_paths()
        
        # 仅在需要生成方案时才导入TrainingPlanGenerator
        try:
            # 这里才导入TrainingPlanGenerator
            from report_generator import TrainingPlanGenerator
            
            # 生成训练方案
            generator = TrainingPlanGenerator()
            generator.generate_training_plan(
                name, age, self.selected_tags, 
                action_db_path, output_dir
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"生成训练方案失败: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = InputInterface(root)
        root.mainloop()
    except Exception as e:
        import traceback
        error_msg = f"程序启动失败: {str(e)}\n\n{traceback.format_exc()}"
        try:
            messagebox.showerror("严重错误", error_msg)
        except:
            print(error_msg)
            input("按Enter键退出...")

if __name__ == "__main__":
    main()