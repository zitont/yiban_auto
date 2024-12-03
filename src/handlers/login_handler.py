import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class LoginHandler:
    def __init__(self, driver, captcha_handler, config):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.captcha_handler = captcha_handler
        self.config = config

    def login(self):
        """登录易班"""
        try:
            print("开始登录...")
            self.driver.get("https://www.yiban.cn/login")
            
            # 等待登录框加载
            account_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "account-txt"))
            )
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "password-txt"))
            )
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login-btn"))
            )

            # 输入账号密码
            account_input.clear()
            account_input.send_keys(self.config.USERNAME)
            time.sleep(0.5)
            password_input.clear()
            password_input.send_keys(self.config.PASSWORD)
            time.sleep(0.5)
            
            # 点击登录按钮
            login_button.click()
            time.sleep(1)
            
            # 处理可能出现的验证码
            def on_captcha_success():
                print("登录验证码验证成功")
                # 不需要额外操作，等待URL变化即可
                pass

            # 检查是否需要验证码
            try:
                base_dom = self.driver.find_element(By.CSS_SELECTOR, "body > div:last-child > div:nth-child(2) > div:first-child")
                if base_dom:
                    print("检测到登录验证码")
                    if not self.captcha_handler.handle_captcha(on_captcha_success):
                        print("登录验证码处理失败")
                        return False
            except:
                print("无需验证码")

            # 等待登录成功
            try:
                self.wait.until(
                    lambda driver: driver.current_url != "https://www.yiban.cn/login"
                )
                print("登录成功")
                time.sleep(2)  # 等待页面完全加载
                return True
            except TimeoutException:
                print("登录失败，请检查账号密码")
                return False

        except Exception as e:
            print(f"登录过程出错: {e}")
            return False

    def check_login_status(self):
        """检查登录状态"""
        try:
            self.driver.get("https://www.yiban.cn/")
            time.sleep(2)
            return "login" not in self.driver.current_url
        except:
            return False

    def ensure_login(self):
        """确保登录状态"""
        try:
            print("打开登录页面...")
            self.driver.get("https://www.yiban.cn/login")
            
            # 等待页面完全加载
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(2)  # 额外等待以确保页面完全加载
            
            # 检查是否已经登录
            if "login" not in self.driver.current_url:
                print("已经处于登录状态")
                return True
            
            # 如果未登录，执行登录流程
            return self.login()
            
        except Exception as e:
            print(f"登录页面加载失败: {e}")
            return False
  