import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PostHandler:
    def __init__(self, driver, captcha_handler, config):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.captcha_handler = captcha_handler
        self.config = config
        self.posts_count = 0

    def get_random_text(self):
        """从一言API获取随机文本"""
        try:
            response = requests.get("https://v1.hitokoto.cn/")
            data = response.json()
            return {
                'text': data['hitokoto'],
                'from': data['from'],
                'author': data['from_who']
            }
        except Exception as e:
            print(f"获取随机文本失败: {e}")
            return None

    def fill_post_content(self, content):
        """填写发帖内容"""
        try:
            # 填写标题和描述
            input_1 = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.mdc-text-field__input"))
            )
            input_2 = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.mdc-text-field__input"))
            )
            
            # 获取编辑器iframe
            editor_frame = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[id^='ueditor_']"))
            )
            
            # 填充标题和描述
            input_1.clear()
            input_2.clear()
            input_1.send_keys(content['text'])
            input_2.send_keys(content['text'])
            
            # 切换到编辑器iframe
            self.driver.switch_to.frame(editor_frame)
            editor_body = self.driver.find_element(By.TAG_NAME, "body")
            editor_body.clear()
            editor_body.send_keys(f"{content['text']}\n来自：{content['from']}\n作者：{content['author']}")
            
            # 切回主文档
            self.driver.switch_to.default_content()
            return True
        except Exception as e:
            print(f"填写内容失败: {e}")
            return False

    def click_submit_button(self):
        """点击发布按钮"""
        try:
            # 使用多种方式查找发布按钮
            submit_btn = None
            try:
                # 方法1：通过标签文本查找
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.funny.mdc-button.mdc-button--outlined")
                for button in buttons:
                    label = button.find_element(By.CLASS_NAME, "mdc-button__label")
                    if label.text.strip() == '发布':
                        submit_btn = button
                        break
            except:
                pass

            if not submit_btn:
                # 方法2：通过完整的CSS选择器查找
                submit_btn = self.wait.until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR, 
                        "button.funny.mdc-button.mdc-button--outlined[type='button']"
                    ))
                )

            if not submit_btn:
                print("未找到发布按钮")
                return False

            print("找到发布按钮，准备点击")
            # 使用JavaScript点击按钮
            self.driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"点击发布按钮失败: {e}")
            return False

    def check_post_success(self):
        """检查发帖是否成功"""
        try:
            # 多次尝试检查验证码弹窗是否消失
            max_retries = 3
            for i in range(max_retries):
                try:
                    # 使用较短的超时时间
                    WebDriverWait(self.driver, 1).until_not(
                        EC.presence_of_element_located((By.CLASS_NAME, "shumei_captcha_popup_wrapper"))
                    )
                    print("验证码弹窗已消失")
                    return True
                except:
                    if i < max_retries - 1:  # 如果不是最后一次尝试
                        print(f"第{i+1}次检查验证码弹窗仍存在，继续检查...")
                        time.sleep(0.5)
                        continue
                    print("验证码弹窗仍然存在，发帖失败")
                    return False

        except Exception as e:
            print(f"检查发帖结果失败: {e}")
            return False

    def handle_post_result(self):
        """处理发帖结果"""
        success_flag = False  # 添加标志变量
        
        def on_success():
            nonlocal success_flag  # 使用nonlocal访问外层变量
            print("验证码验证成功，等待结果...")
            # 验证码验证成功后立即开始检查
            time.sleep(2)  # 增加等待时间
            
            # 检查发帖成功提示
            try:
                success_alert = self.wait.until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        "div.mdc-alert.mdc-alert--success"
                    ))
                )
                if success_alert and success_alert.is_displayed():
                    print("检测到发帖成功提示")
                    success_flag = True  # 设置成功标志
                else:
                    print("未检测到发帖成功提示")
            except:
                print("等待发帖成功提示超时")
        
        # 处理验证码
        if not self.captcha_handler.handle_captcha(on_success):
            return False
        
        # 检查发帖是否成功
        if not success_flag:
            print("验证码验证成功但发帖失败")
            return False
        
        # 如果发帖成功，增加计数并等待间隔
        self.posts_count += 1
        print(f"发帖成功 ({self.posts_count}/{self.config.MODULES['POST']['limit']})")
        time.sleep(self.config.MODULES['POST']['interval'])  # 发帖间隔
        return True

    def post_content(self):
        """发帖功能"""
        try:
            content = self.get_random_text()
            if not content:
                return False

            # 填写内容
            if not self.fill_post_content(content):
                return False
            
            # 点击发布按钮
            if not self.click_submit_button():
                return False
            
            # 处理验证码和发帖结果
            return self.handle_post_result()
            
        except Exception as e:
            print(f"发帖失败: {e}")
            return False

    def start_posting(self):
        """开始发帖流程"""
        try:
            # 记录当前窗口句柄
            main_window = self.driver.current_window_handle
            
            # 在新标签页中打开发帖页面
            self.driver.execute_script("window.open('https://s.yiban.cn/userPost/detail', '_blank');")
            time.sleep(1)
            
            # 切换到新标签页
            new_window = [handle for handle in self.driver.window_handles if handle != main_window][0]
            self.driver.switch_to.window(new_window)
            
            print("已在新标签页打开发帖页面")
            time.sleep(2)  # 等待页面加载
            
            # 执行发帖循环
            while self.posts_count < self.config.MODULES['POST']['limit']:
                try:
                    # 刷新页面以确保活跃状态
                    self.driver.refresh()
                    time.sleep(2)
                    
                    # 检查页面是否正常加载
                    if not self.check_page_status():
                        print("页面状态异常，重新加载...")
                        continue
                    
                    # 获取并填写内容
                    content = self.get_random_text()
                    if not content:
                        print("获取内容失败，重试...")
                        time.sleep(5)
                        continue

                    # 填写内容
                    if not self.fill_post_content(content):
                        print("填写内容失败，重试...")
                        time.sleep(5)
                        continue
                    
                    # 点击发布按钮
                    if not self.click_submit_button():
                        print("点击发布按钮失败，重试...")
                        time.sleep(5)
                        continue
                    
                    # 处理验证码和发帖结果
                    if not self.handle_post_result():
                        print("验证码处理失败，重试...")
                        time.sleep(5)
                        continue
                    
                except Exception as e:
                    print(f"发帖过程出错: {e}")
                    time.sleep(5)
                    continue
            
            print("发帖任务完成")
            
            # 关闭发帖标签页并切回主窗口
            self.driver.close()
            self.driver.switch_to.window(main_window)
            
        except Exception as e:
            print(f"发帖流程出错: {e}")
            # 尝试切回主窗口
            try:
                self.driver.switch_to.window(main_window)
            except:
                pass

    def check_page_status(self):
        """检查页面状态"""
        try:
            # 检查页面是否完全加载
            page_state = self.driver.execute_script('return document.readyState;')
            if page_state != 'complete':
                return False
            
            # 检查关键元素是否存在
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input.mdc-text-field__input"))
                )
                return True
            except:
                return False
            
        except Exception as e:
            print(f"页面状态检查失败: {e}")
            return False