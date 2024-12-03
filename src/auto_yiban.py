import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from chromedriver_py import binary_path
from webdriver_manager.chrome import ChromeDriverManager

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.handlers.captcha_handler import CaptchaHandler
from src.handlers.post_handler import PostHandler
from src.handlers.comment_handler import CommentHandler
from src.handlers.like_handler import LikeHandler
from src.handlers.login_handler import LoginHandler
from src.config import Config
from selenium.webdriver.chrome.service import Service

def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class YibanAutoPost:
    def __init__(self):
        # 初始化配置
        self.config = Config()
        
        # 初始化浏览器
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # 添加无头模式配置
        if self.config.HEADLESS:  # 在config中添加HEADLESS选项
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')  # 设置窗口大小
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 避免被检测
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            print(f"使用Chrome驱动: {binary_path}")
            service = Service(binary_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 修改navigator.webdriver标记
            if self.config.HEADLESS:
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
                })
            
            self.wait = WebDriverWait(self.driver, 10)
        except Exception as e:
            print(f"Chrome驱动加载失败: {e}")
            raise

        # 初始化各个处理器
        model_path = get_resource_path('best_2.pt')
        self.captcha_handler = CaptchaHandler(self.driver)
        self.captcha_handler.predictor.model_path = model_path
        self.login_handler = LoginHandler(self.driver, self.captcha_handler, self.config)
        self.post_handler = PostHandler(self.driver, self.captcha_handler, self.config)
        self.comment_handler = CommentHandler(self.driver, self.captcha_handler, self.config)
        self.like_handler = LikeHandler(self.driver, self.captcha_handler, self.config)

    def run(self):
        """运行主程序"""
        try:
            # 先尝试登录
            print("检查登录状态...")
            login_success = False
            max_retries = 3
            retry_count = 0

            while not login_success and retry_count < max_retries:
                if retry_count > 0:
                    print(f"第{retry_count}次重试登录...")
                    time.sleep(5)
                
                login_success = self.login_handler.ensure_login()
                retry_count += 1

            if not login_success:
                print("多次登录尝试失败，程序退出")
                return

            print("登录成功，等待页面加载...")
            time.sleep(self.config.DELAYS['PAGE_LOAD'])

            # 再次确认登录状态
            if not self.login_handler.check_login_status():
                print("登录状态异常，程序退出")
                return

            # 保存主窗口句柄
            main_window = self.driver.current_window_handle

            try:
                # 按顺序执行各个功能模块
                for module_name in self.config.MODULE_ORDER:
                    module_config = self.config.MODULES[module_name]
                    if not module_config['enabled']:
                        print(f"跳过{module_name}模块（未启用）")
                        continue

                    print(f"\n{'='*20} 开始{module_name}模块 {'='*20}")
                    
                    if module_name == 'POST':
                        print(f"开始发帖流程... (限制{module_config['limit']}次)")
                        self.post_handler.start_posting()
                        
                    elif module_name == 'COMMENT':
                        print(f"开始评论流程... (限制{module_config['limit']}次)")
                        self.comment_handler.start_commenting()
                        
                    elif module_name == 'LIKE':
                        print(f"开始点赞流程... (限制{module_config['limit']}次)")
                        self.like_handler.start_liking()
                    
                    print(f"{'='*20} {module_name}模块完成 {'='*20}\n")
                    
            finally:
                # 确保关闭所有其他窗口，只保留主窗口
                for handle in self.driver.window_handles:
                    if handle != main_window:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                self.driver.switch_to.window(main_window)

        except Exception as e:
            print(f"运行出错: {e}")
        finally:
            print("程序结束，关闭浏览器")
            self.driver.quit()

if __name__ == "__main__":
    bot = None
    try:
        bot = YibanAutoPost()
        bot.run()  # 直接运行，根据配置决定执行哪些功能
    except Exception as e:
        print(f"程序异常退出: {e}")
    finally:
        if bot and bot.driver:
            try:
                bot.driver.quit()
            except:
                pass