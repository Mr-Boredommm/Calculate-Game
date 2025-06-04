import random
import time
from Utils import save_exercise_record

class BasicExercise:
    def __init__(self):
        self.current_question = None
        self.answer = None
        self.question_history = []
        self.correct_count = 0
        self.total_count = 0
        self.start_time = None
        
    def generate_question(self, operation_types, difficulty):
        """生成基于选定操作类型和难度的问题"""
        self.start_time = time.time()
        
        # 根据难度设置数字范围
        if difficulty == "简单":
            num_range = (1, 10)
        elif difficulty == "中等":
            num_range = (1, 50)
        else:  # 困难
            num_range = (1, 100)
            
        # 随机选择操作类型
        if not operation_types:
            operation = "+"  # 默认加法
        else:
            operation = random.choice(operation_types)
            
        # 生成操作数
        num1 = random.randint(num_range[0], num_range[1])
        num2 = random.randint(num_range[0], num_range[1])
        
        # 确保除法不会有除零问题并得到整数结果
        if operation == "/":
            # 先选择结果，再反推除数
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
        elif operation == "/":
            answer = num1 // num2
            
        # 格式化问题
        question = f"{num1} {operation} {num2} = ?"
        
        self.current_question = question
        self.answer = answer
        return question
    
    def check_answer(self, user_answer):
        """检查用户答案是否正确"""
        try:
            user_answer = int(user_answer)
            is_correct = user_answer == self.answer
            
            # 记录此题到历史
            elapsed_time = time.time() - self.start_time
            record = {
                "question": self.current_question,
                "correct_answer": self.answer,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "time_taken": elapsed_time
            }
            self.question_history.append(record)
            
            # 更新统计
            self.total_count += 1
            if is_correct:
                self.correct_count += 1
                
            # 保存记录到用户数据
            save_exercise_record("basic", record)
            
            return is_correct, self.answer
        except:
            return False, self.answer
    
    def get_stats(self):
        """获取当前练习统计"""
        return {
            "total": self.total_count,
            "correct": self.correct_count,
            "accuracy": (self.correct_count / self.total_count) * 100 if self.total_count > 0 else 0,
            "average_time": sum(record["time_taken"] for record in self.question_history) / len(self.question_history) if self.question_history else 0
        }
    
    def reset(self):
        """重置练习记录"""
        self.correct_count = 0
        self.total_count = 0
        self.question_history = []