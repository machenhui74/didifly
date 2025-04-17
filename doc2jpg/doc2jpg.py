import os
import sys
from pdf2image import convert_from_path
import glob
from pathlib import Path
from PIL import Image
from docx2pdf import convert as docx2pdf_convert
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocToJpgConverter:
    """将PDF或Word文档转换为JPG图片的转换器"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.docx', '.doc']
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def convert_file(self, file_path, output_dir=None, dpi=300):
        """
        转换单个文件为JPG图片
        
        Args:
            file_path: 输入文件路径
            output_dir: 输出目录，默认为与输入文件相同的目录
            dpi: 输出图片的DPI值，影响图片质量
            
        Returns:
            生成的JPG文件路径列表
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return []
            
        # 如果未指定输出目录，使用输入文件所在的目录
        if output_dir is None:
            output_dir = file_path.parent
        else:
            output_dir = Path(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
        file_ext = file_path.suffix.lower()
        
        if file_ext not in self.supported_extensions:
            logger.error(f"不支持的文件类型: {file_ext}")
            return []
            
        # 获取不带扩展名的文件名
        filename = file_path.stem
        
        # 根据文件类型进行不同的处理
        if file_ext in ['.doc', '.docx']:
            return self._convert_word_to_jpg(file_path, output_dir, filename, dpi)
        elif file_ext == '.pdf':
            return self._convert_pdf_to_jpg(file_path, output_dir, filename, dpi)
    
    def _convert_word_to_jpg(self, file_path, output_dir, filename, dpi):
        """将Word文档转换为JPG"""
        logger.info(f"正在转换Word文档: {file_path}")
        
        # 首先将Word转换为PDF
        temp_pdf = os.path.join(self.temp_dir, f"{filename}.pdf")
        try:
            docx2pdf_convert(file_path, temp_pdf)
            # 然后将PDF转换为JPG
            jpg_paths = self._convert_pdf_to_jpg(temp_pdf, output_dir, filename, dpi)
            # 删除临时PDF文件
            os.remove(temp_pdf)
            return jpg_paths
        except Exception as e:
            logger.error(f"Word转换失败: {str(e)}")
            return []
    
    def _convert_pdf_to_jpg(self, file_path, output_dir, filename, dpi):
        """将PDF转换为JPG"""
        logger.info(f"正在转换PDF: {file_path}")
        
        jpg_paths = []
        try:
            # 使用pdf2image库转换PDF为图片
            images = convert_from_path(file_path, dpi=dpi)
            
            # 遍历每一页图片
            for i, image in enumerate(images):
                # 生成输出文件名
                if len(images) > 1:
                    output_filename = f"{filename}_page{i+1}.jpg"
                else:
                    output_filename = f"{filename}.jpg"
                    
                output_path = os.path.join(output_dir, output_filename)
                
                # 保存为JPG
                image.save(output_path, "JPEG")
                jpg_paths.append(output_path)
                
            logger.info(f"PDF转换完成，生成了 {len(jpg_paths)} 个JPG文件")
            return jpg_paths
            
        except Exception as e:
            logger.error(f"PDF转换失败: {str(e)}")
            return []

class DocToJpgApp:
    """文档转JPG的图形界面应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("文档转JPG工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        self.converter = DocToJpgConverter()
        self.setup_ui()
        
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="文件路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(file_frame, text="浏览文件", command=self.browse_file).grid(row=0, column=2, pady=5)
        
        # 输出目录选择
        ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.output_dir_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(file_frame, text="浏览目录", command=self.browse_output_dir).grid(row=1, column=2, pady=5)
        
        # DPI选择
        ttk.Label(file_frame, text="DPI (质量):").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.dpi_var = tk.IntVar(value=300)
        dpi_spinbox = ttk.Spinbox(file_frame, from_=72, to=600, textvariable=self.dpi_var, width=5)
        dpi_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 转换按钮
        convert_button = ttk.Button(main_frame, text="开始转换", command=self.start_conversion)
        convert_button.pack(pady=10)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W, pady=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=70, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state=tk.DISABLED)
        
        # 配置日志处理器
        self.log_handler = LogTextHandler(self.log_text)
        logger.addHandler(self.log_handler)
        
    def browse_file(self):
        filetypes = [
            ("支持的文档", "*.pdf;*.docx;*.doc"),
            ("PDF文件", "*.pdf"),
            ("Word文档", "*.docx;*.doc"),
            ("所有文件", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=filetypes)
        if file_path:
            self.file_path_var.set(file_path)
            # 默认将输出目录设置为与输入文件相同的目录
            if not self.output_dir_var.get():
                self.output_dir_var.set(os.path.dirname(file_path))
    
    def browse_output_dir(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_dir_var.set(output_dir)
    
    def start_conversion(self):
        file_path = self.file_path_var.get()
        output_dir = self.output_dir_var.get()
        dpi = self.dpi_var.get()
        
        if not file_path:
            messagebox.showerror("错误", "请选择要转换的文件")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return
            
        if not output_dir:
            output_dir = os.path.dirname(file_path)
            
        # 在新线程中执行转换，避免UI卡顿
        self.status_var.set("正在转换...")
        self.progress_var.set(0)
        
        conversion_thread = threading.Thread(
            target=self._do_conversion,
            args=(file_path, output_dir, dpi)
        )
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def _do_conversion(self, file_path, output_dir, dpi):
        try:
            # 获取文件大小，用于估算进度
            file_size = os.path.getsize(file_path)
            
            # 设置进度条为不确定状态
            self.root.after(0, lambda: self.progress_bar.config(mode="indeterminate"))
            self.root.after(0, lambda: self.progress_bar.start(10))
            
            # 执行转换
            result_files = self.converter.convert_file(file_path, output_dir, dpi)
            
            # 停止进度条动画
            self.root.after(0, lambda: self.progress_bar.stop())
            self.root.after(0, lambda: self.progress_bar.config(mode="determinate"))
            
            if result_files:
                self.root.after(0, lambda: self.progress_var.set(100))
                self.root.after(0, lambda: self.status_var.set(f"转换完成，生成了 {len(result_files)} 个JPG文件"))
                self.root.after(0, lambda: messagebox.showinfo("完成", f"转换完成，生成了 {len(result_files)} 个JPG文件"))
            else:
                self.root.after(0, lambda: self.status_var.set("转换失败"))
                self.root.after(0, lambda: messagebox.showerror("错误", "转换失败，请查看日志"))
        except Exception as e:
            logger.error(f"转换过程中出错: {str(e)}")
            self.root.after(0, lambda: self.status_var.set("转换出错"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"转换过程中出错: {str(e)}"))
            self.root.after(0, lambda: self.progress_bar.stop())
            self.root.after(0, lambda: self.progress_bar.config(mode="determinate"))

class LogTextHandler(logging.Handler):
    """将日志输出到tkinter文本框的处理器"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        msg = self.format(record)
        
        def _update():
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
            
        # 在主线程中更新UI
        self.text_widget.after(0, _update)

def main():
    """程序入口点"""
    try:
        root = tk.Tk()
        app = DocToJpgApp(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        print(f"程序启动失败: {str(e)}")

if __name__ == "__main__":
    main() 