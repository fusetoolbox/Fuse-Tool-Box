from pathlib import Path

from rapidocr import RapidOCR
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
        output_method = get_data["output_method"]
        IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
        OUTPUT_ENCODING = 'utf-8'

        folder_path = Path(folder_path).resolve()
        save_path = Path(save_path).resolve()
        images = [
            f for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTS
        ]
        if not images:
            self.finished.emit(f"[提示] 目录 {folder_path} 中没有找到图片文件")
            return
        engine = RapidOCR()
        merged_lines = []

        all_task = len(images)
        for idx, now_image in enumerate(images, 1):
            try:
                result = engine(str(now_image))
                if result is None or result.txts is None or len(result.txts) == 0:
                    text = ""
                    self.progress.emit(f"{now_image.name}未识别到文字")
                else:
                    text = "\n".join(result.txts)
                    self.progress.emit(f"{now_image.name}识别到 {len(result.txts)} 行文字")

                if output_method==1:
                    out_file = save_path / f"{now_image.stem}.txt"
                    with open(out_file, 'w', encoding=OUTPUT_ENCODING) as f:
                        f.write(text)
                else:
                    merged_lines.append(f"===== {now_image.name} =====")
                    merged_lines.append(text if text else "(无文字)")
                    merged_lines.append("")  # 空行分隔

            except Exception as e:
                self.progress.emit(f"[失败] {now_image.name}: {e}")

            self.progress.emit(f"⏳ {idx}/{all_task} 当前文件：{now_image.name}")
        if output_method==0 and merged_lines:
            merged_file = save_path / "ocr_results.txt"
            with open(merged_file, 'w', encoding=OUTPUT_ENCODING) as f:
                f.write("\n".join(merged_lines))

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

        self.config_output_lay = QHBoxLayout()
        self.cfg_output_label = QLabel("输出方式：")
        self.cfg_output_label.setMinimumWidth(69)
        self.cfg_o_m_combox=QComboBox()
        self.cfg_o_m_combox.addItems(["单个文本文件","多个文本文件"])
        self.config_output_lay.addWidget(self.cfg_output_label)
        self.config_output_lay.addWidget(self.cfg_o_m_combox,1)

        self.config_save_file_lay = QHBoxLayout()
        self.cfg_s_f_label = QLabel("存储位置：")
        self.cfg_s_f_label.setMinimumWidth(69)
        self.cfg_s_f_input = QLineEdit()
        self.cfg_s_f_btn = QPushButton("📂 选择位置")
        self.cfg_s_f_btn.clicked.connect(self.open_s_f_path)

        self.config_save_file_lay.addWidget(self.cfg_s_f_label)
        self.config_save_file_lay.addWidget(self.cfg_s_f_input)
        self.config_save_file_lay.addWidget(self.cfg_s_f_btn)

        self.save_btn = QPushButton("💾 批量OCR")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
        self.group_lay.addLayout(self.config_output_lay)
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
        <div class="title">📖 批量缩放说明</div>

        <div class="highlight">🎯 一次处理整个文件夹里的所有图片</div>

        <div class="section">🚀 操作步骤</div>
        <div class="item">  选文件夹 → 填尺寸 → 选输出位置 → 点批量缩放</div>
        <div class="example">尺寸格式：宽 x 高，例如 800 x 600；DPI 选填</div>

        <div class="section">📁 输出结果</div>
        <div class="example">缩放后文件名加 _new 后缀，保持原格式，原文件不动</div>

        <div class="section">⚠️ 注意</div>
        <div class="item">• 不支持动图，GIF/WebP 动图只保留第一帧</div>
        <div class="item">• 非 .png 后缀的透明图会丢失透明背景</div>
        <div class="item">• 同名文件会被覆盖；请勿使用以 _new 结尾的图片</div>

        <div class="section">✅ 放心</div>
        <div class="item">• 保持原格式，PNG 还是 PNG</div>
        <div class="item">• 自动纠正手机照片方向</div>
        <div class="item">• 会生成新文件，原文件不动</div>
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

        output_method=self.cfg_o_m_combox.currentIndex()
        datas = {
            "folder_path": folder_path,
            "save_path": save_path,
            "output_method": output_method
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
