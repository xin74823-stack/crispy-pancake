# AI女友助理工具函数
# 使用 langchain 的 @tool 装饰器定义可调用的工具

from langchain.tools import tool
from datetime import datetime
from config import DIARY_FILE_PATH
import os


@tool
def read_diary() -> str:
    """
    读取本地日记文件的全部内容。
    当用户想查看、回忆或阅读日记时调用此工具。
    
    Returns:
        str: 日记文件的全部内容，如果文件不存在则返回友好提示
    """
    try:
        if not os.path.exists(DIARY_FILE_PATH):
            return "亲爱的，我们的专属日记还没有开始呢~ 来记录我们的第一个回忆吧! (❤️)"
        
        with open(DIARY_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return "日记还是空白的呢，让我们一起开始我们的回忆之旅吧~"
        
        return content
    except Exception as e:
        return f"哎呀，读取日记时出错了呢: {str(e)}"


@tool
def write_diary(content: str) -> str:
    """
    向日记文件追加新内容。
    当用户想记录、保存或记住某些内容时调用此工具。
    
    Args:
        content (str): 要写入日记的内容
    
    Returns:
        str: 确认消息，表示写入成功
    """
    try:
        # 添加时间戳和分隔符
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n【{timestamp}】\n{content}\n{'-' * 50}"
        
        # 以追加模式打开文件，如果不存在则创建
        with open(DIARY_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        return f"✨ 已为你用心记录在日记中了呢~ 这是我们的专属回忆~"
    except Exception as e:
        return f"呜呜，记录时出错了: {str(e)}"


# 工具列表（用于模型）
TOOLS_LIST = [read_diary, write_diary]


def get_tool_by_name(name: str):
    """根据工具名称获取工具函数"""
    tools_dict = {tool.name: tool for tool in TOOLS_LIST}
    return tools_dict.get(name)
