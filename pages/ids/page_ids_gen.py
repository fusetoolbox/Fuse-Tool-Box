from PySide6.QtCore import QTimer, QDateTime
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QPlainTextEdit, QApplication, QMessageBox)

import pyperclip

class Ui_page(QWidget):
    def __init__(self, /):
        super().__init__()

        self.layout = QHBoxLayout()
        self.groupbox = QGroupBox()
        self.groupbox.setTitle("教程和配置参数")
        self.groupbox.setMaximumWidth(400)
        self.group_lay = QVBoxLayout()

        self.jc_label = QLabel()
        show_text = """
                <html>
<head>
<style>
    body {
        font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
        padding: 5px 5px 0 5px;
        margin: 0;
        color: #2c3e50;
    }
    .title {
        font-size: 20px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding-bottom: 8px;
        border-bottom: 2px solid #3498db;
        margin-bottom: 10px;
    }
    .section {
        font-size: 15px;
        font-weight: bold;
        color: #2980b9;
        margin-top: 10px;
        margin-bottom: 4px;
    }
    .item {
        font-size: 13px;
        color: #34495e;
        margin-left: 6px;
        padding: 2px 0;
    }
    .example {
        font-size: 12px;
        color: #7f8c8d;
        margin-left: 12px;
        padding: 2px 0 4px 0;
    }
    .btn {
        font-size: 13px;
        color: #34495e;
        margin-left: 6px;
        padding: 2px 0;
    }
    .divider {
        border: none;
        border-top: 1px dashed #ecf0f1;
        margin: 8px 0;
    }
</style>
</head>
<body>
<div class="title">📖 使用说明</div>

<div class="section">⚙️ 配置参数</div>
<div class="item">1. 编号规则</div>
<div class="item" style="margin-left:12px;color:#555;">使用 {ids} 作为编号占位符</div>
<div class="example">示例：file_{ids} → file_1, file_2, ...</div>
<div class="item">2. 编号长度</div>
<div class="item" style="margin-left:12px;color:#555;">设置编号显示位数，不足补零</div>
<div class="example">示例：长度3 → 1 显示为 001</div>
<div class="example">设为 0 则是正常的1,2,3,4,5</div>

<hr class="divider">

<div class="section">🔘 操作按钮</div>
<div class="btn">💾 生成编号 - 根据配置批量生成（最多2000个）</div>
<div class="btn">📋 复制内容 - 复制所有编号到剪贴板</div>
<div class="btn">🧹 清空内容 - 清空预览区</div><br><br>
</body>
</html>
                """
        self.jc_label.setText(show_text)

        self.config_guize_lay = QHBoxLayout()
        self.cfg_gz_label = QLabel("编号规则:")
        self.cfg_gz_input = QLineEdit(placeholderText="file_{ids}")
        self.config_guize_lay.addWidget(self.cfg_gz_label)
        self.config_guize_lay.addWidget(self.cfg_gz_input)

        self.config_qiandao0_lay = QHBoxLayout()
        self.cfg_qd0_label = QLabel("编号长度:")
        self.cfg_qd0_input = QLineEdit(placeholderText="仅支持数字")
        validator = QIntValidator()
        self.cfg_qd0_input.setValidator(validator)
        self.config_qiandao0_lay.addWidget(self.cfg_qd0_label)
        self.config_qiandao0_lay.addWidget(self.cfg_qd0_input)

        self.config_id_lay = QHBoxLayout()
        self.cfg_id_label = QLabel("编号范围：")
        self.cfg_id_begin_input = QLineEdit(placeholderText="起始值")
        self.cfg_id_begin_input.setValidator(validator)
        self.cfg_id_label1 = QLabel("到")
        self.cfg_id_end_input = QLineEdit(placeholderText="结束值")
        self.cfg_id_end_input.setValidator(validator)
        self.config_id_lay.addWidget(self.cfg_id_label)
        self.config_id_lay.addWidget(self.cfg_id_begin_input)
        self.config_id_lay.addWidget(self.cfg_id_label1)
        self.config_id_lay.addWidget(self.cfg_id_end_input)

        self.begin_btn = QPushButton("💾 生成编号")
        self.begin_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")


        self.group_lay.addWidget(self.jc_label)
        self.group_lay.addLayout(self.config_guize_lay)
        self.group_lay.addLayout(self.config_qiandao0_lay)
        self.group_lay.addLayout(self.config_id_lay)
        self.group_lay.addWidget(self.begin_btn)

        self.group_lay.addStretch()
        self.group_lay.addWidget(self.status_label)
        self.groupbox.setLayout(self.group_lay)

        self.groupbox_yulan = QGroupBox()
        self.groupbox_yulan.setTitle("预览和结果")
        self.yulan_lay = QVBoxLayout()
        self.show_plain=QPlainTextEdit()
        self.yulan_btn_lay=QHBoxLayout()
        self.copy_btn=QPushButton("📋 复制内容")
        self.clear_btn=QPushButton("🧹 清空内容")

        self.yulan_btn_lay.addWidget(self.copy_btn)
        self.yulan_btn_lay.addWidget(self.clear_btn)
        self.yulan_lay.addWidget(self.show_plain)
        self.yulan_lay.addLayout(self.yulan_btn_lay)
        self.groupbox_yulan.setLayout(self.yulan_lay)
        self.layout.addWidget(self.groupbox)
        self.layout.addWidget(self.groupbox_yulan)
        self.setLayout(self.layout)

        self.cfg_gz_input.textChanged.connect(self.show_ids)
        self.cfg_qd0_input.textChanged.connect(self.show_ids)
        self.cfg_id_begin_input.textChanged.connect(self.show_ids)
        self.cfg_id_end_input.textChanged.connect(self.show_ids)
        self.show_ids()

        self.copy_btn.clicked.connect(self.copy_ids)
        self.clear_btn.clicked.connect(lambda :self.show_plain.clear())


    def show_ids(self):
        id_begin = self.cfg_id_begin_input.text()
        if id_begin == "":
            id_begin = 1
        id_begin = int(id_begin)

        id_end = self.cfg_id_end_input.text()
        if id_end == "":
            id_end = 10
        id_end = int(id_end) + 1

        if id_end-id_begin>50:
            id_begin=id_end-50

        guize=self.cfg_gz_input.text()
        if guize=="":
            guize="{ids}"

        qd0_num=self.cfg_qd0_input.text()
        if qd0_num=="":
            qd0_num=0
        qd0_num=int(qd0_num)
        self.show_plain.clear()


        for id in range(id_begin,id_end):
            if qd0_num>0:
                new_id=str(id).zfill(qd0_num)
            else:
                new_id=id
            new_ids=guize.replace("{ids}",str(new_id))
            self.show_plain.appendPlainText(new_ids)
            QApplication.processEvents()

    def begin_task(self):
        id_begin = self.cfg_id_begin_input.text()
        if id_begin == "":
            id_begin = 1
        id_begin = int(id_begin)

        id_end = self.cfg_id_end_input.text()
        if id_end == "":
            id_end = 10
        id_end = int(id_end) + 1

        if id_end-id_begin>2000:
            id_end=id_begin+2000
            self.status_label.setText("⚠️ 单次任务范围仅展示前2000")

        guize = self.cfg_gz_input.text()
        if guize == "":
            guize = "{ids}"

        qd0_num = self.cfg_qd0_input.text()
        if qd0_num == "":
            qd0_num = 0
        qd0_num = int(qd0_num)
        self.show_plain.clear()
        self.begin_btn.setDisabled(True)

        for id in range(id_begin, id_end):
            if qd0_num > 0:
                new_id = str(id).zfill(qd0_num)
            else:
                new_id = id
            new_ids = guize.replace("{ids}", str(new_id))
            self.show_plain.appendPlainText(new_ids)
            QApplication.processEvents()
        self.begin_btn.setDisabled(False)
        status_text=self.status_label.text()
        if status_text!="⚠️ 单次任务范围仅展示前2000":
            current_time = QDateTime.currentDateTime().toString("hh 时 mm 分 ss")

            # 显示带时间戳的完成信息
            self.status_label.setText(f"✅️ 任务完成  (完成于 {current_time})")


    def copy_ids(self):
        idss=self.show_plain.toPlainText()
        pyperclip.copy(idss)
        text = pyperclip.paste()
        if idss==text:
            msg_box = QMessageBox(parent=self)
            msg_box.setWindowTitle("提示")
            msg_box.setText("✅️ 复制成功！")
            msg_box.setStandardButtons(QMessageBox.Ok)  # 仍保留确定按钮

            # 2. 创建单次定时器，2秒后触发关闭
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(msg_box.close)  # 或 msg_box.accept()
            timer.start(2000)  # 2000毫秒 = 2秒

            # 3. 以模态方式显示消息框
            msg_box.exec()
