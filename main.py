# AI女友助理主程序
# 实现完整的对话循环和工具调用逻辑

import os
import json
from openai import OpenAI
from config import (
    SYSTEM_PROMPT, API_BASE_URL, API_MODEL, 
    TEMPERATURE, MAX_HISTORY
)
from tools import read_diary, write_diary


# 初始化 OpenAI 客户端（支持 DeepSeek 和 OpenAI）
def init_client():
    """初始化 API 客户端"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("❌ 错误：未找到 OPENAI_API_KEY 环境变量，请先设置 API 密钥!")
    
    client = OpenAI(
        api_key=api_key,
        base_url=API_BASE_URL
    )
    return client


def check_tool_trigger(user_message: str) -> list:
    """
    检查用户消息中是否包含工具触发关键词
    返回需要调用的工具列表
    """
    # 日记写入关键词
    write_keywords = ["记住", "记录", "记下", "保存", "记得", "别忘了", "备忘", "笔记"]
    # 日记读取关键词
    read_keywords = ["看日记", "回忆", "查看", "读取", "看看", "告诉我", "提醒", "之前说过"]
    
    tools_to_call = []
    message_lower = user_message.lower()
    
    # 检查是否应该触发读取工具
    if any(keyword in user_message for keyword in read_keywords):
        tools_to_call.append("read_diary")
    
    # 检查是否应该触发写入工具
    if any(keyword in user_message for keyword in write_keywords):
        tools_to_call.append("write_diary")
    
    return tools_to_call


def extract_content_for_diary(user_message: str) -> str:
    """
    从用户消息中提取要保存到日记的内容
    移除触发词，保留核心内容
    """
    # 定义需要移除的触发词
    remove_words = ["记住", "记录", "记下", "保存", "记得", "别忘了", "备忘", "笔记", "请", "帮我"]
    
    content = user_message
    for word in remove_words:
        content = content.replace(word, "").strip()
    
    return content if content else user_message


def call_tool(tool_name: str, user_message: str = None) -> str:
    """
    执行指定的工具函数
    """
    if tool_name == "read_diary":
        return read_diary.invoke({})
    elif tool_name == "write_diary":
        content = extract_content_for_diary(user_message)
        return write_diary.invoke({"content": content})
    else:
        return "工具不存在呢~"


def build_messages_with_tools(conversation_history: list, user_input: str, tool_results: dict) -> list:
    """
    构建发送给模型的消息列表，包含工具执行结果
    """
    messages = []
    
    # 添加系统提示
    messages.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })
    
    # 添加对话历史（限制数量）
    for msg in conversation_history[-MAX_HISTORY:]:
        messages.append(msg)
    
    # 添加当前用户消息
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    # 如果有工具执行结果，作为系统通知添加
    if tool_results:
        tool_notification = "🔔 系统通知：\n"
        for tool_name, result in tool_results.items():
            tool_notification += f"- [{tool_name}] {result}\n"
        
        messages.append({
            "role": "system",
            "content": tool_notification
        })
    
    return messages


def chat(client: OpenAI, conversation_history: list, user_input: str) -> str:
    """
    处理一轮对话：检查工具触发 -> 执行工具 -> 调用API -> 返回回复
    """
    # 第一步：检查是否需要触发工具
    tools_to_trigger = check_tool_trigger(user_input)
    tool_results = {}
    
    # 第二步：执行需要的工具
    if tools_to_trigger:
        for tool_name in tools_to_trigger:
            result = call_tool(tool_name, user_input)
            tool_results[tool_name] = result
            print(f"\n🛠️ [{tool_name}] 执行结果：\n{result}\n")
    
    # 第三步：构建消息并调用 API
    messages = build_messages_with_tools(conversation_history, user_input, tool_results)
    
    try:
        response = client.chat.completions.create(
            model=API_MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=1000
        )
        
        assistant_message = response.choices[0].message.content
        
        # 第四步：更新对话历史
        conversation_history.append({
            "role": "user",
            "content": user_input
        })
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    except Exception as e:
        error_msg = f"呜呜，API 调用出错了呢: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


def main():
    """主程序入口"""
    print("=" * 60)
    print("💕 欢迎来到 AI女友助理系统 - 小桃(Momo) 💕")
    print("=" * 60)
    print("👋 我是小桃，很高兴认识你！")
    print("💬 输入任何内容与我聊天")
    print("📝 说'记住'、'记录'等词让我记下你的话")
    print("📖 说'看日记'、'回忆'等词让我给你讲我们的故事")
    print("🚪 输入 'exit' 或 'quit' 来结束对话")
    print("=" * 60 + "\n")
    
    # 初始化客户端和对话历史
    try:
        client = init_client()
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    conversation_history = []
    
    # 主对话循环
    while True:
        try:
            user_input = input("你: ").strip()
            
            # 检查退出条件
            if user_input.lower() in ["exit", "quit", "再见", "拜拜", "退出"]:
                print("\n小桃: 亲爱的，祝你今天开心哦~期待下次与你聊天! 💋")
                print("=" * 60)
                break
            
            # 跳过空输入
            if not user_input:
                print("小桃: 亲爱的，你想说什么呢~ 我在听呢 🥰\n")
                continue
            
            # 调用对话函数
            response = chat(client, conversation_history, user_input)
            print(f"\n小桃: {response}\n")
        
        except KeyboardInterrupt:
            print("\n\n小桃: 亲爱的，下次聊哦~拜拜! 💕")
            print("=" * 60)
            break
        except Exception as e:
            print(f"❌ 发生错误: {str(e)}")
            print("小桃: 呜呜，发生了点小意外，我们重新开始吧~\n")


if __name__ == "__main__":
    main()
