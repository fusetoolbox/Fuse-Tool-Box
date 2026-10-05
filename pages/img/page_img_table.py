from pathlib import Path
from img2table.ocr import RapidOCR
from img2table.document import Image

from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt, QDateTime

from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QFileDialog, QMessageBox,QComboBox)
import os


class WorkChaiFen(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def run(self, get_data):
        folder_path = get_data["folder_path"]
        save_path = get_data["save_path"]

        folder_path = Path(folder_path).resolve()
        save_path = Path(save_path).resolve()
        files = [
            f for f in folder_path.iterdir()
            if f.is_file()
        ]
        if not files:
            self.finished.emit(f"[提示] 目录 {folder_path} 中没有找到文件")
            return
        ocr = RapidOCR(params={"Rec.lang_type": "ch"})
        all_task = len(files)
        for idx, now_image in enumerate(files, 1):
            try:
                file_name=now_image.stem
                doc = Image(src=now_image, detect_rotation=True)
                doc.to_xlsx(dest=f"{save_path/file_name}.xlsx", ocr=ocr,implicit_rows=True,implicit_columns=True,min_confidence=1)

            except Exception as e:
                self.progress.emit(f"[失败] {now_image.name}: {e}")

            self.progress.emit(f"⏳ {idx}/{all_task} 当前文件：{now_image.name}")


        current_time = QDateTime.currentDateTime().toString("hh 时 mm 分 ss")
        self.finished.emit(f"✅️ 任务完成 (完成于 {current_time})")


class Ui_page(QWidget):
    def __init__(self, /):
        super().__init__()

        self.layout = QHBoxLayout()
        self.groupbox = QGroupBox()
        self.groupbox.setTitle("配置参数")
        self.groupbox.setMaximumWidth(400)
        self.group_lay = QVBoxLayout()
        self.config_get_file_lay = QHBoxLayout()
        self.cfg_g_f_label = QLabel("文件位置：")
        self.cfg_g_f_label.setMinimumWidth(69)
        self.cfg_g_f_input = QLineEdit()
        self.cfg_g_f_btn = QPushButton("📂 选择位置")
        self.cfg_g_f_btn.clicked.connect(self.open_g_f_path)

        self.config_get_file_lay.addWidget(self.cfg_g_f_label)
        self.config_get_file_lay.addWidget(self.cfg_g_f_input)
        self.config_get_file_lay.addWidget(self.cfg_g_f_btn)

        self.config_save_file_lay = QHBoxLayout()
        self.cfg_s_f_label = QLabel("存储位置：")
        self.cfg_s_f_label.setMinimumWidth(69)
        self.cfg_s_f_input = QLineEdit()
        self.cfg_s_f_btn = QPushButton("📂 选择位置")
        self.cfg_s_f_btn.clicked.connect(self.open_s_f_path)

        self.config_save_file_lay.addWidget(self.cfg_s_f_label)
        self.config_save_file_lay.addWidget(self.cfg_s_f_input)
        self.config_save_file_lay.addWidget(self.cfg_s_f_btn)

        self.save_btn = QPushButton("💾 批量转表格")
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
            .warn {
                font-size: 13px;
                color: #c0392b;
                margin-left: 6px;
                padding: 2px 0;
            }
        </style>
        </head>
        <body>
        <div class="title">📖 批量表格识别说明</div>

        <div class="highlight">🎯 一次处理整个文件夹里的所有图片，自动识别表格并导出 Excel</div>

        <div class="section">🚀 操作步骤</div>
        <div class="item">1. 选择图片文件夹（存放待识别的截图/照片）</div>
        <div class="item">2. 选择存储位置（存放生成的 Excel 文件）</div>
        <div class="item">3. 点击「💾 批量转表格」开始处理</div>

        <div class="section">📁 输出结果</div>
        <div class="example">每张图片生成一个同名 .xlsx，如 1.png → 1.xlsx</div>
        <div class="example">原图不动，只读取不修改</div>

        <div class="section">⚠️ 注意事项</div>
        <div class="warn">• 图片越清晰、越正对，识别效果越好</div>
        <div class="warn">• 首次运行会加载 OCR 模型，需要等几秒</div>
        <div class="warn">• 合并单元格、多级表头可能还原不完美，请人工核对</div>
        <div class="warn">• 深色背景、模糊、严重倾斜的图片识别率会下降</div>
        <div class="warn">• 保存文件夹里的同名 .xlsx 会被覆盖</div>
        
        <div class="section">🤖 效果不好怎么办</div>
        <div class="item">• 如果识别出来的表格为空、内容缺失或错乱</div>
        <div class="item">• 说明传统 OCR 在这张图上力不从心</div>
        <div class="highlight">👉 建议改用大模型识图（如通义千问、DeepSeek、文心一言）</div>
        <div class="example">大模型能理解复杂结构，但对密集数字仍需人工核对</div>

        <div class="section">✅ 放心</div>
        <div class="item">• 只读取图片，不修改原文件</div>
        <div class="item">• 状态栏实时显示处理进度</div>
        <div class="item">• 单个文件失败不会中断整个任务</div>
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
            QMessageBox.warning(self, "警告", "选择图片的文件夹路径无效")
            return

        save_path = self.cfg_s_f_input.text()

        if not os.path.isdir(save_path):
            QMessageBox.warning(self, "警告", "存储缩放后的图片文件夹路径无效")
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
        self.status_label.setText("⌛️ 环境准备中...")

    def status_update(self, show_text):
        self.status_label.setText(f"任务进行中：{show_text}")
        # QApplication.processEvents()

    def processor_finished(self, show_text):
        self.save_btn.setEnabled(True)
        self.status_label.setText(show_text)
        self.thread_cf.quit()
        self.thread_cf.wait()
        self.thread_cf.deleteLater()
