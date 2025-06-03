import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget,
                             QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QRadioButton, QTextEdit, QMessageBox, QTabWidget,
                             QScrollArea, QGridLayout, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
            }
            QLineEdit {
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #333333;
            }
            QLineEdit:focus {
                background-color: white;
                box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
                color: #333333;
            }
            QPushButton {
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                min-width: 120px;
                text-align: center;
            }
            QPushButton#login_btn {
                background-color: #2196F3;
                border: 2px solid #1976D2;
                color: white !important;
            }
            QPushButton#login_btn:hover {
                background-color: #1976D2;
                border: 2px solid #0D47A1;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }
            QPushButton#register_btn {
                background-color: #4CAF50;
                border: 2px solid #388E3C;
                color: white !important;
            }
            QPushButton#register_btn:hover {
                background-color: #45a049;
                border: 2px solid #2E7D32;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建登录框容器
        login_container = QWidget()
        login_container.setMaximumWidth(400)
        login_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            }
        """)

        container_layout = QVBoxLayout()

        # 标题
        title = QLabel('数学练习系统')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Microsoft YaHei', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 20px;")
        container_layout.addWidget(title)

        # 用户名输入
        self.username = QLineEdit()
        self.username.setPlaceholderText('请输入用户名')
        container_layout.addWidget(self.username)

        # 密码输入
        self.password = QLineEdit()
        self.password.setPlaceholderText('请输入密码')
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        container_layout.addWidget(self.password)

        # 按钮容器
        button_layout = QHBoxLayout()

        # 登录按钮
        login_btn = QPushButton('登录')
        login_btn.setObjectName('login_btn')
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        login_btn.setText('登录')
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
                border: 2px solid #1976D2;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border: 2px solid #0D47A1;
            }
        """)

        # 注册按钮
        register_btn = QPushButton('注册')
        register_btn.setObjectName('register_btn')
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setFont(QFont('Microsoft YaHei', 14, QFont.Weight.Bold))
        register_btn.setText('注册')
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-width: 120px;
                border: 2px solid #388E3C;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #2E7D32;
            }
        """)

        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)

        container_layout.addLayout(button_layout)
        login_container.setLayout(container_layout)

        layout.addWidget(login_container)
        self.setLayout(layout)


class MainMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
            }
            QPushButton {
                padding: 20px;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                color: white;
                margin: 10px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
                transition: all 0.3s;
            }
            QPushButton:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            }
        """)

        layout = QVBoxLayout()

        # 标题
        title = QLabel('选择练习模式')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont('Microsoft YaHei', 28, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin: 30px 0; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);")
        layout.addWidget(title)

        # 按钮容器
        button_container = QWidget()
        button_layout = QGridLayout()

        # 基础练习按钮
        basic_btn = QPushButton('基础练习\n（不计时）')
        basic_btn.setObjectName('basic_btn')
        basic_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                min-height: 150px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        basic_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 计时练习按钮
        timed_btn = QPushButton('计时练习\n（限时挑战）')
        timed_btn.setObjectName('timed_btn')
        timed_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                min-height: 150px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        timed_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # AI指导按钮
        ai_guide_btn = QPushButton('AI智能指导\n（学习助手）')
        ai_guide_btn.setObjectName('ai_guide_btn')
        ai_guide_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                min-height: 150px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        ai_guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 手写批改按钮
        handwrite_btn = QPushButton('手写批改\n（作业检查）')
        handwrite_btn.setObjectName('handwrite_btn')
        handwrite_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                min-height: 150px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        handwrite_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # 添加按钮到网格布局
        button_layout.addWidget(basic_btn, 0, 0)
        button_layout.addWidget(timed_btn, 0, 1)
        button_layout.addWidget(ai_guide_btn, 1, 0)
        button_layout.addWidget(handwrite_btn, 1, 1)

        button_container.setLayout(button_layout)
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # 退出登录按钮
        logout_btn = QPushButton('退出登录')
        logout_btn.setObjectName('logout_btn')
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                max-width: 200px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(logout_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


class BasicPracticeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e3f2fd, stop: 1 #bbdefb);
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #1976D2;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #1976D2;
            }
        """)

        layout = QVBoxLayout()

        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel('基础练习模式')
        title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))

        back_btn = QPushButton('返回主菜单')
        back_btn.setObjectName('back_btn')
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(back_btn)

        layout.addLayout(title_layout)

        # 题目显示区
        question_group = QGroupBox('题目')
        question_layout = QVBoxLayout()
        self.question_label = QLabel('点击"下一题"开始练习')
        self.question_label.setFont(QFont('Microsoft YaHei', 18))
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setStyleSheet("""
            QLabel {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                min-height: 100px;
                color: #333333;
                border: 2px solid #e0e0e0;
            }
        """)
        question_layout.addWidget(self.question_label)
        question_group.setLayout(question_layout)

        # 答案输入区
        answer_group = QGroupBox('你的答案')
        answer_layout = QVBoxLayout()
        self.answer_input = QLineEdit()
        self.answer_input.setFont(QFont('Microsoft YaHei', 16))
        self.answer_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 2px solid #1976D2;
                border-radius: 8px;
                font-size: 18px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border: 3px solid #2196F3;
                box-shadow: 0 0 10px rgba(33, 150, 243, 0.3);
                color: #333;
            }
        """)
        answer_layout.addWidget(self.answer_input)
        answer_group.setLayout(answer_layout)

        # 按钮区
        button_layout = QHBoxLayout()

        prev_btn = QPushButton('上一题')
        prev_btn.setObjectName('prev_btn')
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)

        next_btn = QPushButton('下一题')
        next_btn.setObjectName('next_btn')
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        submit_btn = QPushButton('提交')
        submit_btn.setObjectName('submit_btn')
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)

        button_layout.addWidget(prev_btn)
        button_layout.addWidget(next_btn)
        button_layout.addWidget(submit_btn)

        layout.addWidget(question_group)
        layout.addWidget(answer_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class TimedPracticeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fff3e0, stop: 1 #ffe0b2);
            }
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #FF6F00;
                border-radius: 10px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: rgba(255, 255, 255, 0.95);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #FF6F00;
            }
        """)

        layout = QVBoxLayout()

        # 标题栏和计时器
        top_layout = QHBoxLayout()
        title = QLabel('计时练习模式')
        title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))

        # 计时器显示
        self.timer_display = QLabel('00:00')
        self.timer_display.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        self.timer_display.setStyleSheet("""
            QLabel {
                background-color: #FF5722;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
        """)

        back_btn = QPushButton('返回主菜单')
        back_btn.setObjectName('back_btn')
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.timer_display)
        top_layout.addWidget(back_btn)

        layout.addLayout(top_layout)

        # 题目和答案区域
        content_layout = QHBoxLayout()

        # 题目列表
        question_list_group = QGroupBox('题目列表')
        question_list_layout = QVBoxLayout()
        self.question_list = QTextEdit()
        self.question_list.setReadOnly(True)
        self.question_list.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                color: #333333;
                font-size: 16px;
                font-family: 'Microsoft YaHei';
            }
        """)
        question_list_layout.addWidget(self.question_list)
        question_list_group.setLayout(question_list_layout)

        # 答案输入区
        answer_group = QGroupBox('答案输入')
        answer_layout = QVBoxLayout()
        self.answer_area = QTextEdit()
        self.answer_area.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
                color: #333333;
            }
        """)
        answer_layout.addWidget(self.answer_area)
        answer_group.setLayout(answer_layout)

        # 添加得分显示
        score_layout = QHBoxLayout()
        self.score_label = QLabel('得分: 0 / 正确: 0 / 总题数: 0')
        self.score_label.setFont(QFont('Microsoft YaHei', 14))
        self.score_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.9);
                padding: 10px 20px;
                border-radius: 8px;
                color: #333;
                border: 2px solid #FF6F00;
            }
        """)
        score_layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(question_list_group)
        content_layout.addWidget(answer_group)

        # 控制按钮
        button_layout = QHBoxLayout()

        start_btn = QPushButton('开始计时')
        start_btn.setObjectName('start_btn')
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        submit_btn = QPushButton('提交答案')
        submit_btn.setObjectName('submit_btn')
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        button_layout.addWidget(start_btn)
        button_layout.addWidget(submit_btn)

        layout.addLayout(content_layout)
        layout.addLayout(score_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class AIGuideWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel('AI智能指导')
        title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))

        back_btn = QPushButton('返回主菜单')
        back_btn.setObjectName('back_btn')
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(back_btn)

        layout.addLayout(title_layout)

        # 主内容区
        content_layout = QHBoxLayout()

        # 左侧 - 问题输入和选项
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # 问题类型选择
        type_group = QGroupBox('选择问题类型')
        type_layout = QVBoxLayout()
        self.problem_type = QComboBox()
        self.problem_type.addItems(['加法', '减法', '乘法', '除法', '混合运算', '应用题'])
        self.problem_type.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        type_layout.addWidget(self.problem_type)
        type_group.setLayout(type_layout)

        # 难度选择
        difficulty_group = QGroupBox('选择难度')
        difficulty_layout = QVBoxLayout()
        self.difficulty = QComboBox()
        self.difficulty.addItems(['简单', '中等', '困难'])
        self.difficulty.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        difficulty_layout.addWidget(self.difficulty)
        difficulty_group.setLayout(difficulty_layout)

        # 问题输入
        question_group = QGroupBox('输入你的问题')
        question_layout = QVBoxLayout()
        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText('在这里输入你不理解的数学问题...')
        self.question_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #333333;
            }
        """)
        question_layout.addWidget(self.question_input)
        question_group.setLayout(question_layout)

        # 获取指导按钮
        get_help_btn = QPushButton('获取AI指导')
        get_help_btn.setObjectName('get_help_btn')
        get_help_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)

        left_layout.addWidget(type_group)
        left_layout.addWidget(difficulty_group)
        left_layout.addWidget(question_group)
        left_layout.addWidget(get_help_btn)
        left_panel.setLayout(left_layout)

        # 右侧 - AI回答显示
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        answer_group = QGroupBox('AI智能解答')
        answer_layout = QVBoxLayout()
        self.ai_answer = QTextEdit()
        self.ai_answer.setReadOnly(True)
        self.ai_answer.setPlaceholderText('AI的解答将显示在这里...')
        self.ai_answer.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
            }
        """)
        answer_layout.addWidget(self.ai_answer)
        answer_group.setLayout(answer_layout)

        right_layout.addWidget(answer_group)
        right_panel.setLayout(right_layout)

        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)

        layout.addLayout(content_layout)
        self.setLayout(layout)


class HandwritingCorrectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 标题栏
        title_layout = QHBoxLayout()
        title = QLabel('手写批改功能')
        title.setFont(QFont('Microsoft YaHei', 20, QFont.Weight.Bold))

        back_btn = QPushButton('返回主菜单')
        back_btn.setObjectName('back_btn')
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(back_btn)

        layout.addLayout(title_layout)

        # 主内容区
        content_layout = QHBoxLayout()

        # 左侧 - 手写板
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        canvas_group = QGroupBox('手写板')
        canvas_layout = QVBoxLayout()

        # 模拟手写板
        self.canvas = QLabel('手写区域\n（在此处书写数学题）')
        self.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px solid #333;
                border-radius: 5px;
                min-height: 400px;
                font-size: 18px;
                color: #999;
            }
        """)

        canvas_layout.addWidget(self.canvas)
        canvas_group.setLayout(canvas_layout)

        # 工具按钮
        tool_layout = QHBoxLayout()

        clear_btn = QPushButton('清空')
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)

        upload_btn = QPushButton('上传图片')
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)

        tool_layout.addWidget(clear_btn)
        tool_layout.addWidget(upload_btn)

        left_layout.addWidget(canvas_group)
        left_layout.addLayout(tool_layout)
        left_panel.setLayout(left_layout)

        # 右侧 - 批改结果
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # 识别结果
        recognition_group = QGroupBox('识别结果')
        recognition_layout = QVBoxLayout()
        self.recognition_result = QTextEdit()
        self.recognition_result.setReadOnly(True)
        self.recognition_result.setPlaceholderText('识别的数学题将显示在这里...')
        self.recognition_result.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        recognition_layout.addWidget(self.recognition_result)
        recognition_group.setLayout(recognition_layout)

        # 批改结果
        correction_group = QGroupBox('批改结果')
        correction_layout = QVBoxLayout()
        self.correction_result = QTextEdit()
        self.correction_result.setReadOnly(True)
        self.correction_result.setPlaceholderText('批改结果将显示在这里...')
        self.correction_result.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        correction_layout.addWidget(self.correction_result)
        correction_group.setLayout(correction_layout)

        # 批改按钮
        correct_btn = QPushButton('开始批改')
        correct_btn.setObjectName('correct_btn')
        correct_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        right_layout.addWidget(recognition_group)
        right_layout.addWidget(correction_group)
        right_layout.addWidget(correct_btn)
        right_panel.setLayout(right_layout)

        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)

        layout.addLayout(content_layout)
        self.setLayout(layout)


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('数学练习系统')
        self.setGeometry(100, 100, 1200, 800)

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()

        # 创建各个页面
        self.login_window = LoginWindow()
        self.main_menu_window = MainMenuWindow()
        self.basic_practice_window = BasicPracticeWindow()
        self.timed_practice_window = TimedPracticeWindow()
        self.ai_guide_window = AIGuideWindow()
        self.handwriting_window = HandwritingCorrectionWindow()

        # 添加到堆叠窗口
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.main_menu_window)
        self.stacked_widget.addWidget(self.basic_practice_window)
        self.stacked_widget.addWidget(self.timed_practice_window)
        self.stacked_widget.addWidget(self.ai_guide_window)
        self.stacked_widget.addWidget(self.handwriting_window)

        self.setCentralWidget(self.stacked_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())