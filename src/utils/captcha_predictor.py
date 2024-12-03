import cv2
import numpy as np
from ultralytics import YOLO
import requests
import logging
import os
from ..config import config
from ..config.class_names import CLASS_NAMES


class CaptchaPredictor:
    def __init__(self, model_path=None):
        # 配置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 从配置文件获取默认模型路径
        if model_path is None:
            model_path = config.model_path
        
        # 从配置文件获取类别名称列表
        self.class_names = CLASS_NAMES

        # 加载模型
        try:
            self.logger.info(f"加载模型: {model_path}")
            self.model = YOLO(model_path)
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            raise

    def download_image(self, image_url):
        """下载图片"""
        try:
            response = requests.get(image_url)
            if response.status_code != 200:
                raise Exception(f"图片下载失败: {image_url}")
            img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                raise Exception("图片解码失败")
            return img
        except Exception as e:
            self.logger.error(f"图片下载或解码错误: {e}")
            raise

    def predict_image(self, img):
        """预测图片"""
        try:
            # 调整图片大小
            img = cv2.resize(img, (600, 600))
            
            # 模型预测
            results = self.model.predict(source=img)
            
            # 找出最小面积的目标
            min_area = float('inf')
            min_detection = None
            
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0]]
                    area = (x2 - x1) * (y2 - y1)
                    if area < min_area:
                        min_area = area
                        center_x = ((x1 + x2) // 2) // 2
                        center_y = ((y1 + y2) // 2) // 2
                        self.logger.info(f"检测到目标: {self.class_names[int(box.cls)]}")
                        self.logger.info(f"边界框坐标: ({x1}, {y1}), ({x2}, {y2})")
                        self.logger.info(f"中心点坐标: ({center_x}, {center_y})")
                        self.logger.info(f"目标面积: {area}")
                        
                        min_detection = {
                            'confidence': float(box.conf),
                            'bbox': [x1, y1, x2, y2],
                            'center': [center_x, center_y],
                            'class_name': self.class_names[int(box.cls)],
                            'top_left': [(x1 / 2), (y1 / 2)]
                        }
            
            return min_detection
            
        except Exception as e:
            self.logger.error(f"预测失败: {e}")
            return None

    def predict_from_url(self, image_url):
        """从URL预测图片"""
        try:
            img = self.download_image(image_url)
            result = self.predict_image(img)
            if result is None:
                raise Exception("未检测到目标")
            return result
        except Exception as e:
            self.logger.error(f"预测失败: {e}")
            return None 