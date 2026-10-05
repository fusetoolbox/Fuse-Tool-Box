from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class Ui_page(QWidget):
    def __init__(self, /):
        super().__init__()
        self.page=QWidget()
        self.layout=QVBoxLayout()
        self.label=QLabel("我是pdf添加水印页面")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)