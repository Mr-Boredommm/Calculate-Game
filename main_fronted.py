import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog, QPushButton, QCheckBox, QRadioButton, QSpinBox, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from new_ui import MainApplication
from random import randint, choice

# 导入OCR相关模块
try:
    from OCR import OCRGrader
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("警告: OCR模块未能正确导入，手写批改功能将使用模拟模式")

# 添加AI助手导入
try:
    from ai_assistant import AIAssistant, AIWorker, AIConfigDialog
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("警告: AI助手模块未能正确导入，AI功能将不可用")

class MathPracticeSystem(MainApplication):
    """数学练习系统 - 整合Game.py逻辑和前端UI"""

    def __init__(self):
        super().__init__()
        # 初始化数据文件路径
        self.data_file = 'user_data.json'
        self.current_user = None
        self.current_answers = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.time_elapsed = 0

        # 基础练习相关变量
        self.practice_history = []  # 存储练习历史 [(problem, answer, user_answer), ...]
        self.current_problem_index = -1  # 当前题目索引
        self.basic_score = 0  # 基础练习得分
        self.basic_correct = 0  # 基础练习正确数
        self.basic_total = 0  # 基础练习总题数
        self.problem_scored = []  # 记录每题是否已计分
        self.basic_start_time = 0  # 基础练习开始时间
        self.basic_timer = QTimer(self)  # 基础练习计时器
        self.basic_timer.timeout.connect(self.update_basic_timer)

        # 计时练习相关变量
        self.timed_score = 0  # 得分
        self.timed_correct = 0  # 正确数
        self.timed_total = 0  # 总题数

        # OCR相关变量
        self.ocr_grader = None
        self.current_image_path = None

        # AI助手相关变量
        self.ai_assistant = None
        self.ai_worker = None
        self.api_key_file = 'deepseek_api_key.txt'

        # 初始化OCR批改器
        if OCR_AVAILABLE:
            try:
                self.ocr_grader = OCRGrader()
                print("OCR批改器初始化成功")
            except Exception as e:
                print(f"OCR批改器初始化失败: {e}")
                self.ocr_grader = None

        # 初始化AI助手
        if AI_AVAILABLE:
            try:
                self.ai_assistant = AIAssistant()
                self.load_api_key()
                print("AI助手初始化成功")
            except Exception as e:
                print(f"AI助手初始化失败: {e}")
                self.ai_assistant = None

        # 初始化用户数据
        self.load_user_data()

        # 设置所有连接
        self.setup_connections()

    def load_api_key(self):
        """加载保存的API密钥"""
        try:
            if os.path.exists(self.api_key_file):
                with open(self.api_key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key and self.ai_assistant:
                        self.ai_assistant.set_api_key(api_key)
                        print("已加载保存的API密钥")
        except Exception as e:
            print(f"加载API密钥失败: {e}")

    def save_api_key(self, api_key):
        """保存API密钥"""
        try:
            with open(self.api_key_file, 'w', encoding='utf-8') as f:
                f.write(api_key)
            print("API密钥已保存")
        except Exception as e:
            print(f"保存API密钥失败: {e}")

    def load_user_data(self):
        """加载用户数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.user_data = json.load(f)
            except:
                self.user_data = {}
        else:
            self.user_data = {}

    def save_user_data(self):
        """保存用户数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存用户数据失败: {e}")

    def setup_connections(self):
        """设置所有按钮连接"""
        # 登录窗口按钮
        try:
            login_btn = self.login_window.findChild(QPushButton, 'login_btn')
            register_btn = self.login_window.findChild(QPushButton, 'register_btn')
            if login_btn:
                login_btn.clicked.connect(self.handle_login)
            if register_btn:
                register_btn.clicked.connect(self.handle_register)
        except:
            pass

        # 主菜单窗口按钮
        try:
            basic_btn = self.main_menu_window.findChild(QPushButton, 'basic_btn')
            timed_btn = self.main_menu_window.findChild(QPushButton, 'timed_btn')
            ai_guide_btn = self.main_menu_window.findChild(QPushButton, 'ai_guide_btn')
            handwrite_btn = self.main_menu_window.findChild(QPushButton, 'handwrite_btn')
            logout_btn = self.main_menu_window.findChild(QPushButton, 'logout_btn')

            if basic_btn:
                basic_btn.clicked.connect(self.show_basic_practice)
            if timed_btn:
                timed_btn.clicked.connect(self.show_timed_practice)
            if ai_guide_btn:
                ai_guide_btn.clicked.connect(self.show_ai_guide)
            if handwrite_btn:
                handwrite_btn.clicked.connect(self.show_handwriting)
            if logout_btn:
                logout_btn.clicked.connect(self.handle_logout)
        except:
            pass

        # 基础练习窗口按钮
        try:
            back_btn = self.basic_practice_window.findChild(QPushButton, 'back_btn')
            prev_btn = self.basic_practice_window.findChild(QPushButton, 'prev_btn')
            next_btn = self.basic_practice_window.findChild(QPushButton, 'next_btn')
            submit_btn = self.basic_practice_window.findChild(QPushButton, 'submit_btn')
            start_btn = self.basic_practice_window.findChild(QPushButton, 'start_basic_btn')
            check_btn = self.basic_practice_window.findChild(QPushButton, 'check_btn')

            if back_btn:
                back_btn.clicked.connect(self.back_to_main_menu)
            if prev_btn:
                prev_btn.clicked.connect(self.show_previous_problem)
            if next_btn:
                next_btn.clicked.connect(self.generate_basic_problem)
            if submit_btn:
                submit_btn.clicked.connect(self.submit_basic_practice)
            if start_btn:
                start_btn.clicked.connect(self.start_basic_practice)
            if check_btn:
                check_btn.clicked.connect(self.check_basic_answer)
        except:
            pass

        # 计时练习窗口按钮
        try:
            timed_back_btn = self.timed_practice_window.findChild(QPushButton, 'back_btn')
            timed_start_btn = self.timed_practice_window.findChild(QPushButton, 'start_btn')
            timed_submit_btn = self.timed_practice_window.findChild(QPushButton, 'submit_btn')

            if timed_back_btn:
                timed_back_btn.clicked.connect(self.back_to_main_menu)
            if timed_start_btn:
                timed_start_btn.clicked.connect(self.start_timed_practice)
            if timed_submit_btn:
                timed_submit_btn.clicked.connect(self.submit_timed_answers)
        except:
            pass

        # AI指导窗口按钮
        try:
            ai_back_btn = self.ai_guide_window.findChild(QPushButton, 'back_btn')
            get_help_btn = self.ai_guide_window.findChild(QPushButton, 'get_help_btn')

            if ai_back_btn:
                ai_back_btn.clicked.connect(self.back_to_main_menu)
            if get_help_btn:
                get_help_btn.clicked.connect(self.get_ai_help)  # 改为真实的AI功能

            # 查找配置按钮（如果存在）
            config_btn = self.ai_guide_window.findChild(QPushButton, 'config_btn')
            if config_btn:
                config_btn.clicked.connect(self.show_ai_config)
        except:
            pass

        # 手写批改窗口按钮
        try:
            hw_back_btn = self.handwriting_window.findChild(QPushButton, 'back_btn')
            correct_btn = self.handwriting_window.findChild(QPushButton, 'correct_btn')

            if hw_back_btn:
                hw_back_btn.clicked.connect(self.back_to_main_menu)
            if correct_btn:
                correct_btn.clicked.connect(self.start_ocr_correction)

            # 手写批改窗口的其他按钮 - 动态查找按钮
            handwriting_buttons = self.handwriting_window.findChildren(QPushButton)
            for btn in handwriting_buttons:
                if '上传' in btn.text() or 'upload' in btn.objectName().lower():
                    btn.clicked.connect(self.upload_image)
                elif '清空' in btn.text() or 'clear' in btn.objectName().lower():
                    btn.clicked.connect(self.clear_canvas)
        except:
            pass

    def get_selected_operations(self):
        """获取用户选择的运算类型"""
        operations = []
        try:
            # 尝试查找复选框（假设它们存在于基础练习窗口中）
            add_check = self.basic_practice_window.findChild(QCheckBox, 'add_checkbox')
            sub_check = self.basic_practice_window.findChild(QCheckBox, 'subtract_checkbox')
            mul_check = self.basic_practice_window.findChild(QCheckBox, 'multiply_checkbox')
            div_check = self.basic_practice_window.findChild(QCheckBox, 'divide_checkbox')

            if add_check and add_check.isChecked():
                operations.append('+')
            if sub_check and sub_check.isChecked():
                operations.append('-')
            if mul_check and mul_check.isChecked():
                operations.append('*')
            if div_check and div_check.isChecked():
                operations.append('/')
        except:
            pass

        # 如果没有选择任何运算类型，默认包含所有类型
        if not operations:
            operations = ['+', '-', '*', '/']

        return operations

    def get_selected_difficulty(self):
        """获取用户选择的难度等级"""
        try:
            # 尝试查找难度单选按钮
            easy_radio = self.basic_practice_window.findChild(QRadioButton, 'easy_radio')
            medium_radio = self.basic_practice_window.findChild(QRadioButton, 'medium_radio')
            hard_radio = self.basic_practice_window.findChild(QRadioButton, 'hard_radio')

            if easy_radio and easy_radio.isChecked():
                return 'easy'
            elif hard_radio and hard_radio.isChecked():
                return 'hard'
            else:
                return 'medium'  # 默认中等难度
        except:
            return 'medium'

    def generate_problem(self, difficulty='medium', operations=None):
        """生成单个数学题（改进版）"""
        if operations is None:
            operations = ['+', '-', '*', '/']

        # 随机选择运算符
        op = choice(operations)
        fdict = {'+': '+', '-': '-', '*': '*', '/': '/'}

        a, b, ans = 0, 0, 0

        # 根据难度调整数字范围
        if difficulty == 'easy':
            max_num = 20
            max_mul = 10
        elif difficulty == 'medium':
            max_num = 50
            max_mul = 20
        else:  # hard
            max_num = 100
            max_mul = 30

        if op == '/':  # 除法确保结果为整数
            b = randint(1, max_mul)
            ans = randint(1, 10)
            a = b * ans
        else:
            if op == '*':  # 乘法
                a = randint(1, max_mul)
                b = randint(1, max_mul)
                ans = a * b
            else:  # 加法或减法
                a = randint(1, max_num)
                b = randint(1, max_num)
                if op == '+':
                    ans = a + b
                elif op == '-':
                    # 确保减法结果为正数
                    if a < b:
                        a, b = b, a
                    ans = a - b

        problem = f'{a} {fdict[op]} {b} = ?'
        return problem, ans

    def generate_multiple_problems(self, count=10):
        """生成多个数学题（来自Game.py）"""
        problems = []
        answers = []
        for _ in range(count):
            problem, answer = self.generate_problem()
            problems.append(problem)
            answers.append(answer)
        return problems, answers

    def show_basic_practice(self):
        """显示基础练习界面"""
        self.stacked_widget.setCurrentWidget(self.basic_practice_window)
        # 重置练习状态
        self.practice_history = []
        self.current_problem_index = -1
        self.basic_score = 0
        self.basic_correct = 0
        self.basic_total = 0
        self.problem_scored = []
        self.basic_start_time = 0

        # 重置计时器显示
        try:
            timer_label = self.basic_practice_window.findChild(QLabel, 'timer_label')
            if timer_label:
                timer_label.setText('用时: 00:00')
        except:
            pass

        # 更新得分显示
        self.update_basic_score_display()

        # 显示欢迎信息
        try:
            self.basic_practice_window.question_label.setText('欢迎来到基础练习！\n请选择难度和题型，然后点击"开始练习"')
            self.basic_practice_window.answer_input.clear()
        except:
            pass

    def start_basic_practice(self):
        """开始基础练习"""
        # 重置状态
        self.practice_history = []
        self.current_problem_index = -1
        self.basic_score = 0
        self.basic_correct = 0
        self.basic_total = 0
        self.problem_scored = []

        # 开始计时
        self.basic_start_time = 0
        self.basic_timer.start(1000)  # 每秒更新一次

        # 生成第一道题目
        self.generate_basic_problem()

        QMessageBox.information(self, '开始练习', '基础练习已开始！\n计时已启动，加油！')

    def update_basic_timer(self):
        """更新基础练习计时器"""
        self.basic_start_time += 1
        minutes = self.basic_start_time // 60
        seconds = self.basic_start_time % 60

        try:
            timer_label = self.basic_practice_window.findChild(QLabel, 'timer_label')
            if timer_label:
                timer_label.setText(f'用时: {minutes:02d}:{seconds:02d}')
        except:
            pass

    def generate_basic_problem(self):
        """为基础练习生成新题目"""
        # 在切换题目前，保存当前题目的答案
        if self.current_problem_index >= 0 and self.current_problem_index < len(self.practice_history):
            user_input = self.basic_practice_window.answer_input.text().strip()
            if user_input:
                try:
                    user_answer = int(user_input)
                    problem, answer, _ = self.practice_history[self.current_problem_index]
                    self.practice_history[self.current_problem_index] = (problem, answer, user_answer)
                except ValueError:
                    pass

        # 如果当前不是最后一题，直接显示下一题
        if self.current_problem_index < len(self.practice_history) - 1:
            self.current_problem_index += 1
            problem, answer, user_answer = self.practice_history[self.current_problem_index]
            self.current_answers = [answer]
            self.basic_practice_window.question_label.setText(problem)

            # 显示之前保存的答案
            if user_answer is not None:
                self.basic_practice_window.answer_input.setText(str(user_answer))
            else:
                self.basic_practice_window.answer_input.clear()

            self.basic_practice_window.answer_input.setFocus()
        else:
            # 生成新题目
            operations = self.get_selected_operations()
            difficulty = self.get_selected_difficulty()
            problem, answer = self.generate_problem(difficulty, operations)

            self.current_answers = [answer]
            self.practice_history.append((problem, answer, None))
            self.problem_scored.append(False)  # 新题目未计分
            self.current_problem_index = len(self.practice_history) - 1
            self.basic_practice_window.question_label.setText(problem)
            self.basic_practice_window.answer_input.clear()
            self.basic_practice_window.answer_input.setFocus()

    def check_basic_answer(self):
        """检查基础练习的答案"""
        if not self.current_answers:
            QMessageBox.warning(self, '提示', '请先点击"下一题"生成题目')
            return

        user_answer = self.basic_practice_window.answer_input.text().strip()

        if not user_answer:
            QMessageBox.warning(self, '提示', '请输入答案')
            return

        try:
            user_answer = int(user_answer)
            correct_answer = self.current_answers[0]

            # 更新历史记录中的用户答案
            if self.current_problem_index < len(self.practice_history):
                problem, answer, _ = self.practice_history[self.current_problem_index]
                self.practice_history[self.current_problem_index] = (problem, answer, user_answer)

            # 只有当这道题还未计分时才计分
            if self.current_problem_index < len(self.problem_scored) and not self.problem_scored[self.current_problem_index]:
                self.problem_scored[self.current_problem_index] = True
                self.basic_total += 1

                if user_answer == correct_answer:
                    self.basic_correct += 1
                    self.basic_score += 10  # 每题10分

                self.update_basic_score_display()

            if user_answer == correct_answer:
                # 创建成功消息框
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle('太棒了！')
                msg.setText(f'回答正确！✨\n\n答案确实是 {correct_answer}')
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #E8F5E9;
                    }
                    QMessageBox QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 4px;
                    }
                """)
                msg.exec()
                # 自动生成下一题
                self.generate_basic_problem()
            else:
                # 创建错误消息框
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle('再试一次！')
                msg.setText(f'答案不对哦 😊\n\n正确答案是：{correct_answer}\n你的答案是：{user_answer}')
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #FFEBEE;
                    }
                    QMessageBox QPushButton {
                        background-color: #F44336;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 4px;
                    }
                """)
                msg.exec()
                self.basic_practice_window.answer_input.clear()
                self.basic_practice_window.answer_input.setFocus()
        except ValueError:
            QMessageBox.warning(self, '错误', '请输入有效的数字')

    def update_basic_score_display(self):
        """更新基础练习得分显示"""
        try:
            score_label = self.basic_practice_window.findChild(QLabel, 'score_label')
            if score_label:
                if self.basic_total > 0:
                    accuracy = (self.basic_correct / self.basic_total) * 100
                    score_text = f'得分: {self.basic_score} | 正确: {self.basic_correct}/{self.basic_total} | 正确率: {accuracy:.1f}%'
                else:
                    score_text = f'得分: {self.basic_score} | 正确: {self.basic_correct}/{self.basic_total}'
                score_label.setText(score_text)
        except:
            pass

    def show_timed_practice(self):
        """显示计时练习界面"""
        self.stacked_widget.setCurrentWidget(self.timed_practice_window)
        self.timed_practice_window.timer_display.setText('00:00')
        self.timed_practice_window.question_list.clear()
        self.timed_practice_window.answer_area.clear()
        # 初始化得分显示
        self.timed_score = 0
        self.timed_correct = 0
        self.timed_total = 0
        self.update_timed_score_display()

    def get_timed_selected_operations(self):
        """获取计时练习用户选择的运算类型"""
        operations = []
        try:
            # 尝试查找计时练习的复选框
            add_check = self.timed_practice_window.findChild(QCheckBox, 'timed_add_checkbox')
            sub_check = self.timed_practice_window.findChild(QCheckBox, 'timed_subtract_checkbox')
            mul_check = self.timed_practice_window.findChild(QCheckBox, 'timed_multiply_checkbox')
            div_check = self.timed_practice_window.findChild(QCheckBox, 'timed_divide_checkbox')

            if add_check and add_check.isChecked():
                operations.append('+')
            if sub_check and sub_check.isChecked():
                operations.append('-')
            if mul_check and mul_check.isChecked():
                operations.append('*')
            if div_check and div_check.isChecked():
                operations.append('/')
        except:
            pass

        # 如果没有选择任何运算类型，默认包含所有类型
        if not operations:
            operations = ['+', '-', '*', '/']

        return operations

    def get_timed_selected_difficulty(self):
        """获取计时练习用户选择的难度等级"""
        try:
            # 尝试查找计时练习的难度单选按钮
            easy_radio = self.timed_practice_window.findChild(QRadioButton, 'timed_easy_radio')
            medium_radio = self.timed_practice_window.findChild(QRadioButton, 'timed_medium_radio')
            hard_radio = self.timed_practice_window.findChild(QRadioButton, 'timed_hard_radio')

            if easy_radio and easy_radio.isChecked():
                return 'easy'
            elif hard_radio and hard_radio.isChecked():
                return 'hard'
            else:
                return 'medium'  # 默认中等难度
        except:
            return 'medium'

    def start_timed_practice(self):
        """开始计时练习"""
        # 获取用户设置
        try:
            question_count = self.timed_practice_window.question_count_spinbox.value()
            time_limit = self.timed_practice_window.time_limit_spinbox.value() * 60  # 转换为秒
        except:
            question_count = 10
            time_limit = 300  # 5分钟

        operations = self.get_timed_selected_operations()
        difficulty = self.get_timed_selected_difficulty()

        # 重置得分
        self.timed_score = 0
        self.timed_correct = 0
        self.timed_total = question_count
        self.update_timed_score_display()

        # 生成题目
        problems, answers = self.generate_multiple_problems_with_settings(question_count, difficulty, operations)
        self.current_answers = answers

        # 显示题目
        question_text = ""
        for i, problem in enumerate(problems, 1):
            question_text += f"{i}. {problem}\n"

        self.timed_practice_window.question_list.setPlainText(question_text)
        self.timed_practice_window.answer_area.clear()
        self.timed_practice_window.answer_area.setFocus()

        # 开始计时
        self.time_elapsed = 0
        self.timer.start(1000)  # 每秒更新一次

    def generate_multiple_problems_with_settings(self, count=10, difficulty='medium', operations=None):
        """根据设置生成多个数学题"""
        problems = []
        answers = []
        for _ in range(count):
            problem, answer = self.generate_problem(difficulty, operations)
            problems.append(problem)
            answers.append(answer)
        return problems, answers

    def update_timer(self):
        """更新计时器显示"""
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.timed_practice_window.timer_display.setText(f'{minutes:02d}:{seconds:02d}')

    def submit_timed_answers(self):
        """提交计时练习答案"""
        if not self.current_answers:
            QMessageBox.warning(self, '提示', '请先点击"开始计时"生成题目')
            return

        # 停止计时
        self.timer.stop()

        # 获取用户答案
        answer_text = self.timed_practice_window.answer_area.toPlainText()
        user_answers = answer_text.strip().split('\n')

        # 检查答案
        correct_count = 0
        result_text = "批改结果：\n\n"
        
        question_count = self.timed_practice_window.question_count_spinbox.value()

        for i in range(question_count):
            if i < len(user_answers):
                try:
                    user_answer = int(user_answers[i].strip())
                    if user_answer == self.current_answers[i]:
                        result_text += f"第{i + 1}题：✓ 正确\n"
                        correct_count += 1
                    else:
                        result_text += f"第{i + 1}题：✗ 错误，正确答案是 {self.current_answers[i]}\n"
                except:
                    result_text += f"第{i + 1}题：✗ 答案格式错误，正确答案是 {self.current_answers[i]}\n"
            else:
                result_text += f"第{i + 1}题：✗ 未作答，正确答案是 {self.current_answers[i]}\n"

        # 计算成绩
        score = correct_count * 10
        self.timed_score = score
        self.timed_correct = correct_count
        self.update_timed_score_display()

        time_str = self.timed_practice_window.timer_display.text()
        result_text += f"\n总分：{score}分 ({correct_count}/10题正确)"
        result_text += f"\n用时：{time_str}"

        # 保存成绩
        if self.current_user:
            self.user_data[self.current_user]['scores']['timed_practice'].append({
                'score': score,
                'time': time_str,
                'correct': correct_count
            })
            self.save_user_data()

        # 昲示结果
        QMessageBox.information(self, '练习完成', result_text)

        # 清空答案
        self.current_answers = []

    def handle_login(self):
        """处理登录"""
        try:
            username = self.login_window.username.text().strip()
            password = self.login_window.password.text().strip()

            if not username or not password:
                QMessageBox.warning(self, '错误', '请输入用户名和密码')
                return

            if username in self.user_data and self.user_data[username]['password'] == password:
                self.current_user = username
                self.stacked_widget.setCurrentWidget(self.main_menu_window)
                QMessageBox.information(self, '登录成功', f'欢迎回来，{username}！')
                # 清空输入框
                self.login_window.username.clear()
                self.login_window.password.clear()
            else:
                QMessageBox.warning(self, '登录失败', '用户名或密码错误')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'登录过程中出现错误：{str(e)}')

    def handle_register(self):
        """处理注册"""
        try:
            username = self.login_window.username.text().strip()
            password = self.login_window.password.text().strip()

            if not username or not password:
                QMessageBox.warning(self, '错误', '请输入用户名和密码')
                return

            if len(username) < 3:
                QMessageBox.warning(self, '错误', '用户名至少需要3个字符')
                return

            if len(password) < 6:
                QMessageBox.warning(self, '错误', '密码至少需要6个字符')
                return

            if username in self.user_data:
                QMessageBox.warning(self, '错误', '该用户名已存在')
                return

            # 创建新用户
            self.user_data[username] = {
                'password': password,
                'scores': {
                    'basic_practice': [],
                    'timed_practice': []
                }
            }
            self.save_user_data()

            QMessageBox.information(self, '注册成功', f'注册成功！欢迎加入，{username}！\n请使用您的账号登录。')
            # 清空输入框
            self.login_window.username.clear()
            self.login_window.password.clear()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'注册过程中出现错误：{str(e)}')

    def handle_logout(self):
        """处理退出登录"""
        try:
            reply = QMessageBox.question(self, '确认', '确定要退出登录吗？')
            if reply == QMessageBox.StandardButton.Yes:
                self.current_user = None
                self.login_window.username.clear()
                self.login_window.password.clear()
                self.stacked_widget.setCurrentWidget(self.login_window)
        except Exception as e:
            print(f"退出登录时出错: {e}")

    def back_to_main_menu(self):
        """返回主菜单"""
        try:
            # 如果正在计时，停止计时器
            if self.timer.isActive():
                self.timer.stop()
            if self.basic_timer.isActive():
                self.basic_timer.stop()
            self.stacked_widget.setCurrentWidget(self.main_menu_window)
        except Exception as e:
            print(f"返回主菜单时出错: {e}")

    def mock_get_ai_help(self):
        """模拟获取AI帮助"""
        try:
            question = self.ai_guide_window.question_input.toPlainText()
            if question:
                self.ai_guide_window.ai_answer.setPlainText(
                    "AI智能解答（示例）：\n\n"
                    "根据您的问题，我为您提供以下解答：\n\n"
                    "1. 首先理解题目要求...\n"
                    "2. 分析解题思路...\n"
                    "3. 具体解题步骤...\n\n"
                    "（此功能尚未实现，这只是示例文本）"
                )
            else:
                QMessageBox.warning(self, '提示', '请先输入您的问题')
        except Exception as e:
            QMessageBox.warning(self, '错误', f'获取AI帮助时出错：{str(e)}')

    def show_ai_guide(self):
        """显示AI指导界面"""
        self.stacked_widget.setCurrentWidget(self.ai_guide_window)

        # 检查AI功能状态
        if not AI_AVAILABLE or not self.ai_assistant:
            self.ai_guide_window.ai_answer.setPlainText(
                "⚠️ AI功能暂不可用\n\n"
                "可能的原因：\n"
                "1. AI助手模块加载失败\n"
                "2. 网络连接问题\n"
                "3. 缺少必要的依赖库\n\n"
                "请联系管理员或检查网络设置。"
            )
            return

        # 检查API密钥
        is_valid, message = self.ai_assistant.validate_api_key()
        if not is_valid:
            self.ai_guide_window.ai_answer.setPlainText(
                "🔧 需要配置API密钥\n\n"
                f"状态: {message}\n\n"
                "请点击下方按钮配置DeepSeek API密钥以使用AI智能助手功能。\n"
                "配置完成后即可享受AI辅导服务！"
            )
        else:
            self.ai_guide_window.ai_answer.setPlainText(
                "🤖 AI智能助手已就绪！\n\n"
                "欢迎使用数学AI助手！我可以帮助您：\n\n"
                "📚 解答各种数学问题\n"
                "📝 提供详细解题步骤\n"
                "💡 分享学习方法和技巧\n"
                "🎯 针对性练习建议\n\n"
                "请在左侧选择问题类型和难度，然后输入您的问题，我将为您提供专业的解答！"
            )

    def get_ai_help(self):
        """获取AI帮助 - 真实功能"""
        if not AI_AVAILABLE or not self.ai_assistant:
            QMessageBox.warning(self, '功能不可用', 'AI助手功能暂不可用，请检查系统配置')
            return

        # 检查API密钥
        is_valid, message = self.ai_assistant.validate_api_key()
        if not is_valid:
            reply = QMessageBox.question(
                self, '需要配置API密钥',
                f'{message}\n\n是否现在配置API密钥？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.show_ai_config()
            return

        # 获取用户输入
        try:
            problem_type = self.ai_guide_window.problem_type.currentText()
            difficulty = self.ai_guide_window.difficulty.currentText()
            user_question = self.ai_guide_window.question_input.toPlainText().strip()
        except:
            QMessageBox.warning(self, '获取信息失败', '无法获取问题信息，请检查界面元素')
            return

        if not user_question:
            QMessageBox.warning(self, '请输入问题', '请在问题输入框中输入您的数学问题')
            return

        if len(user_question.strip()) < 3:
            QMessageBox.warning(self, '问题太短', '请输入更详细的问题描述')
            return

        # 显示处理中状态
        self.ai_guide_window.ai_answer.setPlainText("🤔 AI正在思考您的问题...\n\n请稍候，这可能需要几秒钟时间。")

        # 禁用按钮防止重复点击
        get_help_btn = self.ai_guide_window.findChild(QPushButton, 'get_help_btn')
        if get_help_btn:
            get_help_btn.setEnabled(False)
            get_help_btn.setText('AI思考中...')

        # 创建并启动AI工作线程
        self.ai_worker = AIWorker(self.ai_assistant, problem_type, difficulty, user_question)
        self.ai_worker.response_ready.connect(self.handle_ai_response)
        self.ai_worker.progress_update.connect(self.update_ai_progress)
        self.ai_worker.start()

    def update_ai_progress(self, status_message):
        """更新AI处理进度"""
        current_text = self.ai_guide_window.ai_answer.toPlainText()
        if "AI正在思考" in current_text:
            self.ai_guide_window.ai_answer.setPlainText(f"🤔 {status_message}\n\n请稍候，这可能需要几秒钟时间。")

    def handle_ai_response(self, success, response):
        """处理AI响应"""
        # 恢复按钮状态
        get_help_btn = self.ai_guide_window.findChild(QPushButton, 'get_help_btn')
        if get_help_btn:
            get_help_btn.setEnabled(True)
            get_help_btn.setText('获取AI指导')

        if success:
            # 格式化AI回答
            formatted_response = f"🤖 AI智能解答\n\n{response}\n\n" + "="*50 + "\n💡 如果还有疑问，请继续提问！"
            self.ai_guide_window.ai_answer.setPlainText(formatted_response)

            # 保存对话记录
            if self.current_user:
                self.save_ai_conversation(
                    self.ai_guide_window.question_input.toPlainText(),
                    response
                )
        else:
            # 显示错误信息
            error_message = f"❌ AI回答失败\n\n错误信息: {response}\n\n" + "="*50 + "\n💡 建议检查网络连接或稍后重试"
            self.ai_guide_window.ai_answer.setPlainText(error_message)

        # 清理工作线程
        if self.ai_worker:
            self.ai_worker.deleteLater()
            self.ai_worker = None

    def show_ai_config(self):
        """显示AI配置对话框"""
        if not AI_AVAILABLE:
            QMessageBox.warning(self, '功能不可用', 'AI助手模块未正确加载')
            return

        current_key = ""
        if self.ai_assistant:
            current_key = getattr(self.ai_assistant, 'api_key', '')

        success, new_key = AIConfigDialog.show_config_dialog(self, current_key)

        if success and new_key:
            if self.ai_assistant:
                self.ai_assistant.set_api_key(new_key)
                self.save_api_key(new_key)
                QMessageBox.information(self, '配置成功', 'API密钥已保存，现在可以使用AI助手功能了！')

                # 更新AI界面状态
                self.show_ai_guide()

    def save_ai_conversation(self, question, answer):
        """保存AI对话记录"""
        try:
            if 'ai_conversations' not in self.user_data[self.current_user]:
                self.user_data[self.current_user]['ai_conversations'] = []

            conversation = {
                'timestamp': self.get_current_timestamp(),
                'question': question,
                'answer': answer,
                'problem_type': self.ai_guide_window.problem_type.currentText(),
                'difficulty': self.ai_guide_window.difficulty.currentText()
            }

            self.user_data[self.current_user]['ai_conversations'].append(conversation)

            # 只保留最近50条对话
            if len(self.user_data[self.current_user]['ai_conversations']) > 50:
                self.user_data[self.current_user]['ai_conversations'] = \
                    self.user_data[self.current_user]['ai_conversations'][-50:]

            self.save_user_data()
            print(f"已保存用户 {self.current_user} 的AI对话记录")

        except Exception as e:
            print(f"保存AI对话记录失败: {e}")

    def clear_canvas(self):
        """清空画布"""
        try:
            self.handwriting_window.canvas.clear()
            self.handwriting_window.canvas.setText('手写区域\n（点击"上传图片"选择手写作业）')
            self.handwriting_window.recognition_result.clear()
            self.handwriting_window.correction_result.clear()
            self.current_image_path = None
        except Exception as e:
            print(f"清空画布时出错: {e}")

    def update_timed_score_display(self):
        """更新计时练习得分显示"""
        try:
            score_label = self.timed_practice_window.findChild(QLabel, 'score_label')
            if score_label:
                score_text = f'得分: {self.timed_score} / 正确: {self.timed_correct} / 总题数: {self.timed_total}'
                score_label.setText(score_text)
        except:
            pass

    def show_previous_problem(self):
        """显示上一题"""
        if self.current_problem_index > 0:
            # 保存当前答案
            user_input = self.basic_practice_window.answer_input.text().strip()
            if user_input:
                try:
                    user_answer = int(user_input)
                    problem, answer, _ = self.practice_history[self.current_problem_index]
                    self.practice_history[self.current_problem_index] = (problem, answer, user_answer)
                except ValueError:
                    pass
            
            # 移动到上一题
            self.current_problem_index -= 1
            problem, answer, user_answer = self.practice_history[self.current_problem_index]
            self.current_answers = [answer]
            self.basic_practice_window.question_label.setText(problem)

            # 显示之前保存的答案
            if user_answer is not None:
                self.basic_practice_window.answer_input.setText(str(user_answer))
            else:
                self.basic_practice_window.answer_input.clear()

            self.basic_practice_window.answer_input.setFocus()
        else:
            QMessageBox.information(self, '提示', '已经是第一题了')

    def submit_basic_practice(self):
        """提交基础练习"""
        if not self.practice_history:
            QMessageBox.warning(self, '提示', '还没有开始练习')
            return
        
        # 保存当前题目的答案
        if self.current_problem_index >= 0 and self.current_problem_index < len(self.practice_history):
            user_input = self.basic_practice_window.answer_input.text().strip()
            if user_input:
                try:
                    user_answer = int(user_input)
                    problem, answer, _ = self.practice_history[self.current_problem_index]
                    self.practice_history[self.current_problem_index] = (problem, answer, user_answer)
                except ValueError:
                    pass
        
        # 停止计时
        if self.basic_timer.isActive():
            self.basic_timer.stop()
        
        # 计算最终成绩
        total_problems = len(self.practice_history)
        correct_count = 0
        result_text = "基础练习结果：\n\n"
        
        for i, (problem, correct_answer, user_answer) in enumerate(self.practice_history, 1):
            if user_answer is not None:
                if user_answer == correct_answer:
                    result_text += f"第{i}题: ✓ 正确 ({problem.replace(' = ?', '')} = {correct_answer})\n"
                    correct_count += 1
                else:
                    result_text += f"第{i}题: ✗ 错误 ({problem.replace(' = ?', '')} = {correct_answer}，你的答案: {user_answer})\n"
            else:
                result_text += f"第{i}题: - 未作答 ({problem.replace(' = ?', '')} = {correct_answer})\n"
        
        # 计算统计信息
        if total_problems > 0:
            accuracy = (correct_count / total_problems) * 100
            final_score = correct_count * 10
            
            minutes = self.basic_start_time // 60
            seconds = self.basic_start_time % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            result_text += f"\n=== 统计信息 ===\n"
            result_text += f"总题数: {total_problems}\n"
            result_text += f"正确数: {correct_count}\n"
            result_text += f"正确率: {accuracy:.1f}%\n"
            result_text += f"总得分: {final_score}分\n"
            result_text += f"用时: {time_str}\n"
            
            # 保存成绩
            if self.current_user:
                if 'basic_practice' not in self.user_data[self.current_user]['scores']:
                    self.user_data[self.current_user]['scores']['basic_practice'] = []
                
                self.user_data[self.current_user]['scores']['basic_practice'].append({
                    'score': final_score,
                    'correct': correct_count,
                    'total': total_problems,
                    'accuracy': accuracy,
                    'time': time_str,
                    'timestamp': self.get_current_timestamp()
                })
                self.save_user_data()
        
        # 显示结果
        QMessageBox.information(self, '练习完成', result_text)
        
        # 重置状态
        self.practice_history = []
        self.current_problem_index = -1
        self.basic_score = 0
        self.basic_correct = 0
        self.basic_total = 0
        self.problem_scored = []
        self.update_basic_score_display()

    def show_handwriting(self):
        """显示手写批改界面"""
        self.stacked_widget.setCurrentWidget(self.handwriting_window)
        # 清空之前的结果
        self.clear_canvas()
        
        # 显示OCR状态信息
        if self.ocr_grader:
            status_msg = "OCR功能已就绪，请上传手写作业图片进行批改"
        else:
            status_msg = "OCR功能暂不可用，将使用演示模式"
        
        try:
            self.handwriting_window.recognition_result.setPlainText(status_msg)
        except:
            pass

    def upload_image(self):
        """处理图片上传"""
        # 打开文件对话框让用户选择图片
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择手写作业图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
        )

        if file_path:
            # 验证文件存在
            if not os.path.exists(file_path):
                QMessageBox.warning(self, '错误', '选择的文件不存在！')
                return
            
            # 保存当前图片路径
            self.current_image_path = file_path
            
            # 加载图片并显示在canvas上
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 调整图片大小以适应canvas
                scaled_pixmap = pixmap.scaled(
                    self.handwriting_window.canvas.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.handwriting_window.canvas.setPixmap(scaled_pixmap)
                self.handwriting_window.canvas.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # 显示上传成功消息
                QMessageBox.information(self, '上传成功', f'图片已成功上传！\n文件：{os.path.basename(file_path)}\n\n请点击"开始批改"进行OCR识别和批改。')
                
                # 更新状态显示
                status_text = f"图片已加载: {os.path.basename(file_path)}\n点击'开始批改'进行识别..."
                self.handwriting_window.recognition_result.setPlainText(status_text)
                self.handwriting_window.correction_result.clear()
            else:
                QMessageBox.warning(self, '上传失败', '无法加载所选图片文件！请确保文件格式正确。')
                self.current_image_path = None

    def start_ocr_correction(self):
        """开始OCR批改"""
        if not self.current_image_path:
            QMessageBox.warning(self, '提示', '请先上传手写作业图片！')
            return
        
        if not os.path.exists(self.current_image_path):
            QMessageBox.warning(self, '错误', '图片文件不存在，请重新上传！')
            self.current_image_path = None
            return
        
        # 显示处理中状态
        self.handwriting_window.recognition_result.setPlainText("正在进行OCR识别，请稍候...\n\n提示：如果识别效果不佳，请确保：\n1. 图片清晰度足够\n2. 字迹工整\n3. 背景干净\n4. 光线充足")
        self.handwriting_window.correction_result.setPlainText("正在批改中...")
        
        # 强制刷新界面
        QApplication.processEvents()
        
        # 处理OCR批改
        try:
            if self.ocr_grader:
                print("使用真实OCR进行识别...")
                result = self.perform_real_ocr_correction()
            else:
                print("使用模拟OCR进行演示...")
                result = self.perform_mock_ocr_correction()
            
            # 显示结果
            self.display_ocr_results(result)
            
        except Exception as e:
            error_msg = f"批改过程中出现错误：{str(e)}\n\n可能的解决方案：\n1. 检查图片格式是否正确\n2. 确保图片大小适中\n3. 尝试重新上传图片"
            QMessageBox.critical(self, '批改失败', error_msg)
            self.handwriting_window.recognition_result.setPlainText(error_msg)
            self.handwriting_window.correction_result.setPlainText("批改失败，请检查图片质量或稍后重试。")

    def perform_real_ocr_correction(self):
        """执行真实的OCR批改"""
        try:
            print(f"=== 开始真实OCR处理 ===")
            print(f"图片路径: {self.current_image_path}")
            print(f"图片存在: {os.path.exists(self.current_image_path)}")
            
            if not os.path.exists(self.current_image_path):
                raise Exception(f"图片文件不存在: {self.current_image_path}")
            
            # 显示图片信息
            try:
                file_size = os.path.getsize(self.current_image_path)
                print(f"图片大小: {file_size} bytes")
            except Exception as e:
                print(f"获取图片大小失败: {e}")
            
            # 调用OCR批改器
            print("调用OCR批改器...")
            result = self.ocr_grader.grade_homework(self.current_image_path)
            
            # 验证结果
            if not result:
                raise Exception("OCR返回空结果")
                
            if not isinstance(result, dict):
                raise Exception(f"OCR返回结果类型错误: {type(result)}")
            
            # 检查必要的键
            required_keys = ["detected_problems", "detected_answers", "grading_results"]
            for key in required_keys:
                if key not in result:
                    result[key] = f"缺少 {key} 数据"
            
            print(f"OCR处理完成，返回结果: {len(str(result))} 字符")
            return result
            
        except Exception as e:
            error_msg = f"真实OCR处理失败: {e}"
            print(error_msg)
            print("自动回退到模拟模式")
            return self.perform_mock_ocr_correction()

    def perform_mock_ocr_correction(self):
        """执行模拟的OCR批改（用于演示和错误回退）"""
        print("=== 使用模拟OCR模式 ===")
        
        # 根据上传的图片提供相应的模拟结果
        sample_problems = [
            "9 + 3 = ?",
            "10 - 4 = ?", 
            "7 × 9 = ?",
            "6 ÷ 3 = ?",
            "20 + 15 = ?"
        ]
        
        sample_answers = ["12", "6", "63", "2", "35"]
        correct_answers = [12, 6, 63, 2, 35]
        
        # 模拟用户答案（有些对有些错）
        user_answers = [12, 6, 42, 2, 35]  # 第3题故意答错
        
        # 构建识别结果
        detected_problems = "\n".join(sample_problems)
        detected_answers = "\n".join(sample_answers)
        
        # 构建批改结果
        grading_results = []
        for i, (correct, user) in enumerate(zip(correct_answers, user_answers)):
            if correct == user:
                grading_results.append(f"第{i+1}题: ✓ 正确！")
            else:
                grading_results.append(f"第{i+1}题: ✗ 错误，正确答案是 {correct}")
        
        result = {
            "detected_problems": detected_problems,
            "detected_answers": detected_answers,
            "grading_results": "\n".join(grading_results)
        }
        
        print("模拟OCR完成")
        return result

    def display_ocr_results(self, result):
        """显示OCR批改结果"""
        try:
            # 显示识别的题目和答案
            recognition_text = "=== 识别结果 ===\n\n"
            
            problems = result.get("detected_problems", "未检测到题目")
            answers = result.get("detected_answers", "未检测到答案")
            
            if problems.strip():
                recognition_text += "检测到的题目：\n"
                recognition_text += problems
            else:
                recognition_text += "检测到的题目：\n(未识别到题目，可能图片质量需要改善)"
            
            if answers.strip():
                recognition_text += "\n\n检测到的答案：\n"
                recognition_text += answers
            else:
                recognition_text += "\n\n检测到的答案：\n(未识别到答案)"
            
            self.handwriting_window.recognition_result.setPlainText(recognition_text)
            
            # 显示批改结果
            correction_text = "=== 批改结果 ===\n\n"
            grading_results = result.get("grading_results", "批改失败")
            correction_text += grading_results
            
            # 统计正确率
            grading_lines = grading_results.split('\n') if grading_results else []
            correct_count = sum(1 for line in grading_lines if '✓' in line or '正确' in line)
            total_count = len([line for line in grading_lines if line.strip() and '第' in line])
            
            if total_count > 0:
                accuracy = (correct_count / total_count) * 100
                correction_text += f"\n\n=== 统计信息 ===\n"
                correction_text += f"总题数: {total_count}\n"
                correction_text += f"正确数: {correct_count}\n"
                correction_text += f"正确率: {accuracy:.1f}%\n"
                
                # 添加鼓励语句
                if accuracy >= 90:
                    correction_text += "\n🎉 优秀！继续保持！"
                elif accuracy >= 70:
                    correction_text += "\n👍 不错！再接再厉！"
                elif accuracy >= 60:
                    correction_text += "\n📚 还需努力，多多练习！"
                else:
                    correction_text += "\n💪 不要灰心，继续加油！"
                    
                # 添加改进建议
                if accuracy < 70:
                    correction_text += "\n\n💡 改进建议：\n"
                    correction_text += "• 确保字迹清晰工整\n"
                    correction_text += "• 使用深色笔书写\n"
                    correction_text += "• 保证良好的光线条件\n"
                    correction_text += "• 避免背景杂乱"
            
            self.handwriting_window.correction_result.setPlainText(correction_text)
            
            # 保存批改记录
            if self.current_user:
                self.save_handwriting_record(result, correct_count, total_count)
            
            # 显示完成消息
            if total_count > 0:
                completion_msg = f'手写作业批改完成！\n\n识别到 {total_count} 道题目\n正确 {correct_count} 道题目\n正确率: {accuracy:.1f}%'
                if accuracy < 70:
                    completion_msg += '\n\n💡 如需提高识别准确率，请确保图片清晰、字迹工整'
            else:
                completion_msg = '批改完成！\n\n⚠️ 未能识别到有效题目\n请检查图片质量后重新尝试'
                
            QMessageBox.information(self, '批改完成', completion_msg)
            
        except Exception as e:
            print(f"显示结果时出错: {e}")
            QMessageBox.warning(self, '显示错误', f'显示批改结果时出现问题：{str(e)}')

    def save_handwriting_record(self, result, correct_count, total_count):
        """保存手写批改记录"""
        try:
            if 'handwriting_records' not in self.user_data[self.current_user]:
                self.user_data[self.current_user]['handwriting_records'] = []
            
            record = {
                'timestamp': self.get_current_timestamp(),
                'image_path': os.path.basename(self.current_image_path) if self.current_image_path else 'unknown',
                'total_problems': total_count,
                'correct_answers': correct_count,
                'accuracy': (correct_count / total_count * 100) if total_count > 0 else 0,
                'detected_problems': result.get("detected_problems", ""),
                'grading_results': result.get("grading_results", "")
            }
            
            self.user_data[self.current_user]['handwriting_records'].append(record)
            self.save_user_data()
            print(f"已保存用户 {self.current_user} 的手写批改记录")
            
        except Exception as e:
            print(f"保存手写批改记录失败: {e}")

    def get_current_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    system = MathPracticeSystem()
    system.show()
    sys.exit(app.exec())