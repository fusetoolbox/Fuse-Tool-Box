from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QPlainTextEdit, QFileDialog, QMessageBox)
import os

class WorkChuangJian(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def run(self, get_data):
        folder_path = get_data["folder_path"]
        name_list = get_data["tianchong_text"].split("\n")
        num_task = 1
        all_task = len(name_list)
        for file_name in name_list:
            if file_name == "":
                continue
            try:
                os.makedirs(os.path.join(folder_path, file_name), exist_ok=True)
            except Exception as e:
                print(f"创建失败: {file_name}, {e}")
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
        self.cfg_g_f_label = QLabel("存放文件夹:")
        self.cfg_g_f_input = QLineEdit()
        self.cfg_g_f_btn = QPushButton("📂 选择位置")
        self.cfg_g_f_btn.clicked.connect(self.open_g_f_path)

        self.config_get_file_lay.addWidget(self.cfg_g_f_label)
        self.config_get_file_lay.addWidget(self.cfg_g_f_input)
        self.config_get_file_lay.addWidget(self.cfg_g_f_btn)

        self.text_label = QLabel("设置文件夹名字：")
        self.text_plain_edit = QPlainTextEdit("1\n2\n3")

        self.save_btn = QPushButton("💾 批量创建")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
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
                        font-size: 24px;
                        font-weight: bold;
                        color: #2c3e50;
                        text-align: center;
                        padding-bottom: 8px;
                        border-bottom: 2px solid #3498db;
                        margin-bottom: 10px;
                    }
                    .section {
                        font-size: 18px;
                        font-weight: bold;
                        color: #2980b9;
                        margin-top: 16px;
                        margin-bottom: 6px;
                    }
                    .item {
                        font-size: 16px;
                        color: #34495e;
                        margin-left: 6px;
                        padding: 2px 0;
                    }
                    .example {
                        font-size: 15px;
                        color: #7f8c8d;
                        margin-left: 12px;
                        padding: 2px 0 4px 0;
                    }
                    .highlight {
                        font-size: 16px;
                        color: #e67e22;
                        font-weight: bold;
                        margin-left: 6px;
                        padding: 2px 0;
                    }
                </style>
                </head>
                <body>
                <div class="title">📂 批量创建文件夹说明</div>

                <div class="highlight">🎯 一次在指定位置创建多个文件夹</div>

                <div class="section">🚀 四步搞定</div>
                <div class="item">1. 📂 选存放位置</div>
                <div class="example">点击按钮，选择新文件夹要创建在哪个目录下</div>
                <div class="item">2. 📝 设置文件夹名字</div>
                <div class="example">在文本框中填写文件夹名，每行一个</div>
                <div class="example">示例：项目A / 项目B / 项目C</div>
                <div class="item">3. 💾 点批量创建</div>
                <div class="example">点击"批量创建"执行操作</div>
                <div class="item">4. ✅ 查看结果</div>
                <div class="example">底部状态栏会显示创建进度和完成提示</div>

                <div class="section">💡 说明</div>
                <div class="item">✅ 每行一个名字，空行会自动跳过</div>
                <div class="item">✅ 文件夹已存在时不会报错，直接跳过</div>
                <div class="item">✅ 支持多层路径，如：项目A/图片 会创建嵌套目录</div>
                <div class="item">❗ 名字中请勿包含 \\  : * ? " &lt; &gt; | 等系统非法字符</div><br><br>
                </body>
                </html>"""
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

        tianchong_text = self.text_plain_edit.toPlainText()


        datas = {
            "folder_path": folder_path,
            "tianchong_text": tianchong_text

        }
        self.save_btn.setEnabled(False)

        self.thread_gm = QThread()
        self.work_cj = WorkChuangJian()

        self.work_cj.moveToThread(self.thread_gm)
        self.thread_gm.started.connect(lambda: self.work_cj.run(datas), Qt.DirectConnection)

        self.work_cj.progress.connect(self.status_update)
        self.work_cj.finished.connect(self.processor_finished)

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
