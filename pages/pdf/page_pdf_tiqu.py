from pathlib import Path

from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt

from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QPlainTextEdit, QFileDialog, QMessageBox)
import os
import pymupdf


class WorkChaiFen(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def tiqu_pdf_by_pages(self,input_path, save_path, pages):

        src = pymupdf.open(input_path)
        total = src.page_count
        stem = Path(input_path).stem

        valid = [i for i in pages if 0 <= i < total]

        if not valid:
            src.close()
            return
        new_doc = pymupdf.open()
        numss=1
        for start in valid:
            self.progress.emit(f"[完成]  {numss} 个页面")
            # insert_pdf 的 from_page/to_page 就是从哪一页到哪一页
            new_doc.insert_pdf(src, from_page=start, to_page=start)

        out_name = f"{stem}_new.pdf"
        out_path = os.path.join(save_path, out_name)
        new_doc.save(out_path)
        new_doc.close()

        src.close()


    def run(self, get_data):
        folder_path = get_data["folder_path"]
        save_path = get_data["save_path"]
        page_num = get_data["page_num"]

        directory = Path(folder_path).resolve()
        save_path = Path(save_path).resolve()


        # 只取 .pdf，忽略其他文件；大小写不敏感
        pdf_files = sorted(
            p for p in directory.iterdir()
            if p.is_file() and p.suffix.lower() == ".pdf"
        )
        if not pdf_files:
            self.finished.emit("⚠️ 该目录下没有找到 PDF 文件。")
            return

        pages = set()
        for part in page_num.replace("，", ",").split(","):
            part = part.strip()
            if not part:
                continue

            if not part.isdigit():
                self.finished.emit(f"⚠️ 页码格式错误：{part}")
                return
            n = int(part)
            if n < 1:
                self.finished.emit(f"⚠️ 页码必须 ≥ 1：{n}")
                return

            pages.add(n - 1)  # 转 0-based
        if not pages:
            self.finished.emit(f"⚠️ 没有有效的页码")
            return

        num_task = 1
        all_task = len(pdf_files)
        for file_name in pdf_files:
            try:
                self.tiqu_pdf_by_pages(
                    str(file_name), str(save_path), pages
                )

            except Exception as e:
                self.progress.emit(f"[失败] {file_name.name}: {e}")

            self.progress.emit(f"⏳ {num_task}/{all_task}")
            num_task += 1
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

        self.config_guize_lay = QHBoxLayout()
        self.cfg_gz_label = QLabel("提取页码")
        self.cfg_gz_input = QPlainTextEdit(placeholderText="页码之间用逗号隔开，例如：1,5,7,15")
        self.config_guize_lay.addWidget(self.cfg_gz_label)
        self.config_guize_lay.addWidget(self.cfg_gz_input)

        self.config_save_file_lay = QHBoxLayout()
        self.cfg_s_f_label = QLabel("存储位置:")
        self.cfg_s_f_input = QLineEdit()
        self.cfg_s_f_btn = QPushButton("📂 选择位置")
        self.cfg_s_f_btn.clicked.connect(self.open_s_f_path)

        self.config_save_file_lay.addWidget(self.cfg_s_f_label)
        self.config_save_file_lay.addWidget(self.cfg_s_f_input)
        self.config_save_file_lay.addWidget(self.cfg_s_f_btn)

        self.save_btn = QPushButton("💾 批量提取")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
        self.group_lay.addLayout(self.config_guize_lay)
        self.group_lay.addLayout(self.config_save_file_lay)
        self.group_lay.addWidget(self.save_btn)
        self.group_lay.addStretch()
        self.group_lay.addWidget(self.status_label)
        self.groupbox.setLayout(self.group_lay)

        self.groupbox_jiaocheng = QGroupBox()
        self.groupbox_jiaocheng.setTitle("教程")
        self.jiaocheng_lay = QVBoxLayout()
        self.jc_label = QLabel()
        show_text = """<html>
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
                <div class="title">📖 按页码提取说明</div>

                <div class="highlight">🎯 从整个文件夹的 PDF 里，抽出你想要的页</div>

                <div class="section">🚀 三步搞定</div>
                <div class="item">1️⃣ 📂 选文件夹</div>
                <div class="example">文件夹里有多少 PDF，就自动提取多少</div>
                <div class="item">2️⃣ 🔢 填页码</div>
                <div class="example">想要哪几页？逗号隔开，例如：1,5,7,15</div>
                <div class="item">3️⃣ ✂️ 点提取</div>
                <div class="example">一键批量处理，无需逐个操作</div>

                <div class="section">📁 输出长这样</div>
                <div class="example">📂 待提取/（里面有 3 个 PDF）</div>
                <div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 报告.pdf</div>
                <div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 合同.pdf</div>
                <div class="example">&nbsp;&nbsp;&nbsp;└─ 📄 手册.pdf</div>
                <div class="example">👇 提取后，每个都生成一份新 PDF</div>
                <div class="example">📂 提取结果/</div>
                <div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 报告_new.pdf</div>
                <div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 合同_new.pdf</div>
                <div class="example">&nbsp;&nbsp;&nbsp;└─ 📄 手册_new.pdf</div>

                <div class="section">⚠️ 小提示</div>
                <div class="item">✅ 页码从 1 开始数，和阅读器一致</div>
                <div class="item">✅ 支持中文逗号，1，3，5 也认</div>
                <div class="item">✅ 原文件不动，放心提取</div>
                <div class="item">❗ 超出总页数的页码会被自动忽略</div><br><br>
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
        page_num = self.cfg_gz_input.toPlainText()
        if page_num == "":
            QMessageBox.warning(self, "警告", "未设置提取的页码")
            return

        datas = {
            "folder_path": folder_path,
            "save_path": save_path,
            "page_num": page_num,
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
