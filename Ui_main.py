from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QAbstractItemView, QHBoxLayout,
                               QLabel, QStackedWidget, QTreeWidget,
                               QVBoxLayout, QWidget, QApplication, QFrame, QPushButton)
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


class Ui_Form(QWidget):
    def __init__(self, /):
        super().__init__()

    def setupUi(self, form):
        if not form.objectName():
            form.setObjectName(u"Form")
        screen = QApplication.primaryScreen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        x = (screen_width - 1300) // 2
        y = (screen_height - 800) // 2
        form.setGeometry(x, y, 1300, 800)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setMaximumSize(QSize(200, 16777215))

        self.treeWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setExpandsOnDoubleClick(False)

        self.horizontalLayout.addWidget(self.treeWidget)
        self.stackedWidget = QStackedWidget()
        self.page = QWidget()
        self.page.setObjectName("homePage")
        self.setStyleSheet("""
            QWidget#homePage {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fc, stop:0.5 #eef1f5, stop:1 #e4e8ef);
                border: none;
            }
            QLabel {
                background: transparent;
                color: #2d3436;
            }
        """)
        self.index_layout = QVBoxLayout()
        self.logo_label = QLabel("🔧 开源工具箱")
        self.logo_label.setAlignment(Qt.AlignmentFlag(4))
        self.logo_label.setStyleSheet("""
            color: #2d3436;
            font-size: 32px;
            font-weight: bold;
            font-family: 'Consolas', 'Microsoft YaHei', monospace;
            letter-spacing: 6px;
        """)
        self.subtitle = QLabel("让重复工作，一键完成")
        self.subtitle.setAlignment(Qt.AlignmentFlag(4))
        self.subtitle.setStyleSheet("""
            color: #636e72;
            font-size: 16px;
            font-family: 'Microsoft YaHei', sans-serif;
            letter-spacing: 3px;
        """)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape(4))
        self.line.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent, stop:0.3 #0984e3, 
                stop:0.7 #0984e3, stop:1 transparent);
            max-height: 1px;
            border: none;
            margin: 10px 80px;
        """)
        self.quote_label = QLabel()
        self.quote_label.setAlignment(Qt.AlignmentFlag(4))
        self.quote_label.setWordWrap(True)
        self.quote_label.setStyleSheet("""
                    color: #2d3436;
                    font-size: 28px;
                    font-family: 'Georgia', 'Times New Roman', serif;
                    font-style: italic;
                    line-height: 1.8;
                    padding: 20px 40px;
                """)

        info_layout = QHBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag(4))
        info_layout.setSpacing(30)
        self.count_label = QLabel()
        self.count_label.setStyleSheet("""
                    color: #636e72;
                    font-size: 14px;
                    font-family: 'Consolas', monospace;
                """)
        info_layout.addWidget(self.count_label)

        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignmentFlag(4))
        footer_layout.setSpacing(20)

        self.version_label = QLabel()
        self.version_label.setStyleSheet("""
                    color: #b2bec3;
                    font-size: 13px;
                    font-family: 'Consolas', monospace;
                """)
        footer_layout.addWidget(self.version_label)

        dot = QLabel("·")
        dot.setStyleSheet("color: #b2bec3; font-size: 13px;")
        footer_layout.addWidget(dot)

        # GitHub 链接按钮
        self.github_btn = QPushButton("⭐ Gitee")
        self.github_btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #636e72;
                        border: 1px solid rgba(9, 132, 227, 0.2);
                        border-radius: 12px;
                        padding: 4px 18px;
                        font-size: 12px;
                        font-family: 'Consolas', monospace;
                    }
                    QPushButton:hover {
                        background: rgba(9, 132, 227, 0.08);
                        border-color: #0984e3;
                        color: #0984e3;
                    }
                """)
        self.github_btn.setCursor(Qt.PointingHandCursor)
        self.github_btn.clicked.connect(self.open_gitee)

        footer_layout.addWidget(self.github_btn)

        # 状态指示器
        status_label = QLabel("● 运行中")
        status_label.setStyleSheet("""
                    color: #00b894;
                    font-size: 12px;
                    font-family: 'Consolas', monospace;
                """)
        footer_layout.addWidget(status_label)
        self.index_layout.addStretch()
        self.index_layout.addWidget(self.logo_label)
        self.index_layout.addWidget(self.subtitle)
        self.index_layout.addWidget(self.line)
        self.index_layout.addWidget(self.quote_label)
        self.index_layout.addLayout(info_layout)
        self.index_layout.addLayout(footer_layout)
        self.index_layout.addStretch()
        self.page.setLayout(self.index_layout)
        self.stackedWidget.addWidget(self.page)
        self.horizontalLayout.addWidget(self.stackedWidget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.setLayout(self.verticalLayout)

    def open_gitee(self):
        QDesktopServices.openUrl(QUrl("https://gitee.com/fuse_tool/fuse_tool_box"))