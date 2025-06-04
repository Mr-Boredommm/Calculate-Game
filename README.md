# MathPop 数学练习系统

一个基于 PyQt6 的数学练习系统，集成了基础练习、计时练习、AI智能指导和手写批改功能。

## 功能特点

- 🧮 **基础练习**: 不限时数学练习，支持四则运算和多种难度
- ⏱️ **计时练习**: 限时挑战模式，提高计算速度
- 🤖 **AI智能指导**: 基于 DeepSeek API 的智能数学助手
- ✍️ **手写批改**: OCR 识别手写作业并自动批改

## 系统要求

- Python 3.8+
- PyQt6
- OpenCV (cv2)
- requests
- pytesseract (可选，用于OCR功能)

## 安装说明

1. 克隆项目
```bash
git clone [项目地址]
cd Calculate-Game
```

2. 安装依赖
```bash
pip install PyQt6 opencv-python requests
# 可选：安装OCR支持
pip install pytesseract
```

3. 运行程序
```bash
python main.py
```

## 文件结构

```
Calculate-Game/
├── main.py                 # 主程序入口
├── core/
│   ├── ui/
│   │   └── main_window.py   # 主UI界面
│   ├── features/
│   │   ├── practice.py      # 练习功能核心
│   │   ├── ai_assistant.py  # AI助手功能
│   │   └── ocr_grader.py    # OCR批改功能
│   └── utils/
│       ├── user_manager.py  # 用户管理
│       └── data_storage.py  # 数据存储
├── tests/
│   └── test_ocr.py         # OCR功能测试
├── docs/
│   └── API.md              # API文档
└── README.md               # 项目说明
```

## 使用说明

### 用户系统
- 注册新用户或使用现有账户登录
- 系统会自动保存学习进度和成绩

### 基础练习
1. 选择难度等级（简单/中等/困难）
2. 选择运算类型（加减乘除）
3. 点击"开始练习"开始答题
4. 使用"检查答案"验证结果

### 计时练习
1. 设置题目数量和时间限制
2. 选择难度和运算类型
3. 在限定时间内完成所有题目

### AI智能指导
1. 配置 DeepSeek API 密钥
2. 选择问题类型和难度
3. 输入数学问题获取AI解答

### 手写批改
1. 上传手写作业图片
2. 系统自动识别题目和答案
3. 获取批改结果和建议

## 配置说明

### AI助手配置
- 需要 DeepSeek API 密钥
- 在AI指导界面点击"配置API"进行设置

### OCR配置
- 需要安装 Tesseract OCR
- 支持多种图片格式

## 开发说明

项目采用模块化设计，各功能独立开发和测试。

## 许可证

[添加许可证信息]
