import os
import requests
import zipfile
from ..utils.logger import logger
from ..utils.network_utils import NetworkUtils

class ChromeUtils:
    CHROME_DRIVER_MIRRORS = [
        "https://registry.npmmirror.com/-/binary/chromedriver/",
        "https://cdn.npm.taobao.org/dist/chromedriver/",
    ]
    
    @staticmethod
    def get_chrome_version():
        """获取本地Chrome版本"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version.split('.')[0]  # 只返回主版本号
        except:
            return None

    @staticmethod
    def download_chromedriver():
        """从镜像下载ChromeDriver"""
        chrome_version = ChromeUtils.get_chrome_version()
        if not chrome_version:
            raise Exception("无法获取Chrome版本")

        driver_dir = os.path.join(os.path.expanduser("~"), ".wdm", "drivers", "chromedriver")
        os.makedirs(driver_dir, exist_ok=True)

        for mirror in ChromeUtils.CHROME_DRIVER_MIRRORS:
            try:
                version_url = f"{mirror}{chrome_version}/chromedriver_win32.zip"
                logger.info(f"尝试从镜像下载ChromeDriver: {version_url}")
                
                response = NetworkUtils.download_with_retry(version_url)
                if not response:
                    continue

                zip_path = os.path.join(driver_dir, "chromedriver.zip")
                with open(zip_path, 'wb') as f:
                    f.write(response.content)

                # 解压文件
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(driver_dir)

                driver_path = os.path.join(driver_dir, "chromedriver.exe")
                logger.info(f"ChromeDriver 下载成功: {driver_path}")
                return driver_path

            except Exception as e:
                logger.warning(f"从镜像 {mirror} 下载失败: {str(e)}")
                continue

        raise Exception("无法从任何镜像下载ChromeDriver") 