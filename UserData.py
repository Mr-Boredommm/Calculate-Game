import os
import json
from datetime import datetime
from Utils import ensure_user_data_dir, calculate_statistics, get_exercise_history

class UserData:
    def __init__(self):
        self.user_data_dir = ensure_user_data_dir()
        self.current_user = None
        self.user_settings = {}
        
    def login(self, username):
        """简单的用户登录"""
        self.current_user = username
        self._load_user_settings()
        return True
    
    def logout(self):
        """用户登出"""
        self.save_settings()
        self.current_user = None
        self.user_settings = {}
    
    def _load_user_settings(self):
        """加载用户设置"""
        if not self.current_user:
            return
            
        settings_path = os.path.join(self.user_data_dir, f"{self.current_user}_settings.json")
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    self.user_settings = json.load(f)
            except:
                self.user_settings = self._get_default_settings()
        else:
            self.user_settings = self._get_default_settings()
    
    def _get_default_settings(self):
        """获取默认设置"""
        return {
            "difficulty": "中等",
            "operations": ["+", "-", "*", "/"],
            "timed_mode": {
                "time_limit": 60,
                "question_count": 10
            },
            "last_login": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def save_settings(self):
        """保存用户设置"""
        if not self.current_user:
            return False
            
        settings_path = os.path.join(self.user_data_dir, f"{self.current_user}_settings.json")
        
        # 更新最后登录时间
        self.user_settings["last_login"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_settings, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def update_setting(self, key, value):
        """更新特定设置"""
        if not self.current_user:
            return False
            
        # 处理嵌套设置
        if "." in key:
            main_key, sub_key = key.split(".", 1)
            if main_key in self.user_settings and isinstance(self.user_settings[main_key], dict):
                self.user_settings[main_key][sub_key] = value
            else:
                return False
        else:
            self.user_settings[key] = value
            
        return self.save_settings()
    
    def get_user_statistics(self):
        """获取用户统计数据"""
        if not self.current_user:
            return {}
            
        # 获取基础练习统计
        basic_history = get_exercise_history("basic")
        basic_stats = calculate_statistics(basic_history)
        
        # 获取计时模式统计
        timed_history = get_exercise_history("timed")
        timed_stats = {}
        
        if timed_history:
            total_challenges = len(timed_history)
            total_questions = sum(item.get("total_questions", 0) for item in timed_history)
            attempted_questions = sum(item.get("attempted", 0) for item in timed_history)
            correct_answers = sum(item.get("correct", 0) for item in timed_history)
            
            timed_stats = {
                "total_challenges": total_challenges,
                "total_questions": total_questions,
                "attempted_questions": attempted_questions,
                "correct_answers": correct_answers,
                "accuracy": (correct_answers / attempted_questions * 100) if attempted_questions > 0 else 0,
                "completion_rate": (attempted_questions / total_questions * 100) if total_questions > 0 else 0
            }
        
        return {
            "basic_exercise": basic_stats,
            "timed_mode": timed_stats,
            "user_since": self._get_user_creation_date()
        }
    
    def _get_user_creation_date(self):
        """获取用户创建日期"""
        if not self.current_user:
            return None
            
        settings_path = os.path.join(self.user_data_dir, f"{self.current_user}_settings.json")
        
        if not os.path.exists(settings_path):
            return datetime.now().strftime('%Y-%m-%d')
            
        return datetime.fromtimestamp(os.path.getctime(settings_path)).strftime('%Y-%m-%d')