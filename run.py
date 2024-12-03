import os
import logging
from src.utils.config_manager import ConfigManager
from src.auto_yiban import YibanAutoPost

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    # 获取配置文件路径
    config_path = os.path.join('config', 'config.json')
    
    # 初始化配置管理器
    config_manager = ConfigManager(config_path)
    
    # 运行配置流程
    if not config_manager.setup():
        print("配置失败，程序退出")
        return
    
    # 启动主程序
    try:
        bot = YibanAutoPost()
        bot.run()
    except Exception as e:
        print(f"程序运行出错: {e}")
    finally:
        if 'bot' in locals() and hasattr(bot, 'driver'):
            bot.driver.quit()

if __name__ == "__main__":
    main() 