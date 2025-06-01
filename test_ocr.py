from OCR import OCRGrader
import os
from PyQt5.QtWidgets import QApplication
import sys

def test_ocr_grader():
    # 初始化OCR批改器
    app = QApplication(sys.argv)  # 创建QApplication实例
    grader = OCRGrader()
      # 设置测试图片路径
    test_image_path = "test_example.jpg"  # 使用新创建的测试图片
    
    # 确认图片文件存在
    if not os.path.exists(test_image_path):
        print(f"错误: 图片 {test_image_path} 不存在!")
        return
    
    # 运行OCR批改功能
    try:
        result = grader.grade_homework(test_image_path)
        
        # 输出结果
        print("=" * 50)
        print("OCR识别结果测试")
        print("=" * 50)
        print("检测到的题目:")
        print(result["detected_problems"])
        
        print("\n检测到的答案:")
        print(result["detected_answers"])
        
        print("\n批改结果:")
        print(result["grading_results"])
        print("=" * 50)
        
        # 如果没有检测到题目或答案，可能是识别问题
        if not result["detected_problems"] or not result["detected_answers"]:
            print("警告: OCR可能未能正确识别题目或答案，请检查图片质量和清晰度。")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_ocr_grader()