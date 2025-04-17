import os
import cv2
import numpy as np
from PIL import Image

class WatermarkProcessor:
    def __init__(self):
        pass
    
    def remove_watermark(self, image, watermark_rects):
        """
        从图像中移除指定区域的水印
        
        参数:
            image: 输入图像（numpy数组）
            watermark_rects: 水印区域列表，每个元素为 (x1, y1, x2, y2) 元组
            
        返回:
            处理后的图像
        """
        # 确保图像不为空
        if image.size == 0:
            raise ValueError("图像为空")
        
        # 转换为RGB用于处理
        if len(image.shape) == 3 and image.shape[2] == 3:
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            img = image.copy()
        
        # 应用所有水印区域
        for rect in watermark_rects:
            x1, y1, x2, y2 = rect
            
            # 检查水印区域是否超出图像边界
            height, width = img.shape[:2]
            x1_safe = min(max(0, x1), width-1)
            y1_safe = min(max(0, y1), height-1)
            x2_safe = min(max(0, x2), width-1)
            y2_safe = min(max(0, y2), height-1)
            
            # 如果水印区域太小，跳过
            if x1_safe >= x2_safe or y1_safe >= y2_safe:
                continue
            
            # 直接用白色覆盖水印区域
            if len(img.shape) == 3:  # 彩色图像
                img[y1_safe:y2_safe, x1_safe:x2_safe] = [255, 255, 255]  # 白色
            else:  # 灰度图像
                img[y1_safe:y2_safe, x1_safe:x2_safe] = 255  # 白色
        
        return img
    
    def batch_process(self, image_paths, output_folder, watermark_rects, callback=None):
        """
        批量处理图像
        
        参数:
            image_paths: 图像路径列表
            output_folder: 输出文件夹路径
            watermark_rects: 水印区域列表
            callback: 回调函数，用于更新进度（参数：当前索引，总数，当前文件名）
            
        返回:
            (处理成功数量, 失败数量)
        """
        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)
        
        total_images = len(image_paths)
        processed_count = 0
        failed_count = 0
        
        for i, image_path in enumerate(image_paths):
            try:
                if callback:
                    callback(i, total_images, os.path.basename(image_path))
                
                if not os.path.exists(image_path):
                    raise ValueError(f"文件不存在: {image_path}")
                
                # 读取图像
                img = self._imread_safe(image_path)
                if img is None:
                    raise ValueError(f"无法读取图像: {image_path}")
                
                # 使用水印去除方法处理图像
                result = self.remove_watermark(img, watermark_rects)
                
                # 保存结果
                output_path = os.path.join(output_folder, os.path.basename(image_path))
                
                # 如果结果是RGB格式，转换回BGR用于保存
                if len(result.shape) == 3 and result.shape[2] == 3:
                    result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
                else:
                    result_bgr = result
                
                # 获取图片扩展名
                _, ext = os.path.splitext(image_path)
                ext = ext.lower()
                
                # 根据不同格式设置保存参数
                if ext in ['.jpg', '.jpeg']:
                    # JPEG格式使用最高质量保存
                    cv2.imwrite(output_path, result_bgr, [cv2.IMWRITE_JPEG_QUALITY, 100])
                elif ext == '.png':
                    # PNG格式使用无损压缩
                    cv2.imwrite(output_path, result_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                else:
                    # 其他格式使用默认参数
                    cv2.imwrite(output_path, result_bgr)
                
                processed_count += 1
            except Exception as e:
                print(f"处理图像 {image_path} 失败: {str(e)}")
                failed_count += 1
        
        return processed_count, failed_count
    
    def _imread_safe(self, filepath):
        """安全读取图像，处理中文路径问题"""
        try:
            # 尝试直接读取
            img = cv2.imread(filepath)
            if img is not None:
                return img
                
            # 如果直接读取失败，尝试使用PIL读取然后转换
            pil_img = Image.open(filepath)
            img_array = np.array(pil_img)
            
            # 如果是RGB图像，转换为BGR (OpenCV格式)
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
            return img_array
        except Exception as e:
            print(f"读取图像失败: {str(e)}")
            return None 