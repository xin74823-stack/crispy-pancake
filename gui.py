# 桌面程序 GUI 主入口
# 使用 PyQt5 创建现代化的聊天界面

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap, QIcon
from PyQt5.QtCore import QSize
from openai import OpenAI
from config import (
    SYSTEM_PROMPT, API_BASE_URL, API_MODEL,
    TEMPERATURE, MAX_HISTORY
)
from tools import read_diary, write_diary
from datetime import datetime


class ChatWorker(QThread):
    """后台处理线程，避免 UI 阻塞"""
    response_ready = pyqtSignal(str)
    tool_result = pyqtSignal(str, str)  # 工具名称和结果
    error_occurred = pyqtSignal(str)
    
    def __init__(self, client, conversation_history, user_input):
        super().__init__()
        self.client = client
        self.conversation_history = conversation_history
        self.user_input = user_input
    
    def run(self):
        try:
            # 检查工具触发
            tools_to_trigger = self.check_tool_trigger(self.user_input)
            tool_results = {}
            
            # 执行工具
            for tool_name in tools_to_trigger:
                result = self.call_tool(tool_name, self.user_input)
                tool_results[tool_name] = result
                self.tool_result.emit(tool_name, result)
            
            # 构建消息
            messages = self.build_messages_with_tools(
                self.conversation_history, self.user_input, tool_results
            )
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=API_MODEL,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # 更新对话历史
            self.conversation_history.append({
                "role": "user",
                "content": self.user_input
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            self.response_ready.emit(assistant_message)
        
        except Exception as e:
            self.error_occurred.emit(f"出错了呢: {str(e)}")
    
    def check_tool_trigger(self, user_message: str) -> list:
        """检查是否需要触发工具"""
        write_keywords = ["记住", "记录", "记下", "保存", "记得", "别忘了", "备忘", "笔记"]
        read_keywords = ["看日记", "回忆", "查看", "读取", "看看", "告诉我", "提醒", "之前说过"]
        
        tools_to_call = []
        
        if any(keyword in user_message for keyword in read_keywords):
            tools_to_call.append("read_diary")
        
        if any(keyword in user_message for keyword in write_keywords):
            tools_to_call.append("write_diary")
        
        return tools_to_call
    
    def extract_content_for_diary(self, user_message: str) -> str:
        """从消息中提取日记内容"""
        remove_words = ["记住", "记录", "记下", "保存", "记得", "别忘了", "备忘", "笔记", "请", "帮我"]
        
        content = user_message
        for word in remove_words:
            content = content.replace(word, "").strip()
        
        return content if content else user_message
    
    def call_tool(self, tool_name: str, user_message: str = None) -> str:
        """执行工具"""
        if tool_name == "read_diary":
            return read_diary.invoke({})
        elif tool_name == "write_diary":
            content = self.extract_content_for_diary(user_message)
            return write_diary.invoke({"content": content})
        else:
            return "工具不存在呢~"
    
    def build_messages_with_tools(self, conversation_history: list, user_input: str, tool_results: dict) -> list:
        """构建消息列表"""
        messages = []
        
        messages.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })
        
        for msg in conversation_history[-MAX_HISTORY:]:
            messages.append(msg)
        
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        if tool_results:
            tool_notification = "🔔 系统通知：\n"
            for tool_name, result in tool_results.items():
                tool_notification += f"- [{tool_name}] {result}\n"
            
            messages.append({
                "role": "system",
                "content": tool_notification
            })
        
        return messages


class MomoChatWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💕 小桃 AI助理 💕")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(self.get_stylesheet())
        
        # 初始化 API 客户端
        self.client = self.init_client()
        self.conversation_history = []
        self.worker = None
        
        # 创建 UI
        self.init_ui()
        
        # 设置窗口图标
        self.setWindowIcon(QIcon())
    
    def init_client(self):
        """初始化 API 客户端"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ 未找到 OPENAI_API_KEY 环境变量!")
        
        return OpenAI(
            api_key=api_key,
            base_url=API_BASE_URL
        )
    
    def init_ui(self):
        """初始化 UI 界面"""
        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        
        # 顶部标题
        title_label = QLabel("💕 小桃 - 你的 AI 情感伴侣 💕")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #FF69B4; padding: 10px;")
        main_layout.addWidget(title_label)
        
        # 消息显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #FFF5F7;
                border: 2px solid #FFB6D9;
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                color: #333;
            }
        """)
        self.chat_display.setFont(QFont("Arial", 11))
        main_layout.addWidget(self.chat_display)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(80)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #FFFAFC;
                border: 2px solid #FFB6D9;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                color: #333;
            }
        """)
        self.input_field.setPlaceholderText("亲爱的，你想说什么呢~ 💭")
        self.input_field.setFont(QFont("Arial", 11))
        self.input_field.keyPressEvent = self.on_input_key_press
        input_layout.addWidget(self.input_field)
        
        # 发送按钮
        self.send_btn = QPushButton("💌 发送")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
            QPushButton:pressed {
                background-color: #C71585;
            }
        """)
        self.send_btn.setMaximumWidth(100)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        main_layout.addLayout(input_layout)
        
        # 底部状态栏
        self.status_label = QLabel("准备就绪，开始聊天吧~ 💕")
        self.status_label.setStyleSheet("color: #999; font-size: 11px; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        main_widget.setLayout(main_layout)
        
        # 欢迎消息
        self.display_welcome_message()
    
    def display_welcome_message(self):
        """显示欢迎消息"""
        welcome = """
╭──────────────────────────────────────╮
│   💕 欢迎来到小桃 AI 助理系统 💕     │
│                                      │
│  我是小桃(Momo)，很高兴认识你！      │
│                                      │
│  📝 说"记住/记录"让我记下你的话     │
│  📖 说"看日记/回忆"让我讲我们故事   │
│                                      │
│  祝你今天开心呀~ 🥰                   │
╰──────────────────────────────────────╯
        """
        self.chat_display.setText(welcome)
    
    def on_input_key_press(self, event):
        """处理输入框的按键事件"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            # Ctrl+Enter 发送消息
            self.send_message()
        else:
            QTextEdit.keyPressEvent(self.input_field, event)
    
    def send_message(self):
        """发送消息"""
        user_input = self.input_field.toPlainText().strip()
        
        if not user_input:
            self.status_label.setText("请输入消息呢~ 💭")
            return
        
        # 清空输入框
        self.input_field.clear()
        
        # 禁用发送按钮
        self.send_btn.setEnabled(False)
        self.status_label.setText("小桃正在思考中... ⏳")
        
        # 添加用户消息到显示
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.append(f"\n【{timestamp}】 你: {user_input}")
        
        # 创建工作线程
        self.worker = ChatWorker(self.client, self.conversation_history, user_input)
        self.worker.response_ready.connect(self.on_response_ready)
        self.worker.tool_result.connect(self.on_tool_result)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()
    
    def on_tool_result(self, tool_name: str, result: str):
        """工具执行结果回调"""
        self.chat_display.append(f"\n🛠️ [{tool_name}]:\n{result}")
    
    def on_response_ready(self, response: str):
        """API 响应回调"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.append(f"\n【{timestamp}】 小桃: {response}")
        
        # 重新启用发送按钮
        self.send_btn.setEnabled(True)
        self.status_label.setText("可以继续聊天了~ 💕")
        
        # 自动滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def on_error(self, error_msg: str):
        """错误处理回调"""
        self.chat_display.append(f"\n❌ 小桃: {error_msg}")
        self.send_btn.setEnabled(True)
        self.status_label.setText(f"出错了呢 💔")
    
    def get_stylesheet(self) -> str:
        """获取全局样式表"""
        return """
            QMainWindow {
                background-color: #FFF0F5;
            }
            QScrollBar:vertical {
                background-color: #FFF5F7;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #FFB6D9;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #FF69B4;
            }
        """
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        event.accept()


def main():
    """主入口函数"""
    app = QApplication(sys.argv)
    
    try:
        window = MomoChatWindow()
        window.show()
        sys.exit(app.exec_())
    except ValueError as e:
        print(f"❌ {e}")
        print("请先设置 OPENAI_API_KEY 环境变量！")
        sys.exit(1)


if __name__ == "__main__":
    main()
