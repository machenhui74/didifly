#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import pythoncom
import win32com.client
import json
from pathlib import Path
from PIL import Image, ImageTk

class PPTCropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PPT 页面裁切工具")
        self.root.geometry("800x600")
        self.root.minsize(650, 500)
        
        self.source_file = ""
        self.output_folder = ""
        self.crop_values = {"top": 0, "bottom": 0, "left": 0, "right": 0}
        self.selection_rect = None
        self.start_x = 0
        self.start_y = 0
        self.current_slide = 1
        self.total_slides = 0
        self.presentation = None
        self.ppt_app = None
        
        self.create_config_file()
        self.load_config()
        self.create_widgets()
        self.center_window()
        
    def create_config_file(self):
        """创建配置文件，如果不存在"""
        config_path = Path(__file__).parent / "config.json"
        if not config_path.exists():
            default_config = {
                "last_source_file": "",
                "last_output_dir": "",
                "crop_top": 0,
                "crop_bottom": 0,
                "crop_left": 0,
                "crop_right": 0
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
    
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = Path(__file__).parent / "config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.source_file = config.get("last_source_file", "")
                    self.output_folder = config.get("last_output_dir", "")
                    self.crop_values["top"] = config.get("crop_top", 0)
                    self.crop_values["bottom"] = config.get("crop_bottom", 0)
                    self.crop_values["left"] = config.get("crop_left", 0)
                    self.crop_values["right"] = config.get("crop_right", 0)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
    
    def save_config(self):
        """保存配置文件"""
        try:
            config_path = Path(__file__).parent / "config.json"
            config = {
                "last_source_file": self.source_file,
                "last_output_dir": self.output_folder,
                "crop_top": self.crop_values["top"],
                "crop_bottom": self.crop_values["bottom"],
                "crop_left": self.crop_values["left"],
                "crop_right": self.crop_values["right"]
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        # 源文件选择
        ttk.Label(file_frame, text="PPT文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_entry = ttk.Entry(file_frame)
        self.source_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        if self.source_file:
            self.source_entry.insert(0, self.source_file)
        ttk.Button(file_frame, text="浏览...", command=self.select_source_file).grid(row=0, column=2, pady=5)
        
        # 输出文件夹选择
        ttk.Label(file_frame, text="输出文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_entry = ttk.Entry(file_frame)
        self.output_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        if self.output_folder:
            self.output_entry.insert(0, self.output_folder)
        ttk.Button(file_frame, text="浏览...", command=self.select_output_folder).grid(row=1, column=2, pady=5)
        
        file_frame.columnconfigure(1, weight=1)
        
        # 创建PPT预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="PPT预览和裁切选择", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建画布用于显示PPT幻灯片
        self.canvas = tk.Canvas(preview_frame, bg="white", bd=2, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # 创建幻灯片导航控制
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="上一页", command=self.prev_slide).pack(side=tk.LEFT, padx=5)
        
        self.slide_info = ttk.Label(nav_frame, text="幻灯片: 0/0")
        self.slide_info.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(nav_frame, text="下一页", command=self.next_slide).pack(side=tk.LEFT, padx=5)
        
        # 创建裁切信息区域
        crop_info_frame = ttk.LabelFrame(main_frame, text="裁切信息 (单位: 磅)", padding="10")
        crop_info_frame.pack(fill=tk.X, pady=5)
        
        self.crop_info = ttk.Label(crop_info_frame, text="选择区域: 未选择")
        self.crop_info.pack(fill=tk.X)
        
        # 创建操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="加载PPT", command=self.load_ppt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="应用裁切", command=self.apply_crop).pack(side=tk.LEFT, padx=5)
        
        # 设置状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X, side=tk.BOTTOM)
        
        # 设置关闭窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def select_source_file(self):
        """选择源PPT文件"""
        file = filedialog.askopenfilename(
            initialdir=os.path.dirname(self.source_file) if self.source_file else os.path.expanduser("~"),
            filetypes=[("PowerPoint文件", "*.ppt;*.pptx"), ("所有文件", "*.*")]
        )
        if file:
            self.source_file = file
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, file)
            self.save_config()
    
    def select_output_folder(self):
        """选择输出文件夹"""
        folder = filedialog.askdirectory(initialdir=self.output_folder if self.output_folder else os.path.expanduser("~"))
        if folder:
            self.output_folder = folder
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            self.save_config()
    
    def update_status(self, message):
        """更新状态栏消息"""
        self.status_var.set(message)
    
    def load_ppt(self):
        """加载PPT文件并显示第一页"""
        source_file = self.source_entry.get().strip()
        
        if not source_file or not os.path.isfile(source_file):
            messagebox.showerror("错误", "请选择有效的PPT文件")
            return
        
        # 如果已经打开了一个演示文稿，先关闭它
        self.close_current_presentation()
        
        # 添加提示信息
        self.update_status("正在加载PPT，请稍候...")
        
        # 启动线程加载PPT
        threading.Thread(target=self._load_ppt_thread, args=(source_file,), daemon=True).start()
    
    def close_current_presentation(self):
        """关闭当前的演示文稿"""
        if hasattr(self, 'presentation') and self.presentation:
            try:
                self.presentation.Close()
                self.presentation = None
            except:
                pass
            
        if hasattr(self, 'ppt_app') and self.ppt_app:
            try:
                self.ppt_app.Quit()
                self.ppt_app = None
            except:
                pass
            
            try:
                # 释放COM资源
                pythoncom.CoUninitialize()
            except:
                pass
    
    def _load_ppt_thread(self, source_file):
        """在线程中加载PPT"""
        try:
            # 初始化COM
            pythoncom.CoInitialize()
            
            # 创建PowerPoint应用程序实例
            self.ppt_app = win32com.client.Dispatch("PowerPoint.Application")
            self.ppt_app.Visible = False  # 尝试隐藏PowerPoint窗口
            
            # 获取文件的绝对路径
            source_file_abs = os.path.abspath(source_file)
            
            # 打开PPT文件 - 修改参数
            self.presentation = self.ppt_app.Presentations.Open(
                source_file_abs,
                ReadOnly=True,  # 以只读方式打开
                WithWindow=False
            )
            
            if not self.presentation:
                raise Exception("无法打开PowerPoint文件")
            
            self.total_slides = self.presentation.Slides.Count
            self.current_slide = 1
            
            # 更新状态和导航信息
            self.root.after(0, lambda: self.slide_info.config(text=f"幻灯片: {self.current_slide}/{self.total_slides}"))
            self.root.after(0, lambda: self.update_status(f"已加载PPT: {os.path.basename(source_file)}"))
            
            # 显示第一页
            self.show_slide(1)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("错误", f"加载PPT失败: {error_msg}"))
            self.root.after(0, self.close_current_presentation)
    
    def show_slide(self, slide_index):
        """显示指定页码的幻灯片"""
        if not self.presentation:
            messagebox.showerror("错误", "请先加载PPT文件")
            return
        
        if slide_index < 1 or slide_index > self.total_slides:
            return
        
        try:
            # 获取幻灯片的导出路径
            temp_dir = os.path.join(os.environ['TEMP'], 'ppt_cropper')
            os.makedirs(temp_dir, exist_ok=True)
            image_path = os.path.join(temp_dir, f"slide_{slide_index}.png")
            
            # 更新当前页码
            self.current_slide = slide_index
            self.slide_info.config(text=f"幻灯片: {self.current_slide}/{self.total_slides}")
            
            # 清除旧的选择矩形
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None
            
            # 导出当前幻灯片
            slide = self.presentation.Slides(slide_index)
            slide.Export(image_path, "PNG")
            
            # 在主线程中更新UI
            self.root.after(0, lambda: self._update_canvas(image_path))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("错误", f"显示幻灯片失败: {error_msg}"))
    
    def _update_canvas(self, image_path):
        """更新画布显示"""
        # 清除画布
        self.canvas.delete("all")
        
        # 加载图片
        img = Image.open(image_path)
        
        # 调整画布大小
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 计算缩放比例
        img_width, img_height = img.size
        scale = min(canvas_width / img_width, canvas_height / img_height)
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # 缩放图片
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(resized_img)
        
        # 显示图片
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.tk_img)
        
        # 保存图片信息用于坐标转换
        self.img_info = {
            "width": img_width,
            "height": img_height,
            "canvas_width": canvas_width,
            "canvas_height": canvas_height,
            "scale": scale,
            "x_offset": (canvas_width - new_width) // 2,
            "y_offset": (canvas_height - new_height) // 2
        }
    
    def on_mouse_down(self, event):
        """鼠标按下事件处理"""
        if not hasattr(self, 'img_info'):
            return
        
        # 清除旧的选择矩形
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # 记录起始位置
        self.start_x = event.x
        self.start_y = event.y
        
        # 创建新的选择矩形
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )
    
    def on_mouse_drag(self, event):
        """鼠标拖动事件处理"""
        if not self.selection_rect:
            return
        
        # 更新选择矩形
        self.canvas.coords(self.selection_rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_mouse_up(self, event):
        """鼠标释放事件处理"""
        if not self.selection_rect or not hasattr(self, 'img_info'):
            return
        
        # 获取选择矩形的坐标
        x1, y1, x2, y2 = self.canvas.coords(self.selection_rect)
        
        # 确保顺序正确
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        # 转换为PPT坐标系 (磅)
        img_info = self.img_info
        
        # 计算相对于图片左上角的坐标
        x1 = max(0, x1 - img_info["x_offset"]) / img_info["scale"]
        y1 = max(0, y1 - img_info["y_offset"]) / img_info["scale"]
        x2 = min(img_info["width"], (x2 - img_info["x_offset"]) / img_info["scale"])
        y2 = min(img_info["height"], (y2 - img_info["y_offset"]) / img_info["scale"])
        
        # 获取当前幻灯片的尺寸
        if self.presentation:
            slide_width = self.presentation.PageSetup.SlideWidth
            slide_height = self.presentation.PageSetup.SlideHeight
            
            # 计算裁切值
            crop_left = x1
            crop_top = y1
            crop_right = slide_width - x2
            crop_bottom = slide_height - y2
            
            # 更新裁切值
            self.crop_values["left"] = round(crop_left)
            self.crop_values["top"] = round(crop_top)
            self.crop_values["right"] = round(crop_right)
            self.crop_values["bottom"] = round(crop_bottom)
            
            # 更新裁切信息
            self.crop_info.config(
                text=f"选择区域: 左={round(crop_left,1)}, 上={round(crop_top,1)}, 右={round(crop_right,1)}, 下={round(crop_bottom,1)}"
            )
    
    def prev_slide(self):
        """显示上一页幻灯片"""
        if self.current_slide > 1:
            self.show_slide(self.current_slide - 1)
    
    def next_slide(self):
        """显示下一页幻灯片"""
        if self.current_slide < self.total_slides:
            self.show_slide(self.current_slide + 1)
    
    def apply_crop(self):
        """应用裁切到PPT"""
        if not self.presentation:
            messagebox.showerror("错误", "请先加载PPT文件")
            return
        
        source_file = self.source_entry.get().strip()
        output_folder = self.output_entry.get().strip()
        
        if not output_folder or not os.path.isdir(output_folder):
            messagebox.showerror("错误", "请选择有效的输出文件夹")
            return
        
        # 获取裁切参数
        crop_top = self.crop_values["top"]
        crop_bottom = self.crop_values["bottom"]
        crop_left = self.crop_values["left"]
        crop_right = self.crop_values["right"]
        
        if crop_top == 0 and crop_bottom == 0 and crop_left == 0 and crop_right == 0:
            response = messagebox.askyesno("提示", "您没有设置任何裁切值，确定要继续吗？")
            if not response:
                return
        
        # 保存配置
        self.save_config()
        
        # 确认是否应用到所有幻灯片
        apply_to_all = messagebox.askyesno("确认", "是否将当前裁切设置应用到所有幻灯片？\n选择「否」将只应用到当前幻灯片。")
        
        # 更新状态
        self.update_status("正在处理PPT裁切，请稍候...")
        
        # 启动处理线程
        threading.Thread(
            target=self._process_ppt_thread,
            args=(source_file, output_folder, crop_top, crop_bottom, crop_left, crop_right, apply_to_all),
            daemon=True
        ).start()
    
    def _process_ppt_thread(self, source_file, output_folder, crop_top, crop_bottom, crop_left, crop_right, apply_to_all):
        """在线程中处理PPT"""
        try:
            # 使用新的COM对象，避免与预览冲突
            pythoncom.CoInitialize()
            
            # 创建新的PowerPoint实例用于处理
            process_ppt_app = win32com.client.Dispatch("PowerPoint.Application")
            process_ppt_app.Visible = False  # 尝试隐藏PowerPoint窗口
            
            # 打开文件
            process_presentation = process_ppt_app.Presentations.Open(
                os.path.abspath(source_file),
                ReadOnly=False,  # 需要写入模式
                WithWindow=False
            )
            
            # 文件名处理
            filename = os.path.basename(source_file)
            base_name, ext = os.path.splitext(filename)
            output_file = os.path.join(output_folder, f"{base_name}_裁切{ext}")
            
            # 处理幻灯片
            if apply_to_all:
                slide_range = range(1, process_presentation.Slides.Count + 1)
            else:
                slide_range = [self.current_slide]
            
            for slide_index in slide_range:
                # 设置裁切
                if crop_top > 0 or crop_bottom > 0 or crop_left > 0 or crop_right > 0:
                    try:
                        slide = process_presentation.Slides(slide_index)
                        
                        # 获取当前幻灯片的尺寸
                        slide_width = process_presentation.PageSetup.SlideWidth
                        slide_height = process_presentation.PageSetup.SlideHeight
                        
                        # 计算新的尺寸
                        new_width = slide_width - (crop_left + crop_right)
                        new_height = slide_height - (crop_top + crop_bottom)
                        
                        # 如果裁切后尺寸太小，则跳过
                        if new_width <= 100 or new_height <= 100:
                            continue
                        
                        # 修改幻灯片尺寸
                        slide.CustomLayout.Parent.PageSetup.SlideWidth = new_width
                        slide.CustomLayout.Parent.PageSetup.SlideHeight = new_height
                        
                        # 调整所有对象的位置
                        for shape_index in range(slide.Shapes.Count):
                            shape = slide.Shapes(shape_index + 1)
                            shape.Left = shape.Left - crop_left
                            shape.Top = shape.Top - crop_top
                    except Exception as slide_error:
                        self.root.after(0, lambda: messagebox.showwarning("警告", f"处理幻灯片 {slide_index} 时出错: {slide_error}"))
                        continue
            
            # 保存文件
            output_file_abs = os.path.abspath(output_file)
            process_presentation.SaveAs(output_file_abs)
            
            # 关闭文件和应用
            process_presentation.Close()
            process_ppt_app.Quit()
            
            # 释放COM资源
            pythoncom.CoUninitialize()
            
            # 更新状态
            output_filename = os.path.basename(output_file)
            self.root.after(0, lambda: self.update_status(f"已保存: {output_filename}"))
            self.root.after(0, lambda: messagebox.showinfo("完成", f"裁切已完成并保存为:\n{output_file}"))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理失败: {error_msg}"))
            
            # 尝试释放资源
            try:
                if 'process_presentation' in locals():
                    process_presentation.Close()
                if 'process_ppt_app' in locals():
                    process_ppt_app.Quit()
                pythoncom.CoUninitialize()
            except:
                pass
    
    def on_closing(self):
        """窗口关闭事件处理"""
        # 保存配置
        self.save_config()
        
        # 关闭当前的演示文稿
        self.close_current_presentation()
        
        self.root.destroy()

def main():
    root = tk.Tk()
    app = PPTCropperApp(root)
    
    # 显示提示信息
    messagebox.showinfo("提示", "本工具需要使用PowerPoint进行操作，\n请确保系统中已安装并正确配置Microsoft PowerPoint。")
    
    root.mainloop()

if __name__ == "__main__":
    main() 