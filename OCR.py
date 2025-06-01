import cv2
import numpy as np
import pytesseract
import re
from Game import Game

class OCRGrader:
    def __init__(self):
        self.game = Game()
        # 指定Tesseract路径
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # 根据实际安装路径调整
        print(f"Tesseract路径: {pytesseract.pytesseract.tesseract_cmd}")
    
    def preprocess_image(self, image_path):
        """预处理图片以提高OCR准确率"""
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise Exception(f"无法读取图片: {image_path}")
            
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 放大图像以提高识别率
        scale_factor = 1.5  # 不用放大太多
        height, width = gray.shape
        gray = cv2.resize(gray, (int(width * scale_factor), int(height * scale_factor)), 
                          interpolation=cv2.INTER_CUBIC)
        
        # 对比度增强 - 使用CLAHE（限制对比度自适应直方图均衡化）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # 去噪处理 - 使用双边滤波保留边缘
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # 使用Otsu阈值进行二值化
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 保存预处理后的图片以便调试
        cv2.imwrite("preprocessed_image.jpg", binary)
        print(f"已保存预处理图片到: preprocessed_image.jpg")
        
        return binary
    
    def extract_text(self, image):
        """使用OCR提取文本"""
        # 配置tesseract以优化数学符号和数字识别
        # 使用PSM 4 (假设单列多行文本)
        custom_config = r'--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789+-*/=? '
        text = pytesseract.image_to_string(image, config=custom_config)
        print(f"OCR提取的原始文本:\n{text}")
        return text
    
    def parse_problems_and_answers(self, text):
        """从识别的文本中解析题目和答案"""
        lines = text.strip().split('\n')
        problems = []
        answers = []
        
        for line in lines:
            # 检查是否是题目行 (格式如 "5 + 3 = ???")
            problem_match = re.match(r'(\d+)\s*([+\-*/])\s*(\d+)\s*=\s*(\?+|\d+)', line)
            if problem_match:
                a, op, b, ans = problem_match.groups()
                if ans.strip('?') == '':  # 如果答案部分是问号，则这是一个题目
                    problems.append((int(a), op, int(b)))
                else:  # 否则是一个带答案的题目
                    problems.append((int(a), op, int(b)))
                    answers.append(int(ans))
            
            # 检查是否是单独的答案行
            elif re.match(r'^\d+$', line.strip()):
                answers.append(int(line.strip()))
        
        return problems, answers
    
    def calculate_expected_answers(self, problems):
        """根据题目计算预期答案"""
        expected_answers = []
        for a, op, b in problems:
            if op == '+':
                expected_answers.append(a + b)
            elif op == '-':
                expected_answers.append(a - b)
            elif op == '*':
                expected_answers.append(a * b)
            elif op == '/':
                if b != 0:
                    expected_answers.append(a // b)
                else:
                    expected_answers.append(None)  # 除以零的情况
        return expected_answers
    
    def grade_homework(self, image_path):
        """批改手写作业"""
        # 预处理图片
        processed_image = self.preprocess_image(image_path)
        
        # 提取文本
        text = self.extract_text(processed_image)
        
        # 解析题目和答案
        problems, answers = self.parse_problems_and_answers(text)
        
        # 计算预期答案
        expected_answers = self.calculate_expected_answers(problems)
        
        # 准备输出结果
        detected_problems_str = ""
        for a, op, b in problems:
            detected_problems_str += f"{a} {op} {b} = ???\n"
        
        detected_answers_str = "\n".join(str(ans) for ans in answers)
        
        # 准备批改结果
        grading_results = []
        
        # 处理题目和答案数量不匹配的情况
        if len(problems) > len(answers):
            # 如果题目数量多于答案数量，表示有些题目未作答
            missing_count = len(problems) - len(answers)
            print(f"发现{missing_count}道题目未作答")
            # 扩展答案列表，用None表示未作答的题目
            answers.extend([None] * missing_count)
        
        # 逐题批改
        for i, expected in enumerate(expected_answers):
            if i >= len(answers):
                # 这种情况不应该发生，因为我们已经扩展了答案列表
                break
                
            actual = answers[i]
            if actual is None:
                # 未作答的题目
                grading_results.append(f"未作答，正确答案是: {expected}")
            elif expected == actual:
                grading_results.append(f"对了，牢弟！")
            else:
                grading_results.append(f"错了QAQ，正确答案是: {expected}")
        
        grading_results_str = "\n".join(grading_results)
        
        return {
            "detected_problems": detected_problems_str,
            "detected_answers": detected_answers_str,
            "grading_results": grading_results_str
        }

# 示例用法
if __name__ == "__main__":
    grader = OCRGrader()
    result = grader.grade_homework("test_example.jpg")
    print("检测到的题目:")
    print(result["detected_problems"])
    print("\n检测到的答案:")
    print(result["detected_answers"])
    print("\n批改结果:")
    print(result["grading_results"])
