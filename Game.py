import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from UI import Ui_MainWindow
from BasicExercise import BasicExercise
from TimedMode import TimedMode
from UserData import UserData

class CalculateGame(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        
        # 初始化模块
        self.basic_exercise = BasicExercise()
        self.timed_mode = TimedMode()
        self.user_data = UserData()
        
        # 默认登录临时用户
        self.user_data.login("guest")
        
        # 初始状态
        self.current_mode = "basic"  # 'basic' 或 'timed'
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        # 连接信号和槽
        self.setup_connections()
        
        # 初始化显示基础练习模式
        self.show_basic_exercise_mode()
    
    def init_ui(self):
        """初始化UI其他设置"""
        # TODO: 增加任何UI初始化代码
        pass
    
    def setup_connections(self):
        """设置信号连接"""
        # 模式切换
        self.basicModeBtn.clicked.connect(self.show_basic_exercise_mode)
        self.timedModeBtn.clicked.connect(self.show_timed_mode)
        
        # 基础练习按钮
        self.generateBtn.clicked.connect(self.generate_basic_question)
        self.submitBtn.clicked.connect(self.check_basic_answer)
        self.answerInput.returnPressed.connect(self.check_basic_answer)
        
        # 计时模式按钮
        self.startTimedBtn.clicked.connect(self.start_timed_challenge)
        self.submitTimedBtn.clicked.connect(self.check_timed_answer)
        self.timedAnswerInput.returnPressed.connect(self.check_timed_answer)
    
    def show_basic_exercise_mode(self):
        """切换到基础练习模式"""
        self.current_mode = "basic"
        self.stackedWidget.setCurrentIndex(0)  # 假设基础练习页面是第一个
        self.statusBar().showMessage("基础练习模式")
    
    def show_timed_mode(self):
        """切换到计时模式"""
        self.current_mode = "timed"
        self.stackedWidget.setCurrentIndex(1)  # 假设计时模式页面是第二个
        self.statusBar().showMessage("计时模式")
    
    def generate_basic_question(self):
        """生成基础练习题目"""
        # 获取选中的操作类型
        operations = []
        if self.addCheckBox.isChecked():
            operations.append("+")
        if self.subtractCheckBox.isChecked():
            operations.append("-")
        if self.multiplyCheckBox.isChecked():
            operations.append("*")
        if self.divideCheckBox.isChecked():
            operations.append("/")
        
        # 获取难度
        difficulty = "中等"  # 默认中等
        if self.easyRadioBtn.isChecked():
            difficulty = "简单"
        elif self.hardRadioBtn.isChecked():
            difficulty = "困难"
        
        # 生成问题
        question = self.basic_exercise.generate_question(operations, difficulty)
        self.questionLabel.setText(question)
        self.answerInput.clear()
        self.answerInput.setFocus()
        self.resultLabel.setText("")
    
    def check_basic_answer(self):
        """检查基础练习答案"""
        user_answer = self.answerInput.text().strip()
        if not user_answer:
            return
            
        is_correct, correct_answer = self.basic_exercise.check_answer(user_answer)
        
        if is_correct:
            self.resultLabel.setText("✓ 正确!")
            self.resultLabel.setStyleSheet("color: green;")
        else:
            self.resultLabel.setText(f"✗ 错误! 正确答案是: {correct_answer}")
            self.resultLabel.setStyleSheet("color: red;")
        
        # 更新统计
        stats = self.basic_exercise.get_stats()
        self.statsLabel.setText(f"统计: {stats['correct']}/{stats['total']} 正确率: {stats['accuracy']:.1f}%")
    
    def start_timed_challenge(self):
        """开始计时模式挑战"""
        # 获取选中的操作类型
        operations = []
        if self.timedAddCheck.isChecked():
            operations.append("+")
        if self.timedSubtractCheck.isChecked():
            operations.append("-")
        if self.timedMultiplyCheck.isChecked():
            operations.append("*")
        if self.timedDivideCheck.isChecked():
            operations.append("/")
        
        # 获取难度
        difficulty = "中等"  # 默认中等
        if self.timedEasyRadio.isChecked():
            difficulty = "简单"
        elif self.timedHardRadio.isChecked():
            difficulty = "困难"
        
        # 获取时间限制和题目数量
        time_limit = self.timeSpinBox.value()
        question_count = self.questionCountSpinBox.value()
        
        # 开始挑战
        question = self.timed_mode.start_challenge(operations, difficulty, question_count, time_limit)
        self.timedQuestionLabel.setText(question)
        self.timedAnswerInput.clear()
        self.timedAnswerInput.setFocus()
        self.timedResultLabel.setText("")
        
        # 设置进度显示
        progress = self.timed_mode.get_progress()
        self.progressLabel.setText(f"题目: {progress['current']}/{progress['total']} 正确: {progress['correct']}")
        
        # 开始计时器
        self.timer.start(100)  # 每100毫秒更新一次
        self.timedTimeLabel.setText(f"剩余时间: {time_limit}秒")
        
        # 禁用开始按钮，启用提交按钮
        self.startTimedBtn.setEnabled(False)
        self.submitTimedBtn.setEnabled(True)
    
    def check_timed_answer(self):
        """检查计时模式答案"""
        user_answer = self.timedAnswerInput.text().strip()
        if not user_answer:
            return
            
        is_correct, correct_answer, is_finished = self.timed_mode.check_answer(user_answer)
        
        if is_correct:
            self.timedResultLabel.setText("✓ 正确!")
            self.timedResultLabel.setStyleSheet("color: green;")
        else:
            self.timedResultLabel.setText(f"✗ 错误! 正确答案是: {correct_answer}")
            self.timedResultLabel.setStyleSheet("color: red;")
        
        # 更新进度
        progress = self.timed_mode.get_progress()
        self.progressLabel.setText(f"题目: {progress['current']}/{progress['total']} 正确: {progress['correct']}")
        
        if is_finished:
            self.finish_timed_challenge()
        else:
            # 显示下一题
            self.timedQuestionLabel.setText(self.timed_mode.current_question)
            self.timedAnswerInput.clear()
            self.timedAnswerInput.setFocus()
    
    def update_timer(self):
        """更新计时器显示"""
        remaining = self.timed_mode.time_remaining()
        
        # 更新剩余时间显示
        self.timedTimeLabel.setText(f"剩余时间: {int(remaining)}秒")
        
        # 时间到了，结束挑战
        if remaining <= 0:
            self.finish_timed_challenge()
    
    def finish_timed_challenge(self):
        """结束计时挑战"""
        # 停止计时器
        self.timer.stop()
        
        # 获取结果
        results = self.timed_mode.get_results()
        
        # 显示结果
        result_text = (
            f"挑战结束!\n\n"
            f"总题数: {results['total_questions']}\n"
            f"已答题: {results['attempted']}\n"
            f"正确数: {results['correct']}\n"
            f"正确率: {results['accuracy']:.1f}%\n"
            f"用时: {results['time_taken']:.1f}秒"
        )
        QMessageBox.information(self, "挑战结果", result_text)
        
        # 重置界面
        self.startTimedBtn.setEnabled(True)
        self.submitTimedBtn.setEnabled(False)
        self.timedQuestionLabel.setText("点击\"开始\"按钮开始挑战")
        self.timedAnswerInput.clear()
        self.timedResultLabel.setText("")
        self.timedTimeLabel.setText("剩余时间: --秒")
        self.progressLabel.setText("题目: --/-- 正确: --")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalculateGame()
    window.show()
    sys.exit(app.exec_())