from OCR import OCRGrader
import os

def test_ocr_grader():
    """测试OCR批改器功能"""
    # 初始化OCR批改器
    grader = OCRGrader()
    
    # 设置测试图片路径
    test_image_path = "test_example.jpg"  # 使用测试图片
    
    # 确认图片文件存在
    if not os.path.exists(test_image_path):
        print(f"错误: 图片 {test_image_path} 不存在!")
        print("请将包含手写数学题的图片保存为 test_example.jpg")
        return
    
    print(f"正在处理图片: {test_image_path}")
    print("PaddleOCR初始化和识别可能需要一些时间，请耐心等待...")
    
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
        
        # 如果没有检测到题目或答案，提供手动校正选项
        if "未检测到任何题目" in result["detected_problems"] or "未解析到有效题目" in result["detected_problems"]:
            print("\n警告: OCR可能未能正确识别题目或答案，请检查图片质量和清晰度。")
            print("建议:")
            print("1. 确保图片清晰，光照充足")
            print("2. 手写内容尽量工整")
            print("3. 题目格式如: 5 + 3 = ? 或 5 + 3 = 8")
            
            # 提供手动校正选项
            manual_correction = input("\n是否要手动输入题目和答案进行校正测试？(y/n): ")
            if manual_correction.lower() == 'y':
                problems = []
                answers = []
                
                try:
                    num_problems = int(input("请输入题目数量: "))
                    for i in range(num_problems):
                        print(f"\n题目 #{i+1}:")
                        a = int(input("第一个数字: "))
                        op = input("运算符 (+, -, *, /): ").strip()
                        if op not in ['+', '-', '*', '/']:
                            print("无效的运算符，使用默认值 +")
                            op = '+'
                        b = int(input("第二个数字: "))
                        problems.append((a, op, b))
                        
                        has_answer = input("学生是否作答了这道题? (y/n): ").strip().lower()
                        if has_answer == 'y':
                            answer = int(input("学生的答案: "))
                            answers.append(answer)
                        else:
                            answers.append(None)
                    
                    # 使用手动输入的数据重新计算结果
                    expected_answers = grader.calculate_expected_answers(problems)
                    result = grader.generate_grading_results(problems, answers, expected_answers)
                    
                    print("\n" + "=" * 50)
                    print("手动校正后的批改结果:")
                    print("=" * 50)
                    print("检测到的题目:")
                    print(result["detected_problems"])
                    
                    print("\n检测到的答案:")
                    print(result["detected_answers"])
                    
                    print("\n批改结果:")
                    print(result["grading_results"])
                    print("=" * 50)
                    
                except ValueError as e:
                    print(f"输入错误: {e}")
                except Exception as e:
                    print(f"手动校正失败: {e}")
        else:
            print("\n✅ OCR识别成功！")
            
    except Exception as e:
        print(f"测试失败: {e}")
        print("可能的原因:")
        print("1. PaddleOCR未正确安装")
        print("2. 图片格式不支持")
        print("3. 内存不足")
        print("\n解决建议:")
        print("1. 重新安装PaddleOCR: pip install paddlepaddle paddleocr")
        print("2. 检查图片格式（支持jpg, png等）")
        print("3. 关闭其他程序释放内存")

def create_test_image_info():
    """显示测试图片要求"""
    print("\n测试图片要求:")
    print("=" * 30)
    print("1. 文件名: test_example.jpg")
    print("2. 内容: 手写的数学四则运算题")
    print("3. 格式示例:")
    print("   5 + 3 = 8")
    print("   7 - 2 = ?")
    print("   4 * 6 = 24")
    print("   9 / 3 = ?")
    print("4. 建议:")
    print("   - 字迹工整清晰")
    print("   - 背景简洁")
    print("   - 光线充足")
    print("   - 避免反光和阴影")
    print("=" * 30)

if __name__ == "__main__":
    print("PaddleOCR 手写数学题批改器测试")
    print("=" * 40)
    
    # 显示测试图片要求
    create_test_image_info()
    
    # 运行测试
    test_ocr_grader()
    
    print("\n测试完成！")