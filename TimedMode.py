import random
import time
from Utils import save_exercise_record

class TimedMode:
    def __init__(self):
        self.current_question = None
        self.answer = None
        self.questions = []
        self.current_index = 0
        self.correct_count = 0
        self.start_time = None
        self.time_limit = 60  # 默认60秒
        self.is_running = False
        
    def start_challenge(self, operation_types, difficulty, question_count=10, time_limit=60):
        """开始一次计时挑战"""
        self.questions = []
        self.current_index = 0
        self.correct_count = 0
        self.time_limit = time_limit
        self.is_running = True
        self.start_time = time.time()
        
        # 根据难度设置数字范围
        if difficulty == "简单":
            num_range = (1, 10)
        elif difficulty == "中等":
            num_range = (1, 50)
        else:  # 困难
            num_range = (1, 100)
        
        # 生成指定数量的题目
        for _ in range(question_count):
            if not operation_types:
                operation = "+"  # 默认加法
            else:
                operation = random.choice(operation_types)
                
            # 生成操作数
            num1 = random.randint(num_range[0], num_range[1])
            num2 = random.randint(num_range[0], num_range[1])
            
            # 确保除法不会有除零问题并得到整数结果
            if operation == "/":
                result = random.randint(1, 10)
                num2 = random.randint(1, 10)
                num1 = num2 * result
                
            # 确保减法结果非负
            if operation == "-" and num1 < num2:
                num1, num2 = num2, num1
                
            # 计算答案
            if operation == "+":
                answer = num1 + num2
            elif operation == "-":
                answer = num1 - num2
            elif operation == "*":
                answer = num1 * num2
            else:  # operation == "/"
                answer = num1 // num2
                
            # 格式化问题
            question = f"{num1} {operation} {num2} = ?"
            
            self.questions.append({
                "question": question,
                "answer": answer,
                "user_answer": None,
                "is_correct": None
            })
            
        self.current_question = self.questions[0]["question"]
        self.answer = self.questions[0]["answer"]
        return self.current_question
    
    def check_answer(self, user_answer):
        """检查当前答案并移至下一题"""
        if not self.is_running:
            return False, self.answer, True
            
        try:
            user_answer = int(user_answer)
            is_correct = user_answer == self.answer
            
            # 记录答案
            self.questions[self.current_index]["user_answer"] = user_answer
            self.questions[self.current_index]["is_correct"] = is_correct
            
            if is_correct:
                self.correct_count += 1
                
            # 移动到下一题
            self.current_index += 1
            is_finished = self.current_index >= len(self.questions)
            
            # 如果挑战未结束，准备下一题
            if not is_finished:
                self.current_question = self.questions[self.current_index]["question"]
                self.answer = self.questions[self.current_index]["answer"]
            else:
                self.is_running = False
                self._save_challenge_result()
                
            return is_correct, self.answer, is_finished
        except:
            return False, self.answer, False
    
    def time_remaining(self):
        """返回剩余时间(秒)"""
        if not self.is_running:
            return 0
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        
        # 如果时间到了，结束挑战
        if remaining <= 0:
            self.is_running = False
            self._save_challenge_result()
            return 0
        
        return remaining
    
    def get_progress(self):
        """获取当前进度"""
        return {
            "current": self.current_index + 1,
            "total": len(self.questions),
            "correct": self.correct_count,
            "remaining_time": self.time_remaining()
        }
    
    def get_results(self):
        """获取挑战结果"""
        elapsed_time = time.time() - self.start_time
        return {
            "total_questions": len(self.questions),
            "attempted": self.current_index,
            "correct": self.correct_count,
            "accuracy": (self.correct_count / self.current_index) * 100 if self.current_index > 0 else 0,
            "time_taken": min(elapsed_time, self.time_limit),
            "questions": self.questions
        }
    
    def _save_challenge_result(self):
        """保存挑战结果到用户数据"""
        elapsed_time = time.time() - self.start_time
        result = {
            "total_questions": len(self.questions),
            "attempted": self.current_index,
            "correct": self.correct_count,
            "accuracy": (self.correct_count / self.current_index) * 100 if self.current_index > 0 else 0,
            "time_taken": min(elapsed_time, self.time_limit),
            "questions": self.questions,
            "timestamp": time.time()
        }
        save_exercise_record("timed", result)