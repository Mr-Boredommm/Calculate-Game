from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # 主布局
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        # 模式选择区域
        self.modeSelectionFrame = QtWidgets.QFrame(self.centralwidget)
        self.modeSelectionLayout = QtWidgets.QHBoxLayout(self.modeSelectionFrame)
        
        self.basicModeBtn = QtWidgets.QPushButton("基础练习")
        self.basicModeBtn.setMinimumHeight(40)
        self.timedModeBtn = QtWidgets.QPushButton("计时模式")
        self.timedModeBtn.setMinimumHeight(40)
        
        self.modeSelectionLayout.addWidget(self.basicModeBtn)
        self.modeSelectionLayout.addWidget(self.timedModeBtn)
        self.mainLayout.addWidget(self.modeSelectionFrame)
        
        # 堆叠窗口，用于切换不同模式
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.mainLayout.addWidget(self.stackedWidget)
        
        # 页面1：基础练习
        self.basicExercisePage = QtWidgets.QWidget()
        self.basicLayout = QtWidgets.QVBoxLayout(self.basicExercisePage)
        
        # 难度选择
        self.difficultyGroup = QtWidgets.QGroupBox("难度选择")
        self.difficultyLayout = QtWidgets.QHBoxLayout()
        self.easyRadioBtn = QtWidgets.QRadioButton("简单")
        self.mediumRadioBtn = QtWidgets.QRadioButton("中等")
        self.mediumRadioBtn.setChecked(True)
        self.hardRadioBtn = QtWidgets.QRadioButton("困难")
        
        self.difficultyLayout.addWidget(self.easyRadioBtn)
        self.difficultyLayout.addWidget(self.mediumRadioBtn)
        self.difficultyLayout.addWidget(self.hardRadioBtn)
        self.difficultyGroup.setLayout(self.difficultyLayout)
        self.basicLayout.addWidget(self.difficultyGroup)
        
        # 运算类型选择
        self.operationGroup = QtWidgets.QGroupBox("选择运算类型")
        self.operationLayout = QtWidgets.QHBoxLayout()
        self.addCheckBox = QtWidgets.QCheckBox("加法(+)")
        self.addCheckBox.setChecked(True)
        self.subtractCheckBox = QtWidgets.QCheckBox("减法(-)")
        self.multiplyCheckBox = QtWidgets.QCheckBox("乘法(×)")
        self.divideCheckBox = QtWidgets.QCheckBox("除法(÷)")
        
        self.operationLayout.addWidget(self.addCheckBox)
        self.operationLayout.addWidget(self.subtractCheckBox)
        self.operationLayout.addWidget(self.multiplyCheckBox)
        self.operationLayout.addWidget(self.divideCheckBox)
        self.operationGroup.setLayout(self.operationLayout)
        self.basicLayout.addWidget(self.operationGroup)
        # 问题显示区域
        self.questionFrame = QtWidgets.QFrame()
        self.questionLayout = QtWidgets.QVBoxLayout(self.questionFrame)
        self.questionLabel = QtWidgets.QLabel("点击\"生成问题\"按钮开始")
        self.questionLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.questionLabel.setFont(font)
        self.questionLayout.addWidget(self.questionLabel)
        
        self.answerInput = QtWidgets.QLineEdit()
        self.answerInput.setPlaceholderText("输入你的答案")
        self.answerInput.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.answerInput.setFont(font)
        self.questionLayout.addWidget(self.answerInput)
        
        self.resultLabel = QtWidgets.QLabel("")
        self.resultLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.resultLabel.setFont(font)
        self.questionLayout.addWidget(self.resultLabel)
        
        self.statsLabel = QtWidgets.QLabel("统计: 0/0 正确率: 0.0%")
        self.statsLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.questionLayout.addWidget(self.statsLabel)
        
        self.basicLayout.addWidget(self.questionFrame)
        
        # 按钮区域
        self.buttonFrame = QtWidgets.QFrame()
        self.buttonLayout = QtWidgets.QHBoxLayout(self.buttonFrame)
        
        self.generateBtn = QtWidgets.QPushButton("生成问题")
        self.generateBtn.setMinimumHeight(40)
        self.submitBtn = QtWidgets.QPushButton("提交答案")
        self.submitBtn.setMinimumHeight(40)
        
        self.buttonLayout.addWidget(self.generateBtn)
        self.buttonLayout.addWidget(self.submitBtn)
        self.basicLayout.addWidget(self.buttonFrame)
        
        # 添加基础练习页面到堆叠窗口
        self.stackedWidget.addWidget(self.basicExercisePage)
        
        # 页面2：计时模式
        self.timedModePage = QtWidgets.QWidget()
        self.timedLayout = QtWidgets.QVBoxLayout(self.timedModePage)
        
        # 难度和运算类型设置
        self.timedSettingsFrame = QtWidgets.QFrame()
        self.timedSettingsLayout = QtWidgets.QHBoxLayout(self.timedSettingsFrame)
        
        # 难度选择
        self.timedDifficultyGroup = QtWidgets.QGroupBox("难度选择")
        self.timedDifficultyLayout = QtWidgets.QVBoxLayout()
        self.timedEasyRadio = QtWidgets.QRadioButton("简单")
        self.timedMediumRadio = QtWidgets.QRadioButton("中等")
        self.timedMediumRadio.setChecked(True)
        self.timedHardRadio = QtWidgets.QRadioButton("困难")
        
        self.timedDifficultyLayout.addWidget(self.timedEasyRadio)
        self.timedDifficultyLayout.addWidget(self.timedMediumRadio)
        self.timedDifficultyLayout.addWidget(self.timedHardRadio)
        self.timedDifficultyGroup.setLayout(self.timedDifficultyLayout)
        self.timedSettingsLayout.addWidget(self.timedDifficultyGroup)
        
        # 运算类型选择
        self.timedOperationGroup = QtWidgets.QGroupBox("运算类型")
        self.timedOperationLayout = QtWidgets.QVBoxLayout()
        self.timedAddCheck = QtWidgets.QCheckBox("加法(+)")
        self.timedAddCheck.setChecked(True)
        self.timedSubtractCheck = QtWidgets.QCheckBox("减法(-)")
        self.timedMultiplyCheck = QtWidgets.QCheckBox("乘法(×)")
        self.timedDivideCheck = QtWidgets.QCheckBox("除法(÷)")
        
        self.timedOperationLayout.addWidget(self.timedAddCheck)
        self.timedOperationLayout.addWidget(self.timedSubtractCheck)
        self.timedOperationLayout.addWidget(self.timedMultiplyCheck)
        self.timedOperationLayout.addWidget(self.timedDivideCheck)
        self.timedOperationGroup.setLayout(self.timedOperationLayout)
        self.timedSettingsLayout.addWidget(self.timedOperationGroup)
        
        # 时间和数量设置
        self.timedConfigGroup = QtWidgets.QGroupBox("挑战配置")
        self.timedConfigLayout = QtWidgets.QVBoxLayout()
        
        self.timeLabel = QtWidgets.QLabel("时间限制(秒):")
        self.timeSpinBox = QtWidgets.QSpinBox()
        self.timeSpinBox.setMinimum(10)
        self.timeSpinBox.setMaximum(300)
        self.timeSpinBox.setValue(60)
        self.timeSpinBox.setSingleStep(10)
        
        self.questionCountLabel = QtWidgets.QLabel("题目数量:")
        self.questionCountSpinBox = QtWidgets.QSpinBox()
        self.questionCountSpinBox.setMinimum(5)
        self.questionCountSpinBox.setMaximum(100)
        self.questionCountSpinBox.setValue(10)
        
        self.timedConfigLayout.addWidget(self.timeLabel)
        self.timedConfigLayout.addWidget(self.timeSpinBox)
        self.timedConfigLayout.addWidget(self.questionCountLabel)
        self.timedConfigLayout.addWidget(self.questionCountSpinBox)
        self.timedConfigGroup.setLayout(self.timedConfigLayout)
        self.timedSettingsLayout.addWidget(self.timedConfigGroup)
        
        self.timedLayout.addWidget(self.timedSettingsFrame)
        
        # 计时模式问题显示区域
        self.timedQuestionFrame = QtWidgets.QFrame()
        self.timedQuestionLayout = QtWidgets.QVBoxLayout(self.timedQuestionFrame)
        
        self.timedTimeLabel = QtWidgets.QLabel("剩余时间: --秒")
        self.timedTimeLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.timedTimeLabel.setFont(font)
        self.timedQuestionLayout.addWidget(self.timedTimeLabel)
        self.progressLabel = QtWidgets.QLabel("题目: --/-- 正确: --")
        self.progressLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.timedQuestionLayout.addWidget(self.progressLabel)
        
        self.timedQuestionLabel = QtWidgets.QLabel("点击\"开始\"按钮开始挑战")
        self.timedQuestionLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.timedQuestionLabel.setFont(font)
        self.timedQuestionLayout.addWidget(self.timedQuestionLabel)
        
        self.timedAnswerInput = QtWidgets.QLineEdit()
        self.timedAnswerInput.setPlaceholderText("输入你的答案")
        self.timedAnswerInput.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.timedAnswerInput.setFont(font)
        self.timedQuestionLayout.addWidget(self.timedAnswerInput)
        
        self.timedResultLabel = QtWidgets.QLabel("")
        self.timedResultLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.timedResultLabel.setFont(font)
        self.timedQuestionLayout.addWidget(self.timedResultLabel)
        
        self.timedLayout.addWidget(self.timedQuestionFrame)
        
        # 计时模式按钮区域
        self.timedButtonFrame = QtWidgets.QFrame()
        self.timedButtonLayout = QtWidgets.QHBoxLayout(self.timedButtonFrame)
        
        self.startTimedBtn = QtWidgets.QPushButton("开始挑战")
        self.startTimedBtn.setMinimumHeight(40)
        self.submitTimedBtn = QtWidgets.QPushButton("提交答案")
        self.submitTimedBtn.setMinimumHeight(40)
        self.submitTimedBtn.setEnabled(False)  # 开始前不可用
        
        self.timedButtonLayout.addWidget(self.startTimedBtn)
        self.timedButtonLayout.addWidget(self.submitTimedBtn)
        self.timedLayout.addWidget(self.timedButtonFrame)
        
        # 添加计时模式页面到堆叠窗口
        self.stackedWidget.addWidget(self.timedModePage)
        
        # 设置中央窗口和状态栏
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        # 设置窗口标题
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "速算练习助手"))