import json
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()
        self.default_modules = {
            "POST": {
                "enabled": True,
                "limit": 20,
                "interval": 60
            },
            "COMMENT": {
                "enabled": True,
                "limit": 20,
                "interval": 60
            },
            "LIKE": {
                "enabled": True,
                "limit": 30,
                "interval": 15
            }
        }

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def check_credentials(self):
        """检查并更新账号信息"""
        if self.config.get('username') and self.config.get('password'):
            print(f"\n当前账号: {self.config['username']}")
            change = input("是否修改账号信息？(y/N): ").strip().lower()
            if change == 'y':
                self.config['username'] = ""
                self.config['password'] = ""
        
        if not self.config.get('username') or not self.config.get('password'):
            print("\n请输入账号信息：")
            username = input("用户名: ").strip()
            password = input("密码: ").strip()
            
            if username and password:
                self.config['username'] = username
                self.config['password'] = password
                self.save_config()
                return True
            else:
                print("账号或密码不能为空")
                return False
        return True

    def configure_modules(self):
        """配置模块设置"""
        print("\n模块配置：")
        print("1. 使用默认设置")
        print("2. 自定义设置")
        print("3. 保持当前设置")
        
        current_settings = self.config.get('modules', self.default_modules)
        print("\n当前设置:")
        for module_name, settings in current_settings.items():
            status = "启用" if settings['enabled'] else "禁用"
            if settings['enabled']:
                print(f"{module_name}: {status}, 限制: {settings['limit']}, 间隔: {settings['interval']}秒")
            else:
                print(f"{module_name}: {status}")
        
        choice = input("\n请选择 (1/2/3，默认3): ").strip() or "3"

        if choice == "1":
            # 使用默认设置
            self.config['modules'] = self.default_modules.copy()
            self.save_config()
            print("\n已应用默认设置")
            
        elif choice == "2":
            modules = current_settings.copy()
            for module_name, default_settings in self.default_modules.items():
                print(f"\n{module_name}模块设置:")
                current = modules.get(module_name, default_settings)
                
                # 是否启用
                enabled_input = input(f"是否启用{module_name}？(y/N，当前{'启用' if current['enabled'] else '禁用'}，直接回车保持当前设置): ").strip().lower()
                enabled = current['enabled']  # ��认保持当前值
                if enabled_input:
                    enabled = enabled_input == 'y'
                
                limit = current['limit']
                interval = current['interval']
                
                if enabled:
                    # 设置限制
                    limit_input = input(f"设置{module_name}数量限制 (当前{limit}，直接回车保持当前设置): ").strip()
                    if limit_input:
                        try:
                            limit = max(1, int(limit_input))
                        except ValueError:
                            print(f"输入无效，使用当前值: {limit}")
                    
                    # 设置间隔
                    interval_input = input(f"设置{module_name}间隔时间(秒) (当前{interval}，直接回车保持当前设置): ").strip()
                    if interval_input:
                        try:
                            interval = max(1, int(interval_input))
                        except ValueError:
                            print(f"输入无效，使用当前值: {interval}")
                
                modules[module_name] = {
                    "enabled": enabled,
                    "limit": limit,
                    "interval": interval
                }
            
            self.config['modules'] = modules
            self.save_config()
            print("\n已保存自定义设置")
        
        # 显示最终配置
        print("\n最终配置：")
        for module_name, settings in self.config['modules'].items():
            status = "启用" if settings['enabled'] else "禁用"
            if settings['enabled']:
                print(f"{module_name}: {status}, 限制: {settings['limit']}, 间隔: {settings['interval']}秒")
            else:
                print(f"{module_name}: {status}")

    def setup(self):
        """运行完整的配置流程"""
        if not self.check_credentials():
            logger.error("账号信息无效")
            return False
        
        self.configure_modules()
        return True 