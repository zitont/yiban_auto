import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
from src.utils.captcha_predictor import CaptchaPredictor
from selenium.common.exceptions import TimeoutException

class CaptchaHandler:
    def __init__(self, driver, server_url='http://127.0.0.1:5000'):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.SERVER_URL = server_url
        self.bg_url = None
        # 初始化验证码识别器
        self.predictor = CaptchaPredictor()

    def predict_image(self, image_url):
        """验证码识别"""
        try:
            result = self.predictor.predict_from_url(image_url)
            if result:
                return {
                    'x': result['center'][0],
                    'y': result['center'][1]
                }
            return None
        except Exception as e:
            print(f"验证码识别失败: {e}")
            return None

    def simulate_click(self, element, x, y):
        """模拟点击验证码"""
        try:
            rect = element.rect
            print(f"\n验证码图片信息:")
            print(f"图片位置: x={rect['x']}, y={rect['y']}")
            print(f"图片大小: {rect['width']}x{rect['height']}")
            
            # 将预测的中心点坐标除以2
            click_x = x 
            click_y = y // 2
            
            print(f"\n点击坐标信息:")
            print(f"原始中心点坐标: ({x}, {y})")
            print(f"实际点击坐标: ({click_x}, {click_y})")

            # 添加点击位置的可视化标记到验证码图片容器中
            self.driver.execute_script("""
                const wrapper = arguments[0].closest('.shumei_captcha_img_loaded_bg_wrapper');
                if (wrapper) {
                    const dot = document.createElement('div');
                    dot.style.position = 'absolute';
                    dot.style.width = '10px';
                    dot.style.height = '10px';
                    dot.style.backgroundColor = 'red';
                    dot.style.borderRadius = '50%';
                    dot.style.zIndex = '10000';
                    dot.style.left = arguments[1] + 'px';
                    dot.style.top = arguments[2] + 'px';
                    dot.style.transform = 'translate(-50%, -50%)';  // 居中显示
                    wrapper.appendChild(dot);
                    setTimeout(() => dot.remove(), 1000);  // 1秒后移除标记
                }
            """, element, click_x, click_y)

            # 使用JavaScript执行点击
            script = """
                function simulateClick(element, x, y) {
                    const rect = element.getBoundingClientRect();
                    const clickX = rect.left + x;
                    const clickY = rect.top + y;
                    
                    ["mousedown", "mouseup", "click"].forEach((eventType) => {
                        const clickEvent = new MouseEvent(eventType, {
                            bubbles: true,
                            cancelable: true,
                            view: window,
                            clientX: clickX,
                            clientY: clickY
                        });
                        element.dispatchEvent(clickEvent);
                    });
                }
                simulateClick(arguments[0], arguments[1], arguments[2]);
            """
            self.driver.execute_script(script, element, click_x, click_y)
            print("点击执行完成")
            
            time.sleep(1)
            return True
        except Exception as e:
            print(f"点击失败: {e}")
            return False

    def check_success(self):
        """检查验证码结果"""
        try:
            # 等待一小段时间让验证结果显示
            time.sleep(1)
            
            # 检查验证码弹窗是否还存在
            try:
                popup = self.driver.find_element(By.CLASS_NAME, "shumei_captcha_popup_wrapper")
                if popup.is_displayed():
                    print("验证码弹窗仍然存在，验证失败")
                    return False
                else:
                    print("验证码弹窗已消失，验证成功")
                    return True
            except:
                # 找不到弹窗说明验证成功
                print("验证码弹窗已消失，验证成功")
                return True

        except Exception as e:
            print(f"检查验证结果失败: {e}")
            return False

    def handle_captcha(self, on_success=None):
        """处理验证码"""
        try:
            # 确保当前标签页处于活跃状态
            self.driver.switch_to.window(self.driver.current_window_handle)
            
            # 等待验证码弹窗出现
            time.sleep(1)  # 给弹窗一点时间加载
            
            # 使用更可靠的选择器
            try:
                # 首先等待验证码弹窗出现
                popup = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "shumei_captcha_popup_wrapper"))
                )
                
                # 然后在弹窗内查找验证码图片
                captcha_img = popup.find_element(By.CLASS_NAME, "shumei_captcha_loaded_img_bg")
                if not captcha_img.is_displayed():
                    print("验证码图片未显示")
                    return False
                    
                image_url = captcha_img.get_attribute('src')
                if not image_url:
                    print("未获取到验证码图片URL")
                    return False
                    
                print(f"验证码图片URL: {image_url}")
                
                # 避免重复处理同一个验证码
                if image_url == self.bg_url:
                    return False
                
                self.bg_url = image_url
                result = self.predict_image(image_url)
                
                if not result:
                    print("验证码识别失败，刷新重试")
                    try:
                        refresh_btn = popup.find_element(By.CLASS_NAME, "shumei_captcha_img_refresh_btn")
                        refresh_btn.click()
                        time.sleep(1)
                        return self.handle_captcha(on_success)
                    except:
                        return False
                
                print(f"识别结果: {result}")
                success = self.simulate_click(captcha_img, result['x'], result['y'])
                
                if not success:
                    print("点击失败，刷新重试")
                    try:
                        refresh_btn = popup.find_element(By.CLASS_NAME, "shumei_captcha_img_refresh_btn")
                        refresh_btn.click()
                        time.sleep(1)
                        return self.handle_captcha(on_success)
                    except:
                        return False
                
                # 等待验证结果
                time.sleep(1)  # 等待验证结果显示
                
                # 多次检查验证结果
                max_retries = 3
                for i in range(max_retries):
                    if self.check_success():
                        if on_success:
                            on_success()
                        return True
                    if i < max_retries - 1:
                        print(f"第{i+1}次检查验证结果...")
                        time.sleep(1)
                
                print("验证失败，刷新重试")
                try:
                    refresh_btn = popup.find_element(By.CLASS_NAME, "shumei_captcha_img_refresh_btn")
                    refresh_btn.click()
                    time.sleep(1)
                    return self.handle_captcha(on_success)
                except:
                    return False
                    
            except TimeoutException:
                print("验证码弹窗未出现")
                return False
                
        except Exception as e:
            print(f"验证码处理失败: {e}")
            return False 