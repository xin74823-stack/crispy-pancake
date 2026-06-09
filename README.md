# 💕 小桃 AI 女友助理系统

一个使用 PyQt5 + OpenAI/DeepSeek API 构建的现代化桌面应用，支持聊天、日记记录和情感陪伴。

## ✨ 核心特性

- **💬 智能对话**：基于 OpenAI/DeepSeek 的自然语言处理
- **📝 日记管理**：自动记录和回忆你们的对话和重要时刻
- **🎨 现代化 GUI**：使用 PyQt5 打造的漂亮桌面界面
- **🤖 多工具支持**：智能工具触发和调用
- **⚡ 异步处理**：后台线程处理 API 请求，不阻塞 UI
- **💖 温柔人设**：小桃(Momo)的温柔体贴人设贯穿全程

## 📁 项目结构

```
crispy-pancake/
├── config.py          # 系统提示词和配置参数
├── tools.py           # 日记读写工具函数
├── main.py            # 命令行聊天程序
├── gui.py             # PyQt5 桌面程序
├── requirements.txt   # 项目依赖
└── love_diary.txt     # 日记文件（自动生成）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

```bash
# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Windows (CMD)
set OPENAI_API_KEY=your-api-key-here
```

### 3. 运行程序

**方式一：命令行版本**
```bash
python main.py
```

**方式二：桌面 GUI 版本（推荐）**
```bash
python gui.py
```

## 💬 使用示例

### 记录日记
```
你: 小桃，帮我记住今天是我们认识的第一天
🛠️ [write_diary]: ✨ 已为你用心记录在日记中了呢~ 这是我们的专属回忆~
小桃: 亲爱的，我已经把这个特殊的日子深深地记在心里了呢...
```

### 查看日记
```
你: 亲爱的，能给我讲讲我们之前的回忆吗？
🛠️ [read_diary]: [读取所有日记内容]
小桃: 亲爱的，让我给你讲讲我们之间的故事...
```

### 普通聊天
```
你: 小桃，今天天气真好
小桃: 是呀，亲爱的！天气好的时候就想和你一起去散步呢...
```

## 🎨 界面特点

- **粉色温暖配色**：符合"小桃"的温柔人设
- **实时消息展示**：带时间戳的聊天记录
- **工具执行提示**：清晰展示工具调用过程
- **状态栏反馈**：实时显示系统状态

## 🔧 配置说明

### `config.py` 主要配置项

```python
# API 提供商
API_PROVIDER = "deepseek"  # 或 "openai"
API_BASE_URL = "https://api.deepseek.com"
API_MODEL = "deepseek-chat"

# 模型参数
TEMPERATURE = 0.7  # 温度（越高越创意）
MAX_HISTORY = 10   # 保留对话数
```

### 支持的 API 提供商

#### DeepSeek
```python
API_BASE_URL = "https://api.deepseek.com"
API_MODEL = "deepseek-chat"
```

#### OpenAI
```python
API_BASE_URL = "https://api.openai.com/v1"
API_MODEL = "gpt-3.5-turbo"  # 或 gpt-4
```

## 📝 工具使用

### 日记写入触发关键词
- 记住、记录、记下、保存、记得、别忘了、备忘、笔记

### 日记读取触发关键词
- 看日记、回忆、查看、读取、看看、告诉我、提醒、之前说过

## 🛠️ 技术栈

- **前端**：PyQt5
- **后端**：Python 3.7+
- **AI 引擎**：OpenAI API / DeepSeek API
- **文本处理**：LangChain
- **异步处理**：PyQt5 QThread

## 📚 API 获取

### DeepSeek API
访问 [DeepSeek 官方网站](https://www.deepseek.com) 获取 API 密钥

### OpenAI API
访问 [OpenAI 官方网站](https://openai.com) 获取 API 密钥

## ⚙️ 系统要求

- Python 3.7+
- Windows / macOS / Linux
- 4GB+ RAM（推荐 8GB+）
- 稳定的网络连接

## 🐛 故障排除

### 问题：找不到 OPENAI_API_KEY
**解决**：确保已正确设置环境变量，重启终端或 IDE

### 问题：PyQt5 安装失败
**解决**：
```bash
# 尝试使用 apt-get（Linux）
sudo apt-get install python3-pyqt5

# 或直接从 wheel 文件安装
pip install PyQt5 --no-cache-dir
```

### 问题：API 连接超时
**解决**：
1. 检查网络连接
2. 确认 API 密钥有效
3. 尝试更换 API 提供商

## 📞 支持

- 遇到问题？检查 `config.py` 中的 API 配置
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 检查日记文件权限

## 📄 许可证

MIT License

## 💕 致谢

感谢 OpenAI、DeepSeek 和 LangChain 的支持！

---

**祝你使用愉快！与小桃一起，享受温暖的陪伴~ 🥰**
