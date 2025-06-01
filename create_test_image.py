from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename="test_example.jpg"):
    """创建一个包含数学题的测试图片"""
    img = Image.new('RGB', (800, 600), color='white')
    d = ImageDraw.Draw(img)
    
    # 尝试加载字体，使用更大更清晰的字体
    try:
        font = ImageFont.truetype("arial.ttf", 72)  # 更大的字体
    except:
        font = ImageFont.load_default()
      # 添加一些数学题，使用更简单的格式和更大的间距
    d.text((100, 50), "9 + 3 = 12", fill=(0, 0, 0), font=font)  # 使用RGB元组指定黑色
    d.text((100, 150), "10 - 4 = 6", fill=(0, 0, 0), font=font)
    d.text((100, 250), "7 * 9 = 63", fill=(0, 0, 0), font=font)
    d.text((100, 350), "6 / 3 = 2", fill=(0, 0, 0), font=font)
    
    # 添加未带答案的题目，便于测试题目识别
    d.text((100, 450), "20 + 15 = ???", fill=(0, 0, 0), font=font)
    
    # 提高图片质量
    img.save(filename, quality=95)
    print(f"测试图片已创建: {os.path.abspath(filename)}")
    return filename

if __name__ == "__main__":
    create_test_image()
