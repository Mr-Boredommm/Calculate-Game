import os
import json
import time
from datetime import datetime

# 确保用户数据目录存在
def ensure_user_data_dir():
    user_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    return user_data_dir

# 保存练习记录
def save_exercise_record(exercise_type, record):
    user_data_dir = ensure_user_data_dir()
    
    # 获取当前日期作为文件名
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"{exercise_type}_{today}.json"
    file_path = os.path.join(user_data_dir, filename)
    
    # 读取现有记录或创建新记录
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = {"records": []}
    else:
        data = {"records": []}
    
    # 添加时间戳
    if isinstance(record, dict) and "timestamp" not in record:
        record["timestamp"] = time.time()
    
    # 添加新记录
    data["records"].append(record)
    
    # 保存到文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 获取练习历史
def get_exercise_history(exercise_type, days=7):
    user_data_dir = ensure_user_data_dir()
    history = []
    
    # 获取最近几天的数据
    for i in range(days):
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f"{exercise_type}_{date}.json"
        file_path = os.path.join(user_data_dir, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    history.extend(data.get("records", []))
                except:
                    pass
    
    return history

# 计算统计数据
def calculate_statistics(history):
    if not history:
        return {
            "total_questions": 0,
            "correct_answers": 0,
            "accuracy": 0,
            "average_time": 0
        }
    
    total_questions = len(history)
    correct_answers = sum(1 for record in history if record.get("is_correct", False))
    
    # 计算平均用时
    times = [record.get("time_taken", 0) for record in history if "time_taken" in record]
    average_time = sum(times) / len(times) if times else 0
    
    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "accuracy": (correct_answers / total_questions) * 100 if total_questions > 0 else 0,
        "average_time": average_time
    }