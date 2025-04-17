import tkinter as tk
from tkinter import messagebox
import traceback
import os
from PIL import Image, ImageTk
import io

def main():
    """主程序入口点"""
    try:
        # 创建主根窗口
        root = tk.Tk()
        root.title("训练方案生成器")
        
        # 设置窗口图标
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_dir, "app_icon.png")
            
            # 如果图标文件存在则设置
            if os.path.exists(icon_path):
                # 加载PNG图标
                icon_img = Image.open(icon_path)
                
                # 对于Windows系统，直接使用PhotoImage
                icon_tk = ImageTk.PhotoImage(icon_img)
                root.iconphoto(True, icon_tk)
                
                # 备用方法：使用wm iconphoto命令
                root.tk.call('wm', 'iconphoto', root._w, icon_tk)
        except Exception as icon_error:
            print(f"设置图标失败: {str(icon_error)}")
        
        # 延迟导入InputInterface，只在需要时才导入
        from input_interface import InputInterface
        
        # 初始化应用
        app = InputInterface(root)
        
        # 启动主循环
        root.mainloop()
    except Exception as e:
        # 如果GUI无法启动，显示错误信息
        error_msg = f"程序启动失败: {str(e)}\n\n{traceback.format_exc()}"
        try:
            messagebox.showerror("严重错误", error_msg)
        except:
            print(error_msg)
            input("按Enter键退出...")

if __name__ == "__main__":
    main() 