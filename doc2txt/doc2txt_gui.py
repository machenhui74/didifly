import os
import docx
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import queue

def doc_to_txt(doc_path):
    """
    将doc/docx文件转换为txt文件
    
    Args:
        doc_path: doc/docx文件路径
    
    Returns:
        转换后的txt文件路径
    """
    try:
        # 打开doc文件
        doc = docx.Document(doc_path)
        
        # 提取文本内容
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        
        # 生成输出文件路径，保持原文件名，只改扩展名为.txt
        output_path = str(Path(doc_path).with_suffix('.txt'))
        
        # 写入txt文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(full_text))
        
        return output_path, None
    
    except Exception as e:
        return None, str(e)

class Doc2TxtGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Doc2Txt 文档转换工具")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建文件选择区域
        files_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 文件列表
        self.files_listbox = tk.Listbox(files_frame, selectmode=tk.EXTENDED, width=70, height=15)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 操作按钮
        buttons_frame = ttk.Frame(main_frame, padding="5")
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加文件按钮
        self.add_file_btn = ttk.Button(buttons_frame, text="添加文件", command=self.add_files)
        self.add_file_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加文件夹按钮
        self.add_folder_btn = ttk.Button(buttons_frame, text="添加文件夹", command=self.add_folder)
        self.add_folder_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空列表按钮
        self.clear_btn = ttk.Button(buttons_frame, text="清空列表", command=self.clear_files)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 递归选项
        self.recursive_var = tk.BooleanVar(value=False)
        self.recursive_check = ttk.Checkbutton(buttons_frame, text="递归处理子文件夹", variable=self.recursive_var)
        self.recursive_check.pack(side=tk.LEFT, padx=20)
        
        # 开始转换按钮
        self.convert_btn = ttk.Button(buttons_frame, text="开始转换", command=self.start_conversion)
        self.convert_btn.pack(side=tk.RIGHT, padx=5)
        
        # 进度显示
        progress_frame = ttk.Frame(main_frame, padding="5")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(progress_frame, text="转换进度:").pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 状态和日志区域
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_frame, width=80, height=10, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        # 文件列表
        self.files = []
        
        # 队列用于线程间通信
        self.queue = queue.Queue()
        self.update_timer = None
        
    def add_files(self):
        """添加单个或多个文件"""
        filetypes = [("Word文档", "*.docx *.doc"), ("所有文件", "*.*")]
        files = filedialog.askopenfilenames(title="选择Word文档", filetypes=filetypes)
        
        for file in files:
            if file.lower().endswith(('.doc', '.docx')) and file not in self.files:
                self.files.append(file)
                self.files_listbox.insert(tk.END, file)
    
    def add_folder(self):
        """添加文件夹中的文件"""
        folder = filedialog.askdirectory(title="选择包含Word文档的文件夹")
        if not folder:
            return
            
        recursive = self.recursive_var.get()
        count = 0
        
        # 遍历文件夹
        path = Path(folder)
        pattern = '**/*.doc*' if recursive else '*.doc*'
        
        for file in path.glob(pattern):
            if file.suffix.lower() in ['.doc', '.docx'] and str(file) not in self.files:
                self.files.append(str(file))
                self.files_listbox.insert(tk.END, str(file))
                count += 1
        
        if count == 0:
            messagebox.showinfo("提示", "未找到Word文档")
        else:
            messagebox.showinfo("提示", f"已添加 {count} 个Word文档")
    
    def clear_files(self):
        """清空文件列表"""
        self.files = []
        self.files_listbox.delete(0, tk.END)
    
    def start_conversion(self):
        """开始转换过程"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加要转换的Word文档")
            return
        
        # 禁用按钮
        self.add_file_btn.state(['disabled'])
        self.add_folder_btn.state(['disabled'])
        self.clear_btn.state(['disabled'])
        self.convert_btn.state(['disabled'])
        
        # 重置进度条
        self.progress_bar['maximum'] = len(self.files)
        self.progress_bar['value'] = 0
        
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "开始转换...\n")
        
        # 在新线程中执行转换
        threading.Thread(target=self.conversion_thread, daemon=True).start()
        
        # 启动定时器定期检查队列
        self.update_timer = self.root.after(100, self.check_queue)
    
    def conversion_thread(self):
        """在单独的线程中执行文件转换"""
        for i, file in enumerate(self.files):
            output_path, error = doc_to_txt(file)
            
            if error:
                log_message = f"转换失败: {file}\n错误: {error}\n"
            else:
                log_message = f"成功转换: {file} -> {output_path}\n"
            
            # 将结果放入队列
            self.queue.put((i+1, log_message))
    
    def check_queue(self):
        """检查队列中的转换结果并更新界面"""
        while not self.queue.empty():
            progress, message = self.queue.get()
            self.progress_bar['value'] = progress
            self.log_text.insert(tk.END, message)
            self.log_text.see(tk.END)  # 滚动到底部
            
            # 如果完成所有转换
            if progress == len(self.files):
                self.log_text.insert(tk.END, "所有转换任务完成！\n")
                # 恢复按钮状态
                self.add_file_btn.state(['!disabled'])
                self.add_folder_btn.state(['!disabled'])
                self.clear_btn.state(['!disabled'])
                self.convert_btn.state(['!disabled'])
                return
        
        # 继续检查队列
        self.update_timer = self.root.after(100, self.check_queue)

def main():
    root = tk.Tk()
    app = Doc2TxtGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 