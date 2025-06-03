import cv2
import numpy as np
import re
from paddleocr import PaddleOCR
from Game import Game

class OCRGrader:
    def __init__(self):
        self.game = Game()
        # 初始化PaddleOCR，使用中英文模型，启用方向分类器
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
        print("PaddleOCR初始化完成")
    
    def preprocess_for_handwriting(self, image_path):
        """针对手写体优化的图像预处理"""
        image = cv2.imread(image_path)
        if image is None:
            raise Exception(f"无法读取图片: {image_path}")
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 超高分辨率放大（手写体需要更高分辨率）
        scale_factor = 3.0
        height, width = gray.shape
        gray = cv2.resize(gray, (int(width * scale_factor), int(height * scale_factor)), 
                          interpolation=cv2.INTER_CUBIC)
        
        # 多步骤降噪处理
        # 1. 非局部均值降噪
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # 2. 高斯模糊减少噪声
        blurred = cv2.GaussianBlur(denoised, (3, 3), 0)
        
        # 3. 锐化处理增强笔画
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(blurred, -1, kernel)
        
        # 4. 自适应阈值处理（对手写体更有效）
        binary = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 15, 4)
        
        # 5. 形态学操作连接断开的笔画
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 6. 去除小噪点
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # 保存预处理后的图片以便调试
        cv2.imwrite("preprocessed_handwriting.jpg", binary)
        print(f"已保存手写体预处理图片到: preprocessed_handwriting.jpg")
        
        return binary
    
    def extract_text_with_paddle(self, image_path):
        """使用PaddleOCR提取手写文本"""
        try:
            # 对原图和预处理后的图都进行识别
            results = []
            
            # 1. 识别原图
            print("正在识别原图...")
            original_result = self.ocr.ocr(image_path, cls=True)
            if original_result and original_result[0]:
                results.extend(original_result[0])
            
            # 2. 识别预处理后的图
            print("正在识别预处理图...")
            preprocessed_image = self.preprocess_for_handwriting(image_path)
            cv2.imwrite("temp_preprocessed.jpg", preprocessed_image)
            preprocessed_result = self.ocr.ocr("temp_preprocessed.jpg", cls=True)
            if preprocessed_result and preprocessed_result[0]:
                results.extend(preprocessed_result[0])
            
            # 合并并过滤结果
            extracted_text = ""
            confidence_threshold = 0.3  # 降低置信度阈值，因为手写体识别较困难
            
            for line in results:
                if line and len(line) >= 2:
                    text = line[1][0]  # 获取识别的文本
                    confidence = line[1][1]  # 获取置信度
                    
                    if confidence > confidence_threshold:
                        # 清理文本，只保留数字和数学符号
                        cleaned_text = re.sub(r'[^0-9+\-*/=?\s]', '', text)
                        if cleaned_text.strip():
                            extracted_text += cleaned_text + "\n"
            
            print(f"PaddleOCR提取的文本:\n{extracted_text}")
            return extracted_text
            
        except Exception as e:
            print(f"PaddleOCR识别失败: {e}")
            return ""
    
    def parse_problems_and_answers(self, text):
        """从识别的文本中解析题目和答案，增强手写内容的识别能力"""
        lines = text.strip().split('\n')
        problems = []
        answers = []
        
        # 清理行，移除多余空格
        cleaned_lines = []
        for line in lines:
            cleaned = re.sub(r'\s+', ' ', line.strip())
            if cleaned:
                cleaned_lines.append(cleaned)
        
        # 定义多种匹配模式
        patterns = [
            r'(\d+)\s*([+\-*/])\s*(\d+)\s*=\s*(\?+|\d+)',  # 标准格式: 5 + 3 = 8
            r'(\d+)\s*([+\-*/])\s*(\d+)\s*=\s*(\?+)',       # 题目格式: 5 + 3 = ???
            r'(\d+)\s*([+\-*/])\s*(\d+)',                   # 只有表达式: 5 + 3
        ]
        
        standalone_answer_pattern = r'^\s*(\d+)\s*$'
        
        i = 0
        while i < len(cleaned_lines):
            line = cleaned_lines[i]
            matched = False
            
            # 尝试匹配各种题目模式
            for pattern in patterns:
                problem_match = re.search(pattern, line)
                if problem_match:
                    try:
                        if len(problem_match.groups()) == 4:  # 完整格式
                            a, op, b, ans = problem_match.groups()
                            a, b = int(a), int(b)
                            problems.append((a, op, b))
                            
                            # 检查是否包含数字答案
                            if ans and not ans.strip('?'):
                                try:
                                    answers.append(int(ans))
                                except ValueError:
                                    pass
                        else:  # 只有表达式
                            a, op, b = problem_match.groups()
                            a, b = int(a), int(b)
                            problems.append((a, op, b))
                            
                            # 查看下一行是否是答案
                            if i + 1 < len(cleaned_lines):
                                next_line = cleaned_lines[i + 1]
                                answer_match = re.search(standalone_answer_pattern, next_line)
                                if answer_match:
                                    try:
                                        answers.append(int(answer_match.group(1)))
                                        i += 1  # 跳过答案行
                                    except ValueError:
                                        pass
                        
                        matched = True
                        break
                        
                    except ValueError as e:
                        print(f"解析数字失败: {problem_match.groups()}, 错误: {e}")
                        continue
            
            # 如果不是题目，检查是否是单独的答案
            if not matched:
                answer_match = re.search(standalone_answer_pattern, line)
                if answer_match:
                    try:
                        answers.append(int(answer_match.group(1)))
                    except ValueError:
                        pass
            
            i += 1
        
        print(f"解析结果: {len(problems)}道题目, {len(answers)}个答案")
        print(f"题目: {problems}")
        print(f"答案: {answers}")
        
        return problems, answers
    
    def calculate_expected_answers(self, problems):
        """根据题目计算预期答案"""
        expected_answers = []
        for a, op, b in problems:
            try:
                if op == '+':
                    expected_answers.append(a + b)
                elif op == '-':
                    expected_answers.append(a - b)
                elif op == '*':
                    expected_answers.append(a * b)
                elif op == '/':
                    if b != 0:
                        expected_answers.append(a // b)  # 整数除法
                    else:
                        expected_answers.append(None)  # 除以零的情况
                else:
                    expected_answers.append(None)  # 未知运算符
            except Exception as e:
                print(f"计算错误: {a} {op} {b}, 错误: {e}")
                expected_answers.append(None)
        
        return expected_answers
    
    def generate_grading_results(self, problems, answers, expected_answers):
        """生成批改结果"""
        # 准备输出结果
        detected_problems_str = ""
        for a, op, b in problems:
            detected_problems_str += f"{a} {op} {b} = ???\n"
        
        # 处理答案显示
        detected_answers_str = ""
        for i, ans in enumerate(answers):
            if ans is not None:
                detected_answers_str += f"第{i+1}题: {ans}\n"
            else:
                detected_answers_str += f"第{i+1}题: 未作答\n"
        
        # 准备批改结果
        grading_results = []
        
        # 处理题目和答案数量不匹配的情况
        if len(problems) > len(answers):
            missing_count = len(problems) - len(answers)
            print(f"发现{missing_count}道题目未作答")
            answers.extend([None] * missing_count)
        
        # 逐题批改
        for i, expected in enumerate(expected_answers):
            if i >= len(answers):
                break
            
            actual = answers[i]
            if expected is None:
                grading_results.append(f"第{i+1}题: 题目有误，无法计算")
            elif actual is None:
                grading_results.append(f"第{i+1}题: 未作答，正确答案是 {expected}")
            elif expected == actual:
                grading_results.append(f"第{i+1}题: 正确！答案是 {expected}")
            else:
                grading_results.append(f"第{i+1}题: 错误，你的答案是 {actual}，正确答案是 {expected}")
        
        grading_results_str = "\n".join(grading_results)
        
        return {
            "detected_problems": detected_problems_str,
            "detected_answers": detected_answers_str,
            "grading_results": grading_results_str
        }
    
    def grade_homework(self, image_path):
        """批改手写作业"""
        try:
            # 使用PaddleOCR提取文本
            text = self.extract_text_with_paddle(image_path)
            
            if not text.strip():
                return {
                    "detected_problems": "未检测到任何题目",
                    "detected_answers": "未检测到任何答案", 
                    "grading_results": "OCR识别失败，请检查图片质量"
                }
            
            # 解析题目和答案
            problems, answers = self.parse_problems_and_answers(text)
            
            if not problems:
                return {
                    "detected_problems": "未解析到有效题目",
                    "detected_answers": f"识别到的原始文本:\n{text}",
                    "grading_results": "未能解析出数学题目，请检查图片内容"
                }
            
            # 计算预期答案
            expected_answers = self.calculate_expected_answers(problems)
            
            # 生成批改结果
            return self.generate_grading_results(problems, answers, expected_answers)
            
        except Exception as e:
            print(f"批改过程出错: {e}")
            return {
                "detected_problems": "处理失败",
                "detected_answers": "处理失败",
                "grading_results": f"批改过程出错: {str(e)}"
            }

# 示例用法
if __name__ == "__main__":
    try:
        grader = OCRGrader()
        result = grader.grade_homework("test_example.jpg")
        print("检测到的题目:")
        print(result["detected_problems"])
        print("\n检测到的答案:")
        print(result["detected_answers"])
        print("\n批改结果:")
        print(result["grading_results"])
    except Exception as e:
        print(f"程序运行出错: {e}")
        print("请确保已安装PaddleOCR: pip install paddlepaddle paddleocr")