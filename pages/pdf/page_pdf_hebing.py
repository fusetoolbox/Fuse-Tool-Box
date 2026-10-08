from pathlib import Path

from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt

from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QFileDialog, QMessageBox)
import os
import pymupdf


class WorkChaiFen(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def run(self, get_data):
        folder_path = get_data["folder_path"]
        save_path = get_data["save_path"]

        directory = Path(folder_path).resolve()
        save_path = Path(save_path).resolve()
        pdf_files = sorted(
            p for p in directory.iterdir()
            if p.is_file() and p.suffix.lower() == ".pdf"
        )
        if not pdf_files:
            self.finished.emit("⚠️ 该目录下没有找到 PDF 文件。")
            return

        result = pymupdf.open()
        num_task = 1
        all_task = len(pdf_files)

        try:
            for path in pdf_files:
                # 打开源文件
                with pymupdf.open(path) as src:
                    # 将 src 的全部页面插入到 result 中
                    result.insert_pdf(src)
                self.progress.emit(f"⏳ {num_task}/{all_task}")
                num_task += 1
            # 保存结果
            out_path = os.path.join(save_path, "output.pdf")
            result.save(out_path)
        finally:
            result.close()
            self.finished.emit("✅️ 任务完成")


class Ui_page(QWidget):
    def __init__(self, /):
        super().__init__()

        self.layout = QHBoxLayout()
        self.groupbox = QGroupBox()
        self.groupbox.setTitle("配置参数")
        self.groupbox.setMaximumWidth(400)
        self.group_lay = QVBoxLayout()
        self.config_get_file_lay = QHBoxLayout()
        self.cfg_g_f_label = QLabel("文件位置:")
        self.cfg_g_f_input = QLineEdit()
        self.cfg_g_f_btn = QPushButton("📂 选择位置")
        self.cfg_g_f_btn.clicked.connect(self.open_g_f_path)

        self.config_get_file_lay.addWidget(self.cfg_g_f_label)
        self.config_get_file_lay.addWidget(self.cfg_g_f_input)
        self.config_get_file_lay.addWidget(self.cfg_g_f_btn)

        self.config_save_file_lay = QHBoxLayout()
        self.cfg_s_f_label = QLabel("存储位置:")
        self.cfg_s_f_input = QLineEdit()
        self.cfg_s_f_btn = QPushButton("📂 选择位置")
        self.cfg_s_f_btn.clicked.connect(self.open_s_f_path)

        self.config_save_file_lay.addWidget(self.cfg_s_f_label)
        self.config_save_file_lay.addWidget(self.cfg_s_f_input)
        self.config_save_file_lay.addWidget(self.cfg_s_f_btn)

        self.save_btn = QPushButton("💾 批量合并")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
        self.group_lay.addLayout(self.config_save_file_lay)
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
        <div class="title">📖 批量合并说明</div>

        <div class="highlight">🎯 一次把整个文件夹的 PDF 合成一份</div>

        <div class="section">🚀 三步搞定</div>
        <div class="item">1️⃣ 📂 选文件夹</div>
        <div class="example">文件夹里有多少 PDF，就自动并多少</div>
        <div class="item">2️⃣ 💾 选存储位置</div>
        <div class="example">合并后的文件就放在这里</div>
        <div class="item">3️⃣ 🔗 点合并</div>
        <div class="example">一键批量处理，无需逐个打开</div>

        <div class="section">📁 输出长这样</div>
        <div class="example">📂 待合并/（里面有 3 个 PDF）</div>
        <div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 报告.pdf</div>
        <div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 合同.pdf</div>
        <div class="example">&nbsp;&nbsp;&nbsp;└─ 📄 手册.pdf</div>
        <div class="example">👇 合并后，全部拼成一份</div>
        <div class="example">📂 合并结果/</div>
        <div class="example">&nbsp;&nbsp;&nbsp;└─ 📄 output.pdf</div>

        <div class="section">⚠️ 小提示</div>
        <div class="item">✅ 只认 .pdf，其他文件自动跳过</div>
        <div class="item">✅ 原文件不动，放心并</div>
        <div class="item">📑 按文件名排序，顺序即合并顺序</div>
        <div class="item">❗ 同名 output.pdf 会被覆盖</div><br><br>
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

    def open_s_f_path(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            QDir.homePath(),  # 默认打开用户主目录
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if folder_path:
            self.cfg_s_f_input.setText(folder_path)

    def begin_task(self):

        folder_path = self.cfg_g_f_input.text()

        if not os.path.isdir(folder_path):
            QMessageBox.warning(self, "警告", "读取PDF的文件夹路径无效")
            return

        save_path = self.cfg_s_f_input.text()

        if not os.path.isdir(save_path):
            QMessageBox.warning(self, "警告", "存储拆分后的PDF的文件夹路径无效")
            return


        datas = {
            "folder_path": folder_path,
            "save_path": save_path,
        }
        self.save_btn.setEnabled(False)

        self.thread_cf = QThread()
        self.work_cf = WorkChaiFen()

        self.work_cf.moveToThread(self.thread_cf)
        self.thread_cf.started.connect(lambda: self.work_cf.run(datas), Qt.DirectConnection)

        self.work_cf.progress.connect(self.status_update)
        self.work_cf.finished.connect(self.processor_finished)

        self.thread_cf.start()

    def status_update(self, show_text):
        self.status_label.setText(f"任务进行中：{show_text}")
        # QApplication.processEvents()

    def processor_finished(self, show_text):
        self.save_btn.setEnabled(True)
        self.status_label.setText(show_text)
        self.thread_cf.quit()
        self.thread_cf.wait()
        self.thread_cf.deleteLater()
        self.thread_cf.terminate()
