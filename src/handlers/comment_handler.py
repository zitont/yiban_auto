import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CommentHandler:
    def __init__(self, driver, captcha_handler, config):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.captcha_handler = captcha_handler
        self.config = config
        self.comments_count = 0
        self.processed_posts = set()  # 记录已评论过的帖子
        self.MAX_COMMENTS = self.config.MODULES['COMMENT']['limit']

    def get_post_list(self, offset=0, count=10):
        """获取帖子列表"""
        try:
            url = "https://s.yiban.cn/api/forum/getListByBoard"
            params = {
                'offset': offset,
                'count': count,
                'boardId': '2Q7ilwXrebzMlyL',
                'order': '',
                'orgId': '2006794'
            }
            
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            
            response = requests.get(
                url,
                params=params,
                cookies=cookies,
                headers={
                    'User-Agent': self.driver.execute_script("return navigator.userAgent"),
                    'Referer': 'https://s.yiban.cn/userPost/',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('status') and data.get('data', {}).get('list'):
                    return data['data']['list']
            return []
            
        except Exception as e:
            print(f"获取帖子列表失败: {e}")
            return []

    def post_comment(self, post_id):
        """评论功能"""
        try:
            # 检查是否达到评论次数限制
            if self.comments_count >= self.MAX_COMMENTS:
                print(f"已达到评论次数限制: {self.MAX_COMMENTS}")
                return False

            # 打开帖子页面
            post_url = f"https://s.yiban.cn/app/2006794/post-detail/{post_id}"
            self.driver.get(post_url)
            time.sleep(2)  # 等待页面加载

            # 点击评论触发区域
            trigger_area = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.trigger-area"))
            )
            trigger_area.click()

            # 等待输入框出现并输入评论
            comment_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.input-area input[type='text']"))
            )
            comment_input.clear()
            comment_input.send_keys("好文章，支持！")

            # 点击发送按钮
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.submit-btn.btn"))
            )

            # 在点击发送按钮之前定义成功回调
            def on_success():
                """验证码验证成功后的处理"""
                print("验证码验证成功，评论成功")
                self.comments_count += 1
                self.processed_posts.add(post_id)
                print(f"评论成功 ({self.comments_count}/{self.MAX_COMMENTS})")
                time.sleep(self.config.MODULES['COMMENT']['interval'])
                return True

            # 点击发送按钮
            submit_btn.click()
            time.sleep(1)  # 等待验证码出现

            # 检查是否出现验证码
            try:
                popup = self.driver.find_element(By.CLASS_NAME, "shumei_captcha_popup_wrapper")
                if popup.is_displayed():
                    print("检测到验证码，开始处理...")
                    if not self.captcha_handler.handle_captcha(on_success):
                        print("验证码处理失败")
                        return False
                    return True  # 如果验证码处理成功，直接返回True
                else:
                    print("无需验证码")
                    # 直接执行成功回调
                    return on_success()
            except:
                print("无需验证码")
                # 直接执行成功回调
                return on_success()

            return True

        except Exception as e:
            print(f"评论失败: {e}")
            return False

    def start_commenting(self):
        """开始评论流程"""
        try:
            print(f"开始评论任务，目标次数: {self.MAX_COMMENTS}")
            offset = 0
            while self.comments_count < self.MAX_COMMENTS:
                # 获取帖子列表
                posts = self.get_post_list(offset=offset)
                if not posts:
                    print("没有更多帖子了")
                    break
                
                for post in posts:
                    if self.comments_count >= self.MAX_COMMENTS:
                        print(f"已完成评论任务，共评论 {self.comments_count} 次")
                        return
                        
                    post_id = post.get('id')
                    if not post_id or post_id in self.processed_posts:
                        continue
                    
                    # 处理评论
                    if not self.post_comment(post_id):
                        print(f"处理帖子评论失败: {post_id}")
                        time.sleep(5)  # 失败后等待一段时间
                        continue
                    
                    print(f"当前评论进度: {self.comments_count}/{self.MAX_COMMENTS}")
                    time.sleep(2)  # 成功后等待一下再继续
                
                offset += len(posts)
                
            print(f"评论任务完成，共评论 {self.comments_count} 次")
            
        except Exception as e:
            print(f"评论流程出错: {e}") 