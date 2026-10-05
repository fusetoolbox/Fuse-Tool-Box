from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QPlainTextEdit, QFileDialog, QMessageBox)
import os
from natsort import natsorted


class WorkGaiMing(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def run(self, get_data):
        folder_path = get_data["folder_path"]

        items = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        items = natsorted(items)
        name_list = get_data["tianchong_text"].split("\n")
        num_task = 1
        all_task = len(items)
        for file_name in items:
            if len(name_list) == 0:
                break
            now_name = name_list[0]
            if now_name == "":
                del name_list[0]
                continue
            new_name = get_data["change_guize"]
            houzhui = file_name.split(".")[-1]
            new_name = new_name.replace("{name}", now_name)
            old_path = os.path.join(folder_path, file_name)
            new_path = os.path.join(folder_path, new_name + "." + houzhui)
            os.rename(old_path, new_path)
            del name_list[0]
            self.progress.emit(f"⏳ {num_task}/{all_task}")
            num_task += 1
        self.finished.emit("")


class Ui_page(QWidget):
    def __init__(self, /):
        super().__init__()

        self.layout = QHBoxLayout()
        self.groupbox = QGroupBox()
        self.groupbox.setTitle("配置参数")
        self.groupbox.setMaximumWidth(400)
        self.group_lay = QVBoxLayout()
        self.config_get_file_lay = QHBoxLayout()
        self.cfg_g_f_label = QLabel("待改名文件夹:")
        self.cfg_g_f_input = QLineEdit()
        self.cfg_g_f_btn = QPushButton("📂 选择位置")
        self.cfg_g_f_btn.clicked.connect(self.open_g_f_path)

        self.config_get_file_lay.addWidget(self.cfg_g_f_label)
        self.config_get_file_lay.addWidget(self.cfg_g_f_input)
        self.config_get_file_lay.addWidget(self.cfg_g_f_btn)

        self.config_guize_lay = QHBoxLayout()
        self.cfg_gz_label = QLabel("设置改名规则:")
        self.cfg_gz_input = QLineEdit(placeholderText="new_{name}")

        self.config_guize_lay.addWidget(self.cfg_gz_label)
        self.config_guize_lay.addWidget(self.cfg_gz_input)

        self.text_label = QLabel("设置填充内容：")
        self.text_plain_edit = QPlainTextEdit("1\n2\n3")

        self.save_btn = QPushButton("💾 批量改名")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
        self.group_lay.addLayout(self.config_guize_lay)
        self.group_lay.addWidget(self.text_label)
        self.group_lay.addWidget(self.text_plain_edit)
        self.group_lay.addWidget(self.save_btn)

        self.group_lay.addStretch()
        self.group_lay.addWidget(self.status_label)
        self.groupbox.setLayout(self.group_lay)

        self.groupbox_jiaocheng = QGroupBox()
        self.groupbox_jiaocheng.setTitle("教程")
        self.jiaocheng_lay = QVBoxLayout()
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
                margin-top: 16px;
                margin-bottom: 6px;
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
            .highlight {
                font-size: 13px;
                color: #e67e22;
                font-weight: bold;
                margin-left: 6px;
                padding: 2px 0;
            }
        </style>
        </head>
        <body>
        <div class="title">📖 批量改名说明</div>

        <div class="highlight">🎯 一次处理整个文件夹里的所有文件</div>

        <div class="section">🚀 四步搞定</div>
        <div class="item">1️⃣ 📂 选文件夹</div>
        <div class="example">点击按钮，选择存放待改名文件的文件夹</div>
        <div class="item">2️⃣ ✏️ 设置改名规则</div>
        <div class="example">规则中 {name} 会被替换为填充内容</div>
        <div class="example">示例：new_{name} → new_1、new_2…</div>
        <div class="item">3️⃣ 📝 填填充内容</div>
        <div class="example">在文本框中填写名称，每行一个</div>
        <div class="example">张三 / 李四 / 王五</div>
        <div class="item">4️⃣ 💾 点改名</div>
        <div class="example">点击"批量改名"执行操作</div>

        <div class="section">💡 规则说明</div>
        <div class="item">✅ 不改后缀名（.jpg、.txt 保留不变）</div>
        <div class="item">✅ 按文件名自然排序（1、2、3… 或 a、b、c…）</div>
        <div class="item">❗ 填充内容中请勿包含 {name}</div><br><br>
        </body>
        </html>
                        """
        self.jc_label.setText(show_text)
        self.jiaocheng_lay.addWidget(self.jc_label)
        self.jiaocheng_lay.addStretch()

        self.groupbox_jiaocheng.setLayout(self.jiaocheng_lay)

        self.layout.addWidget(self.groupbox)
        self.layout.addWidget(self.groupbox_jiaocheng)
        self.setLayout(self.layout)

    def open_g_f_path(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            QDir.homePath(),  # 默认打开用户主目录
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if folder_path:
            self.cfg_g_f_input.setText(folder_path)

    def begin_task(self):

        folder_path = self.cfg_g_f_input.text()

        if not os.path.isdir(folder_path):
            QMessageBox.warning(self, "警告", "文件夹路径无效")
            return
        change_guize = self.cfg_gz_input.text()
        if change_guize == "":
            change_guize = "new_{name}"

        tianchong_text = self.text_plain_edit.toPlainText()
        if "{name}" in tianchong_text:
            QMessageBox.warning(self, "警告", "请勿在填充内容中填写{name}")
            return

        datas = {
            "folder_path": folder_path,
            "change_guize": change_guize,
            "tianchong_text": tianchong_text

        }
        self.save_btn.setEnabled(False)

        self.thread_gm = QThread()
        self.work_gm = WorkGaiMing()

        self.work_gm.moveToThread(self.thread_gm)
        self.thread_gm.started.connect(lambda: self.work_gm.run(datas), Qt.DirectConnection)

        self.work_gm.progress.connect(self.status_update)
        self.work_gm.finished.connect(self.processor_finished)

        self.thread_gm.start()

    def status_update(self, show_text):
        self.status_label.setText(f"任务进行中：{show_text}")
        # QApplication.processEvents()

    def processor_finished(self):
        self.save_btn.setEnabled(True)
        self.status_label.setText(f"✅️ 任务完成")
        self.thread_gm.quit()
        self.thread_gm.wait()
        self.thread_gm.deleteLater()
