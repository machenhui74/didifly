import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
from pathlib import Path
import sys

from watermark_processor import WatermarkProcessor

class WatermarkRemoverUI:
    def __init__(self, root):
        self.root = root
        self.root.title("批量水印消除工具")
        self.root.geometry("1000x600")
        self.processor = WatermarkProcessor()
        self.input_folder, self.output_folder, self.current_image_path = "", "", None
        self.watermark_rects, self.rectangle_ids, self.image_paths = [], [], []
        self.start_x, self.start_y, self.current_rect = 0, 0, None
        self.is_previewing, self.dragging_rect = False, None
        self.drag_start_x, self.drag_start_y = 0, 0
        self.resize_edge = None  # 新增：记录调整的边缘
        self._create_ui()
    
    def _create_ui(self):
        # 左侧控制面板
        control_frame = tk.Frame(self.root, width=300)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        # 输入文件夹选择
        tk.Label(control_frame, text="输入文件夹:").pack(anchor="w", pady=(0, 5))
        input_frame = tk.Frame(control_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        self.input_entry = tk.Entry(input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(input_frame, text="浏览", command=self.select_input_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 输出文件夹选择
        tk.Label(control_frame, text="输出文件夹:").pack(anchor="w", pady=(0, 5))
        output_frame = tk.Frame(control_frame)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        self.output_entry = tk.Entry(output_frame)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(output_frame, text="浏览", command=self.select_output_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 图像列表
        tk.Label(control_frame, text="图像列表:").pack(anchor="w", pady=(0, 5))
        self.image_listbox = tk.Listbox(control_frame, height=10)
        self.image_listbox.pack(fill=tk.X, pady=(0, 10))
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # 水印处理参数
        tk.Label(control_frame, text="处理参数:").pack(anchor="w", pady=(0, 5))
        
        # 操作按钮
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        self.preview_btn = tk.Button(btn_frame, text="预览效果", command=self.toggle_preview)
        self.preview_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="批量处理", command=self.batch_process).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="清除选择", command=self.clear_selections).pack(side=tk.RIGHT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.progress_bar = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        tk.Label(control_frame, textvariable=self.status_var).pack(anchor="w")
        
        # 右侧图像显示区域
        image_frame = tk.Frame(self.root)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(image_frame, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        
        # 提示
        tk.Label(image_frame, text="提示: 在图像上拖拽鼠标来选择水印区域，右键点击矩形可删除选择").pack(anchor="w")
    
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="选择包含水印图像的文件夹")
        if folder:
            self.input_folder = folder
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, folder)
            self.load_images()
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_folder = folder
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
    
    def load_images(self):
        self.image_listbox.delete(0, tk.END)
        self.image_paths = []
        if not self.input_folder: return
        
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        self.image_paths = [os.path.join(self.input_folder, f) for f in os.listdir(self.input_folder) 
                           if f.lower().endswith(valid_extensions)]
        
        for path in self.image_paths:
            self.image_listbox.insert(tk.END, os.path.basename(path))
        
        self.status_var.set(f"已加载 {len(self.image_paths)} 个图像文件")
        
        if self.image_paths:
            self.image_listbox.selection_set(0)
            self.on_image_select(None)
    
    def on_image_select(self, event):
        selection = self.image_listbox.curselection()
        if selection:
            self.current_image_path = self.image_paths[selection[0]]
            self.load_image(self.current_image_path)
    
    def load_image(self, image_path):
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)
                canvas_width = self.canvas.winfo_width() or self.root.update() or self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height() or self.canvas.winfo_height()
                
                self.original_image = np.array(image)
                
                img_width, img_height = image.size
                self.scale_ratio = min(canvas_width / img_width, canvas_height / img_height)
                new_width, new_height = int(img_width * self.scale_ratio), int(img_height * self.scale_ratio)
                
                self.display_image = image.resize((new_width, new_height), Image.LANCZOS)
                self.photo_image = ImageTk.PhotoImage(self.display_image)
                
                self.canvas.delete("all")
                self.image_id = self.canvas.create_image(
                    (canvas_width - new_width) // 2, 
                    (canvas_height - new_height) // 2, 
                    anchor=tk.NW, image=self.photo_image
                )
                
                self.watermark_rects, self.rectangle_ids, self.current_rect = [], [], None
                self.is_previewing = False
                self.status_var.set("已加载图像")
            else:
                messagebox.showerror("错误", f"文件不存在: {image_path}")
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图像: {str(e)}")
    
    def on_mouse_down(self, event):
        if not hasattr(self, 'photo_image') or not self.photo_image or self.is_previewing:
            return
        
        coords = self.canvas.coords(self.image_id)
        img_width, img_height = self.display_image.width, self.display_image.height
        
        if (coords[0] <= event.x <= coords[0] + img_width and 
            coords[1] <= event.y <= coords[1] + img_height):
            
            # 检查鼠标是否在矩形边缘，进行大小调整
            edge = self.get_resize_edge(event.x, event.y)
            if edge:
                self.resize_edge = edge
                return
            
            # 检查是否点击了现有矩形
            for i, rect_id in enumerate(self.rectangle_ids):
                if self.is_point_in_rectangle(event.x, event.y, rect_id):
                    self.dragging_rect = i
                    self.drag_start_x, self.drag_start_y = event.x, event.y
                    return
            
            # 水印区域上限检查
            if len(self.watermark_rects) >= 3:
                messagebox.showinfo("提示", "最多只能选择3个水印区域")
                return
            
            self.start_x, self.start_y = event.x, event.y
            self.current_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline="red", width=2
            )
    
    def get_resize_edge(self, x, y, threshold=5):
        for i, rect_id in enumerate(self.rectangle_ids):
            coords = self.canvas.coords(rect_id)
            if not coords: continue
            
            # 检查是否在边缘
            left_edge = abs(x - coords[0]) < threshold and coords[1] <= y <= coords[3]
            right_edge = abs(x - coords[2]) < threshold and coords[1] <= y <= coords[3]
            top_edge = abs(y - coords[1]) < threshold and coords[0] <= x <= coords[2]
            bottom_edge = abs(y - coords[3]) < threshold and coords[0] <= x <= coords[2]
            
            if left_edge:
                return ('left', i)
            elif right_edge:
                return ('right', i)
            elif top_edge:
                return ('top', i)
            elif bottom_edge:
                return ('bottom', i)
        
        return None
    
    def on_mouse_drag(self, event):
        if self.is_previewing: return
        
        if self.resize_edge:
            edge_type, rect_index = self.resize_edge
            rect_id = self.rectangle_ids[rect_index]
            coords = self.canvas.coords(rect_id)
            
            if edge_type == 'left':
                self.canvas.coords(rect_id, event.x, coords[1], coords[2], coords[3])
            elif edge_type == 'right':
                self.canvas.coords(rect_id, coords[0], coords[1], event.x, coords[3])
            elif edge_type == 'top':
                self.canvas.coords(rect_id, coords[0], event.y, coords[2], coords[3])
            elif edge_type == 'bottom':
                self.canvas.coords(rect_id, coords[0], coords[1], coords[2], event.y)
                
        elif self.current_rect:
            self.canvas.coords(self.current_rect, self.start_x, self.start_y, event.x, event.y)
        elif self.dragging_rect is not None:
            dx, dy = event.x - self.drag_start_x, event.y - self.drag_start_y
            rect_id = self.rectangle_ids[self.dragging_rect]
            coords = self.canvas.coords(rect_id)
            self.canvas.coords(rect_id, 
                coords[0] + dx, coords[1] + dy, 
                coords[2] + dx, coords[3] + dy)
            self.drag_start_x, self.drag_start_y = event.x, event.y
    
    def on_mouse_up(self, event):
        if self.is_previewing: return
        
        if self.resize_edge:
            edge_type, rect_index = self.resize_edge
            rect_id = self.rectangle_ids[rect_index]
            canvas_coords = self.canvas.coords(rect_id)
            img_coords = self.canvas.coords(self.image_id)
            
            # 更新水印区域原始坐标
            x1 = max(0, (canvas_coords[0] - img_coords[0]) / self.scale_ratio)
            y1 = max(0, (canvas_coords[1] - img_coords[1]) / self.scale_ratio)
            x2 = min(self.original_image.shape[1], (canvas_coords[2] - img_coords[0]) / self.scale_ratio)
            y2 = min(self.original_image.shape[0], (canvas_coords[3] - img_coords[1]) / self.scale_ratio)
            
            if x1 > x2: x1, x2 = x2, x1
            if y1 > y2: y1, y2 = y2, y1
            
            self.watermark_rects[rect_index] = (int(x1), int(y1), int(x2), int(y2))
            self.resize_edge = None
            
        elif self.current_rect:
            coords = self.canvas.coords(self.image_id)
            # 计算原始图像坐标
            x1 = max(0, (self.start_x - coords[0]) / self.scale_ratio)
            y1 = max(0, (self.start_y - coords[1]) / self.scale_ratio)
            x2 = min(self.original_image.shape[1], (event.x - coords[0]) / self.scale_ratio)
            y2 = min(self.original_image.shape[0], (event.y - coords[1]) / self.scale_ratio)
            
            # 确保坐标有序
            if x1 > x2: x1, x2 = x2, x1
            if y1 > y2: y1, y2 = y2, y1
            
            rect = (int(x1), int(y1), int(x2), int(y2))
            
            # 检查矩形大小
            if rect[2] - rect[0] < 5 or rect[3] - rect[1] < 5:
                self.canvas.delete(self.current_rect)
            else:
                self.watermark_rects.append(rect)
                self.rectangle_ids.append(self.current_rect)
                self.status_var.set(f"已选择 {len(self.watermark_rects)} 个水印区域")
            
            self.current_rect = None
        
        elif self.dragging_rect is not None:
            # 更新移动后的矩形坐标
            rect_id = self.rectangle_ids[self.dragging_rect]
            canvas_coords = self.canvas.coords(rect_id)
            img_coords = self.canvas.coords(self.image_id)
            
            # 更新水印区域原始坐标
            x1 = max(0, (canvas_coords[0] - img_coords[0]) / self.scale_ratio)
            y1 = max(0, (canvas_coords[1] - img_coords[1]) / self.scale_ratio)
            x2 = min(self.original_image.shape[1], (canvas_coords[2] - img_coords[0]) / self.scale_ratio)
            y2 = min(self.original_image.shape[0], (canvas_coords[3] - img_coords[1]) / self.scale_ratio)
            
            self.watermark_rects[self.dragging_rect] = (int(x1), int(y1), int(x2), int(y2))
            self.dragging_rect = None
    
    def is_point_in_rectangle(self, x, y, rect_id):
        rect_coords = self.canvas.coords(rect_id)
        if not rect_coords: return False
        return (rect_coords[0] <= x <= rect_coords[2] and rect_coords[1] <= y <= rect_coords[3])
    
    def on_right_click(self, event):
        if self.is_previewing: return
        
        for i, rect_id in enumerate(self.rectangle_ids):
            if self.is_point_in_rectangle(event.x, event.y, rect_id):
                self.canvas.delete(rect_id)
                self.rectangle_ids.pop(i)
                self.watermark_rects.pop(i)
                self.status_var.set(f"已选择 {len(self.watermark_rects)} 个水印区域")
                return
    
    def clear_selections(self):
        if self.is_previewing: return
        
        for rect_id in self.rectangle_ids:
            self.canvas.delete(rect_id)
        
        self.rectangle_ids, self.watermark_rects = [], []
        self.status_var.set("已清除所有水印选择")
    
    def toggle_preview(self):
        if self.is_previewing:
            # 取消预览，恢复原图
            self.is_previewing = False
            self.preview_btn.config(text="预览效果")
            
            # 恢复原图显示
            if hasattr(self, 'photo_image') and self.photo_image:
                canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
                x_pos = (canvas_width - self.display_image.width) // 2
                y_pos = (canvas_height - self.display_image.height) // 2
                
                self.canvas.delete("all")
                self.image_id = self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.photo_image)
                
                # 重新绘制矩形
                self.rectangle_ids = []
                img_coords = self.canvas.coords(self.image_id)
                
                for rect in self.watermark_rects:
                    x1, y1, x2, y2 = rect
                    canvas_x1 = img_coords[0] + x1 * self.scale_ratio
                    canvas_y1 = img_coords[1] + y1 * self.scale_ratio
                    canvas_x2 = img_coords[0] + x2 * self.scale_ratio
                    canvas_y2 = img_coords[1] + y2 * self.scale_ratio
                    
                    rect_id = self.canvas.create_rectangle(
                        canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                        outline="red", width=2
                    )
                    self.rectangle_ids.append(rect_id)
                
                self.status_var.set(f"已选择 {len(self.watermark_rects)} 个水印区域")
        else:
            # 进入预览
            self.preview_removal()
    
    def preview_removal(self):
        if not self.current_image_path or not self.watermark_rects:
            messagebox.showinfo("提示", "请先选择图像并标记水印区域")
            return
        
        try:
            img = self.processor._imread_safe(self.current_image_path)
            if img is None: raise ValueError(f"无法读取图像: {self.current_image_path}")
            
            # 处理水印
            result = self.processor.remove_watermark(img, self.watermark_rects)
            result_pil = Image.fromarray(result)
            
            # 缩放显示
            canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
            img_width, img_height = result_pil.size
            ratio = min(canvas_width / img_width, canvas_height / img_height)
            new_width, new_height = int(img_width * ratio), int(img_height * ratio)
            
            result_display = result_pil.resize((new_width, new_height), Image.LANCZOS)
            self.preview_photo = ImageTk.PhotoImage(result_display)
            
            self.canvas.delete("all")
            self.canvas.create_image(
                (canvas_width - new_width) // 2, 
                (canvas_height - new_height) // 2, 
                anchor=tk.NW, image=self.preview_photo
            )
            
            self.is_previewing = True
            self.preview_btn.config(text="取消预览")
            self.status_var.set("水印消除预览")
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def batch_process(self):
        if not self.input_folder or not self.output_folder or not self.watermark_rects:
            messagebox.showinfo("提示", "请先选择输入/输出文件夹并标记水印区域")
            return
        
        # 设置进度条
        self.progress_bar["maximum"] = len(self.image_paths)
        
        # 执行批量处理
        processed_count, failed_count = self.processor.batch_process(
            self.image_paths, 
            self.output_folder, 
            self.watermark_rects,
            lambda current, total, filename: self._update_progress(current, total, filename)
        )
        
        self.progress_bar["value"] = len(self.image_paths)
        self.status_var.set(f"处理完成: 成功 {processed_count} 张，失败 {failed_count} 张")
        messagebox.showinfo("完成", f"批量处理完成!\n成功: {processed_count} 张\n失败: {failed_count} 张")
    
    def _update_progress(self, current, total, filename):
        self.progress_bar["value"] = current
        self.status_var.set(f"正在处理 {current+1}/{total}")
        self.root.update()

def main():
    root = tk.Tk()
    app = WatermarkRemoverUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 