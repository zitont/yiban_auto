# 易班自动化工具

一个基于 Python 的易班自动化工具，支持自动点赞、评论和发帖等功能。

## 功能特点

- 🚀 自动点赞、评论和发帖
- 🔒 验证码自动识别
- 🎯 智能操作间隔
- 📝 可配置的操作限制
- 🐳 支持 Docker 部署
- 💻 支持 Windows 本地运行

## 快速开始

### Windows 本地运行

1. 双击运行 `start.bat`
2. 首次运行会自动配置环境（下载 Python、创建虚拟环境等）
3. 根据提示编辑配置文件
4. 程序会自动开始运行

### Docker 运行

1. 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 双击运行 `start-docker.bat`
3. 根据提示编辑配置文件
4. Docker 容器会自动构建和运行

## 配置说明

配置文件位于 `config/config.json`，主要配置项：

## 自动识别

识别模块基于yolov5，支持自定义模型文件，默认使用官方提供的模型文件 `yolov5s.pt`。.pt 模型，训练后模型文件路径在 `resources/models/` 目录下。
### 配置项：


```json
{
  "username": "", // 易班账号
  "password": "", // 易班密码
  "modules": {
    "POST": {
      "enabled": true, // 是否启用发帖
      "limit": 2, // 发帖数量限制
      "interval": 60 // 发帖间隔(秒)
    },
    "COMMENT": {
      "enabled": true, // 是否启用评论
      "limit": 2, // 评论数量限制
      "interval": 60 // 评论间隔(秒)
    },
    "LIKE": {
      "enabled": true, // 是否启用点赞
      "limit": 3, // 点赞数量限制
      "interval": 15 // 点赞间隔(秒)
    }
  }
}
```
 ### 项目结构

project_root/
├── config/ # 配置文件目录
│   ├── config.template.json
│   └── config.json
├── src/ # 源代码目录
│   ├── config/ # 配置模块
│   └── utils/ # 工具模块
├── resources/ # 资源文件目录
├── logs/ # 日志目录
├── requirements.txt # Python依赖
├── Dockerfile # Docker配置
├── docker-compose.yml # Docker编排
├── start.bat # Windows启动脚本
└── start-docker.bat # Docker启动脚本

### 环境要求
Windows 本地运行
Windows 7 或更高版本
网络连接（用于下载 Python 和依赖）
2GB 以上可用内存
Docker 运行
Windows 10 或更高版本
Docker Desktop
4GB 以上可用内存
网络连接
常见问题
程序无法启动

检查网络连接
确保配置文件格式正确
查看日志文件了解详细错误信息
验证码识别失败

确保模型文件存在
检查网络连接状态
尝试重新运行程序
Docker 版本启动失败

确保 Docker Desktop 正在运行
检查 Docker 日志了解详细错误
确保端口未被占用
网络问题

检查网络连接是否稳定
尝试重启路由器或切换网络
权限问题

确保运行脚本的用户具有足够的权限
尝试以管理员身份运行脚本
注意事项
请合理设置操作间隔，避免操作过于频繁
定期检查日志文件，及时发现并处理异常
不要将账号密码提交到代码仓库
建议使用 Docker 版本以获得更稳定的运行环境
保护个人信息，不要在公共场合使用此工具
更新日志
v1.0.0 (2024-03-xx)
初始版本发布
支持基本的自动化功能
添加 Docker 支持
添加 Windows 本地运行支持
许可证
MIT License



代码风格
遵循 PEP 8 编码规范
提交信息格式：feat: 新增功能 或 fix: 修复问题
联系方式
作者：[zitont]
邮箱：[1456492197@qq.com]
项目地址：[https://github.com/zitont/yiban-auto]