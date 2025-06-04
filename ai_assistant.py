import requests
import json
import time
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import QMessageBox

class AIAssistant(QObject):
    """AI智能助手 - DeepSeek API调用"""
    
    def __init__(self):
        super().__init__()
        self.api_key = ""  # 在这里填入你的DeepSeek API密钥
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.max_retries = 3
        self.retry_delay = 1  # 秒
        
    def set_api_key(self, api_key):
        """设置API密钥"""
        self.api_key = api_key.strip()
        
    def validate_api_key(self):
        """验证API密钥是否有效"""
        if not self.api_key:
            return False, "请先设置API密钥"
        
        if not self.api_key.startswith('sk-'):
            return False, "API密钥格式不正确，应该以'sk-'开头"
            
        return True, "API密钥格式正确"
    
    def generate_math_prompt(self, problem_type, difficulty, user_question):
        """生成数学问题的提示词"""
        base_prompt = """你是一个专业的数学教师和AI助手，专门帮助学生学习数学。请用简单易懂的语言回答学生的数学问题。

请遵循以下要求：
1. 回答要清晰、简洁、易于理解
2. 如果是计算题，请提供详细的解题步骤
3. 如果是概念问题，请用简单的例子说明
4. 鼓励学生思考，给出解题思路
5. 用中文回答

题目类型：{problem_type}
难度等级：{difficulty}
学生问题：{user_question}

请提供详细的解答："""
        
        return base_prompt.format(
            problem_type=problem_type,
            difficulty=difficulty,
            user_question=user_question
        )
    
    def call_deepseek_api(self, prompt, max_tokens=1000):
        """调用DeepSeek API"""
        is_valid, message = self.validate_api_key()
        if not is_valid:
            return False, message
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        }
        
        for attempt in range(self.max_retries):
            try:
                print(f"正在调用DeepSeek API (尝试 {attempt + 1}/{self.max_retries})...")
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        ai_response = result['choices'][0]['message']['content']
                        return True, ai_response
                    else:
                        return False, "API返回数据格式错误"
                        
                elif response.status_code == 401:
                    return False, "API密钥无效，请检查密钥是否正确"
                    
                elif response.status_code == 429:
                    return False, "请求过于频繁，请稍后再试"
                    
                elif response.status_code == 500:
                    if attempt < self.max_retries - 1:
                        print(f"服务器错误，{self.retry_delay}秒后重试...")
                        time.sleep(self.retry_delay)
                        continue
                    return False, "服务器内部错误，请稍后再试"
                    
                else:
                    error_msg = f"API调用失败，状态码: {response.status_code}"
                    try:
                        error_detail = response.json()
                        if 'error' in error_detail:
                            error_msg += f"，错误信息: {error_detail['error']}"
                    except:
                        pass
                    return False, error_msg
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    print(f"请求超时，{self.retry_delay}秒后重试...")
                    time.sleep(self.retry_delay)
                    continue
                return False, "请求超时，请检查网络连接"
                
            except requests.exceptions.ConnectionError:
                return False, "网络连接错误，请检查网络设置"
                
            except Exception as e:
                return False, f"未知错误: {str(e)}"
        
        return False, "多次重试后仍然失败"


class AIWorker(QThread):
    """AI调用工作线程，避免阻塞UI"""
    
    # 定义信号
    response_ready = pyqtSignal(bool, str)  # success, response
    progress_update = pyqtSignal(str)  # status message
    
    def __init__(self, ai_assistant, problem_type, difficulty, user_question):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.problem_type = problem_type
        self.difficulty = difficulty
        self.user_question = user_question
    
    def run(self):
        """在后台线程中执行AI调用"""
        try:
            # 更新进度
            self.progress_update.emit("正在生成AI提示词...")
            
            # 生成提示词
            prompt = self.ai_assistant.generate_math_prompt(
                self.problem_type, 
                self.difficulty, 
                self.user_question
            )
            
            # 更新进度
            self.progress_update.emit("正在调用DeepSeek API...")
            
            # 调用API
            success, response = self.ai_assistant.call_deepseek_api(prompt)
            
            # 发送结果
            if success:
                self.progress_update.emit("AI回答已生成完成！")
                self.response_ready.emit(True, response)
            else:
                self.progress_update.emit("AI调用失败")
                self.response_ready.emit(False, response)
                
        except Exception as e:
            self.response_ready.emit(False, f"处理过程中出现错误: {str(e)}")


class AIConfigDialog:
    """AI配置对话框"""
    
    @staticmethod
    def show_config_dialog(parent, current_api_key=""):
        """显示API密钥配置对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTextEdit
        
        dialog = QDialog(parent)
        dialog.setWindowTitle('配置DeepSeek API')
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # 说明信息
        info_label = QLabel("""
<h3>DeepSeek API 配置</h3>
<p>请在下方输入您的DeepSeek API密钥以使用AI智能助手功能。</p>
<p><b>获取API密钥的步骤：</b></p>
<ol>
<li>访问 <a href="https://platform.deepseek.com">DeepSeek官网</a></li>
<li>注册并登录账户</li>
<li>在控制台中创建API密钥</li>
<li>复制密钥并粘贴到下方输入框</li>
</ol>
<p><b>注意：</b>API密钥以"sk-"开头，请妥善保管。</p>
        """)
        info_label.setWordWrap(True)
        info_label.setOpenExternalLinks(True)
        layout.addWidget(info_label)
        
        # API密钥输入
        key_label = QLabel('API密钥:')
        key_input = QLineEdit()
        key_input.setPlaceholderText('请输入您的DeepSeek API密钥 (sk-xxx...)')
        key_input.setText(current_api_key)
        key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # 显示/隐藏密钥按钮
        show_key_btn = QPushButton('显示')
        show_key_btn.setCheckable(True)
        show_key_btn.clicked.connect(
            lambda checked: key_input.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        show_key_btn.clicked.connect(
            lambda checked: show_key_btn.setText('隐藏' if checked else '显示')
        )
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(key_input)
        key_layout.addWidget(show_key_btn)
        
        layout.addWidget(key_label)
        layout.addLayout(key_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton('测试连接')
        save_btn = QPushButton('保存')
        cancel_btn = QPushButton('取消')
        
        test_btn.clicked.connect(lambda: AIConfigDialog.test_api_key(key_input.text().strip(), dialog))
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(test_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # 返回结果
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return True, key_input.text().strip()
        else:
            return False, ""
    
    @staticmethod
    def test_api_key(api_key, parent):
        """测试API密钥"""
        if not api_key:
            QMessageBox.warning(parent, '错误', '请先输入API密钥')
            return
        
        # 显示测试中消息
        test_msg = QMessageBox(parent)
        test_msg.setWindowTitle('测试中')
        test_msg.setText('正在测试API连接，请稍候...')
        test_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
        test_msg.show()
        
        # 简单的API验证
        ai = AIAssistant()
        ai.set_api_key(api_key)
        
        try:
            success, response = ai.call_deepseek_api("请简单回答：1+1等于几？", max_tokens=50)
            test_msg.close()
            
            if success:
                QMessageBox.information(parent, '测试成功', f'API连接成功！\n\nAI回答: {response[:100]}...')
            else:
                QMessageBox.warning(parent, '测试失败', f'API连接失败：\n{response}')
                
        except Exception as e:
            test_msg.close()
            QMessageBox.critical(parent, '测试错误', f'测试过程中出现错误：\n{str(e)}')
