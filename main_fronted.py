import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog, QPushButton
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap
from new_ui import MainApplication
from random import randint


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

        # 计时练习相关变量
        self.timed_score = 0  # 得分
        self.timed_correct = 0  # 正确数
        self.timed_total = 0  # 总题数

        # 初始化用户数据
        self.load_user_data()

        # 设置所有连接
        self.setup_connections()

    def load_user_data(self):
        """加载用户数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.user_data = json.load(f)
        else:
            self.user_data = {}

    def save_user_data(self):
        """保存用户数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)

    def setup_connections(self):
        """设置所有按钮连接"""
        # 登录窗口按钮
        self.login_window.findChild(QPushButton, 'login_btn').clicked.connect(self.handle_login)
        self.login_window.findChild(QPushButton, 'register_btn').clicked.connect(self.handle_register)

        # 主菜单窗口按钮
        self.main_menu_window.findChild(QPushButton, 'basic_btn').clicked.connect(self.show_basic_practice)
        self.main_menu_window.findChild(QPushButton, 'timed_btn').clicked.connect(self.show_timed_practice)
        self.main_menu_window.findChild(QPushButton, 'ai_guide_btn').clicked.connect(self.show_ai_guide)
        self.main_menu_window.findChild(QPushButton, 'handwrite_btn').clicked.connect(self.show_handwriting)
        self.main_menu_window.findChild(QPushButton, 'logout_btn').clicked.connect(self.handle_logout)

        # 基础练习窗口按钮
        self.basic_practice_window.findChild(QPushButton, 'back_btn').clicked.connect(self.back_to_main_menu)
        self.basic_practice_window.findChild(QPushButton, 'prev_btn').clicked.connect(self.show_previous_problem)
        self.basic_practice_window.findChild(QPushButton, 'next_btn').clicked.connect(self.generate_basic_problem)
        self.basic_practice_window.findChild(QPushButton, 'submit_btn').clicked.connect(self.submit_basic_practice)

        # 计时练习窗口按钮
        self.timed_practice_window.findChild(QPushButton, 'back_btn').clicked.connect(self.back_to_main_menu)
        self.timed_practice_window.findChild(QPushButton, 'start_btn').clicked.connect(self.start_timed_practice)
        self.timed_practice_window.findChild(QPushButton, 'submit_btn').clicked.connect(self.submit_timed_answers)

        # AI指导窗口按钮
        self.ai_guide_window.findChild(QPushButton, 'back_btn').clicked.connect(self.back_to_main_menu)
        self.ai_guide_window.findChild(QPushButton, 'get_help_btn').clicked.connect(self.mock_get_ai_help)

        # 手写批改窗口按钮
        self.handwriting_window.findChild(QPushButton, 'back_btn').clicked.connect(self.back_to_main_menu)
        self.handwriting_window.findChild(QPushButton, 'correct_btn').clicked.connect(self.mock_correct_handwriting)

        # 手写批改窗口的其他按钮
        upload_btn = self.handwriting_window.findChildren(QPushButton)[2]  # 获取上传按钮
        clear_btn = self.handwriting_window.findChildren(QPushButton)[1]  # 获取清空按钮
        upload_btn.clicked.connect(self.upload_image)
        clear_btn.clicked.connect(self.clear_canvas)

    def handle_login(self):
        """处理登录"""
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

    def handle_register(self):
        """处理注册"""
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

    def handle_logout(self):
        """处理退出登录"""
        reply = QMessageBox.question(self, '确认', '确定要退出登录吗？')
        if reply == QMessageBox.StandardButton.Yes:
            self.current_user = None
            self.login_window.username.clear()
            self.login_window.password.clear()
            self.stacked_widget.setCurrentWidget(self.login_window)

    def generate_problem(self, difficulty='medium'):
        """生成单个数学题（改进版）"""
        fdict = {0: '+', 1: '-', 2: '*', 3: '/'}
        c = randint(0, 3)
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

        if c == 3:  # 除法确保结果为整数
            b = randint(1, max_mul)
            ans = randint(1, 10)
            a = b * ans
        else:
            if c == 2:  # 乘法
                a = randint(1, max_mul)
                b = randint(1, max_mul)
                ans = a * b
            else:  # 加法或减法
                a = randint(1, max_num)
                b = randint(1, max_num)
                if c == 0:
                    ans = a + b
                elif c == 1:
                    # 确保减法结果为正数
                    if a < b:
                        a, b = b, a
                    ans = a - b

        problem = f'{a} {fdict[c]} {b} = ?'
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
        # 自动生成第一道题目
        self.generate_basic_problem()

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
            problem, answer = self.generate_problem()
            self.current_answers = [answer]
            self.practice_history.append((problem, answer, None))
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
            if self.current_problem_index < len(self.problem_scored) and not self.problem_scored[
                self.current_problem_index]:
                self.problem_scored[self.current_problem_index] = True
                self.basic_total += 1

                if user_answer == correct_answer:
                    self.basic_correct += 1
                    self.basic_score += 10  # 每题10分

                self.update_score_display()

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

    def start_timed_practice(self):
        """开始计时练习"""
        # 重置得分
        self.timed_score = 0
        self.timed_correct = 0
        self.timed_total = 10  # 固定10道题
        self.update_timed_score_display()

        # 生成10道题
        problems, answers = self.generate_multiple_problems(10)
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

        for i in range(10):
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

        # 显示结果
        QMessageBox.information(self, '练习完成', result_text)

        # 清空答案
        self.current_answers = []

    def show_ai_guide(self):
        """显示AI指导界面"""
        self.stacked_widget.setCurrentWidget(self.ai_guide_window)

    def show_handwriting(self):
        """显示手写批改界面"""
        self.stacked_widget.setCurrentWidget(self.handwriting_window)

    def back_to_main_menu(self):
        """返回主菜单"""
        # 如果正在计时，停止计时器
        if self.timer.isActive():
            self.timer.stop()
        self.stacked_widget.setCurrentWidget(self.main_menu_window)

    def mock_get_ai_help(self):
        """模拟获取AI帮助"""
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

    def mock_correct_handwriting(self):
        """模拟手写批改"""
        self.handwriting_window.recognition_result.setPlainText(
            "识别结果（示例）：\n15 + 23 = 38"
        )
        self.handwriting_window.correction_result.setPlainText(
            "批改结果（示例）：\n✓ 正确！\n\n计算过程完全正确。"
        )
        QMessageBox.information(self, '批改完成', '手写批改功能演示完成（功能尚未实现）')

    def upload_image(self):
        """处理图片上传"""
        # 打开文件对话框让用户选择图片
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片文件",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
        )

        if file_path:
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
                QMessageBox.information(self, '上传成功', f'图片已成功上传！\n文件：{os.path.basename(file_path)}')
            else:
                QMessageBox.warning(self, '上传失败', '无法加载所选图片文件！')

    def clear_canvas(self):
        """清空画布"""
        self.handwriting_window.canvas.clear()
        self.handwriting_window.canvas.setText('手写区域\n（在此处书写数学题）')
        self.handwriting_window.recognition_result.clear()
        self.handwriting_window.correction_result.clear()

    def show_previous_problem(self):
        """显示上一题"""
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

        if self.current_problem_index > 0:
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
            QMessageBox.information(self, '提示', '已经是第一题了！')

    def submit_basic_practice(self):
        """提交基础练习并显示正确率"""
        # 在提交前，保存当前题目的答案
        if self.current_problem_index >= 0 and self.current_problem_index < len(self.practice_history):
            user_input = self.basic_practice_window.answer_input.text().strip()
            if user_input:
                try:
                    user_answer = int(user_input)
                    problem, answer, _ = self.practice_history[self.current_problem_index]
                    self.practice_history[self.current_problem_index] = (problem, answer, user_answer)
                except ValueError:
                    pass

        if not self.practice_history:
            QMessageBox.warning(self, '提示', '还没有做任何题目！')
            return

        # 统计答题情况
        total_answered = 0
        correct_count = 0

        for problem, answer, user_answer in self.practice_history:
            if user_answer is not None:
                total_answered += 1
                if user_answer == answer:
                    correct_count += 1

        if total_answered == 0:
            QMessageBox.warning(self, '提示', '您还没有回答任何题目！')
            return

        # 计算正确率和得分
        accuracy = (correct_count / total_answered) * 100
        score = correct_count * 10

        # 显示详细结果
        result_text = f"练习统计：\n\n"
        result_text += f"总生成题数：{len(self.practice_history)}\n"
        result_text += f"已作答题数：{total_answered}\n"
        result_text += f"正确数：{correct_count}\n"
        result_text += f"错误数：{total_answered - correct_count}\n"
        result_text += f"正确率：{accuracy:.1f}%\n"
        result_text += f"总得分：{score}\n\n"

        # 详细题目列表
        result_text += "题目详情：\n"
        for i, (problem, answer, user_answer) in enumerate(self.practice_history):
            if user_answer is not None:
                if user_answer == answer:
                    result_text += f"第{i + 1}题: {problem} ✓ (你的答案: {user_answer})\n"
                else:
                    result_text += f"第{i + 1}题: {problem} ✗ (正确答案: {answer}, 你的答案: {user_answer})\n"
            else:
                result_text += f"第{i + 1}题: {problem} (未作答)\n"

        result_text += "\n"
        if accuracy >= 90:
            result_text += "太棒了！继续保持！💪"
        elif accuracy >= 70:
            result_text += "做得不错！加油！😊"
        elif accuracy >= 60:
            result_text += "还需要多练习哦！📚"
        else:
            result_text += "不要灰心，多练习就会进步的！🌟"

        # 保存成绩
        if self.current_user:
            self.user_data[self.current_user]['scores']['basic_practice'].append({
                'total_generated': len(self.practice_history),
                'total_answered': total_answered,
                'correct': correct_count,
                'score': score,
                'accuracy': accuracy
            })
            self.save_user_data()

        QMessageBox.information(self, '练习完成', result_text)

    def update_score_display(self):
        """更新得分显示"""
        score_text = f'得分: {self.basic_score} / 正确: {self.basic_correct} / 总题数: {self.basic_total}'
        self.basic_practice_window.score_label.setText(score_text)

    def update_timed_score_display(self):
        """更新计时练习得分显示"""
        score_text = f'得分: {self.timed_score} / 正确: {self.timed_correct} / 总题数: {self.timed_total}'
        self.timed_practice_window.score_label.setText(score_text)


# 导入必要的类
from PyQt6.QtWidgets import QPushButton

if __name__ == '__main__':
    app = QApplication(sys.argv)
    system = MathPracticeSystem()
    system.show()
    sys.exit(app.exec())