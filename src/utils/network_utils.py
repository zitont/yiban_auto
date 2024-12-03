import socket
import requests
import time
from ..utils.logger import logger

class NetworkUtils:
    @staticmethod
    def check_internet_connection(timeout=3):
        """
        检查网络连接，尝试多个可靠的网站
        """
        urls = [
            "https://www.baidu.com",
            "https://www.qq.com",
            "https://www.yiban.cn"
        ]
        
        for url in urls:
            try:
                requests.get(url, timeout=timeout)
                return True
            except requests.RequestException:
                continue
        return False

    @staticmethod
    def wait_for_connection(max_retries=3, delay=5):
        """
        等待网络连接恢复
        """
        for i in range(max_retries):
            if NetworkUtils.check_internet_connection():
                logger.info("网络连接正常")
                return True
            if i < max_retries - 1:  # 只在非最后一次重试时显示等待消息
                logger.warning(f"网络连接失败，{delay}秒后重试... ({i+1}/{max_retries})")
                time.sleep(delay)
            else:
                logger.error("网络连接失败，请检查网络设置")
        return False

    @staticmethod
    def download_with_retry(url, timeout=10, max_retries=3):
        """
        带重试的下载功能
        """
        for i in range(max_retries):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if i == max_retries - 1:
                    raise
                logger.warning(f"下载失败，正在重试 ({i+1}/{max_retries}): {str(e)}")
                time.sleep(2)