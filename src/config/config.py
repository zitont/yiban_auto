import os
import json
import sys
import logging
from typing import Dict, List, Any, Optional

class Config:
    def __init__(self):
        # 配置日志
        self._setup_logging()
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_path = os.path.join(self.base_dir, 'config', 'config.json')
        self.template_path = os.path.join(self.base_dir, 'config', 'config.template.json')
        
        # 设置默认值
        self.set_defaults()
        
        # 加载配置文件
        self._load_config()

    def _setup_logging(self) -> None:
        """配置日志"""
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def set_defaults(self) -> None:
        """设置默认配置"""
        self.config = self._load_template() or {
            'model': {'path': 'resources/best_3.pt'}
        }
        
        self.MODULE_ORDER = [
            'LIKE',      # 先点赞
            'COMMENT',   # 再评论
            'POST'       # 最后发帖
        ]
        
        self.HEADLESS = os.environ.get('DOCKER_ENV', False) or False
        self.WINDOW_SIZE = {'width': 1920, 'height': 1080}
        self.USERNAME = ""
        self.PASSWORD = ""
        
        self.MODULES: Dict[str, Dict[str, Any]] = {
            'LIKE': {'enabled': True, 'limit': 3, 'interval': 15},
            'COMMENT': {'enabled': True, 'limit': 2, 'interval': 60},
            'POST': {'enabled': True, 'limit': 2, 'interval': 60}
        }
        
        self.DELAYS = {
            'PAGE_LOAD': 2,
            'INPUT': 0.5,
            'CHECK': 1,
            'RETRY': 5
        }

    def _load_template(self) -> Optional[Dict]:
        """加载配置模板"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置模板失败: {e}")
            return None

    def _load_config(self) -> None:
        """加载用户配置"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"配置文件不存在，将使用默认配置")
                self._create_default_config()
                return

            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                self.update_from_config(self.config)
                self.logger.info("配置加载成功")
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self.logger.info("使用默认配置")

    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            config = {
                "username": self.USERNAME,
                "password": self.PASSWORD,
                "modules": self.MODULES,
                "delays": self.DELAYS,
                "browser": {
                    "headless": self.HEADLESS,
                    "window_size": self.WINDOW_SIZE
                },
                "model": self.config.get('model', {})
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.logger.info(f"已创建默认配置文件: {self.config_path}")
        except Exception as e:
            self.logger.error(f"创建配置文件失败: {e}")

    def update_from_config(self, config: Dict) -> None:
        """从配置文件更新配置"""
        self.USERNAME = config.get('username', self.USERNAME)
        self.PASSWORD = config.get('password', self.PASSWORD)
        
        if 'modules' in config:
            for module, settings in config['modules'].items():
                if module in self.MODULES:
                    self.MODULES[module].update(settings)
        
        if 'delays' in config:
            self.DELAYS.update(config['delays'])
        
        if 'browser' in config:
            self.HEADLESS = config['browser'].get('headless', self.HEADLESS)
            if 'window_size' in config['browser']:
                self.WINDOW_SIZE.update(config['browser']['window_size'])

    @property
    def model_path(self) -> str:
        """获取模型路径"""
        relative_path = self.config.get('model', {}).get('path', 'resources/best_3.pt')
        return os.path.join(self.base_dir, relative_path)

    @property
    def class_names_path(self) -> str:
        """获取类别名称文件路径"""
        relative_path = self.config.get('model', {}).get('class_names_path', 'src/config/class_names.py')
        return os.path.join(self.base_dir, relative_path)