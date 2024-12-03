import time
import json
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LikeHandler:
    def __init__(self, driver, captcha_handler, config):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.captcha_handler = captcha_handler
        self.config = config
        self.likes_count = 0
        self.MAX_LIKES = self.config.MODULES['LIKE']['limit']
        self.processed_posts = set()  # 记录已处理过的帖子ID

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
            
            # 获取当前的cookies
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            
            # 使用requests发送请求
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

    def get_user_id(self, post_id):
        """获取帖子作者ID"""
        try:
            url = "https://s.yiban.cn/api/forum/primaryComment"
            params = {
                'postId': post_id,
                'offset': 0,
                'count': 20
            }
            
            # 获取当前的cookies
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            
            # 使用requests发送请求
            response = requests.get(
                url,
                params=params,
                cookies=cookies,
                headers={
                    'User-Agent': self.driver.execute_script("return navigator.userAgent"),
                    'Referer': f'https://s.yiban.cn/app/2006794/post-detail/{post_id}',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('status') and data.get('data', {}).get('topic', {}).get('user', {}).get('id'):
                    return data['data']['topic']['user']['id']
            return None
            
        except Exception as e:
            print(f"获取用户ID失败: {e}")
            return None

    def like_post(self, post_id, user_id):
        """点赞帖子"""
        try:
            url = "https://s.yiban.cn/api/post/thumb"
            data = {
                'action': 'up',
                'postId': post_id,
                'userId': user_id
            }
            
            # 获取当前的cookies
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
            
            # 使用requests发送请求
            response = requests.post(
                url,
                json=data,
                cookies=cookies,
                headers={
                    'User-Agent': self.driver.execute_script("return navigator.userAgent"),
                    'Referer': f'https://s.yiban.cn/app/2006794/post-detail/{post_id}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and data.get('status'):
                    print(f"点赞成功: {post_id}")
                    return True
                else:
                    print(f"点赞失败: {data.get('message', '未知错误')}")
            return False
            
        except Exception as e:
            print(f"点赞请求失败: {e}")
            return False

    def handle_like_result(self, post_id, user_id):
        """处理点赞结果"""
        try:
            # 检查是否达到点赞次数限制
            if self.likes_count >= self.MAX_LIKES:
                print(f"已达到点赞次数限制: {self.MAX_LIKES}")
                return False

            # 直接执行点赞
            if self.like_post(post_id, user_id):
                self.likes_count += 1
                self.processed_posts.add(post_id)
                print(f"点赞成功 ({self.likes_count}/{self.MAX_LIKES})")
                time.sleep(self.config.MODULES['LIKE']['interval'])  # 使用配置的间隔时间
                return True
            return False
        except Exception as e:
            print(f"点赞处理失败: {e}")
            return False

    def start_liking(self):
        """开始点赞流程"""
        try:
            print(f"开始点赞任务，目标次数: {self.MAX_LIKES}")
            offset = 0
            while self.likes_count < self.MAX_LIKES:
                # 获取帖子列表
                posts = self.get_post_list(offset=offset)
                if not posts:
                    print("没有更多帖子了")
                    break
                
                for post in posts:
                    if self.likes_count >= self.MAX_LIKES:
                        break
                        
                    post_id = post.get('id')
                    if not post_id or post_id in self.processed_posts:
                        continue
                    
                    # 获取用户ID
                    user_id = self.get_user_id(post_id)
                    if not user_id:
                        continue
                    
                    # 处理点赞
                    if not self.handle_like_result(post_id, user_id):
                        print(f"处理帖子点赞失败: {post_id}")
                        continue
                    
                    time.sleep(2)  # 等待一下再继续
                
                offset += len(posts)
                
        except Exception as e:
            print(f"点赞流程出错: {e}")