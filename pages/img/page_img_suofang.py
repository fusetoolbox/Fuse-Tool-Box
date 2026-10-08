from pathlib import Path

from PIL import Image, ImageOps
from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QFileDialog, QMessageBox)
import os


class WorkChaiFen(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def run(self, get_data):
        folder_path = get_data["folder_path"]
        save_path = get_data["save_path"]
        width = get_data["width"]
        height = get_data["height"]
        dpi_x=get_data["dpi_x"]
        dpi_y=get_data["dpi_y"]

        folder_path = Path(folder_path).resolve()
        save_path = Path(save_path).resolve()
        filepaths = [p for p in folder_path.iterdir() if p.is_file()]

        num_task = 1
        all_task = len(filepaths)
        for file_name in filepaths:

            try:
                with Image.open(file_name) as img:
                    img = ImageOps.exif_transpose(img)
                    new_img = img.resize((width, height), Image.LANCZOS)
                    ext = os.path.splitext(file_name)[1].lower()
                    save_kwargs = {}
                    if ext in (".jpg", ".jpeg"):
                        # JPEG 不支持透明通道，转 RGB
                        if new_img.mode in ("RGBA", "LA", "P"):
                            new_img = new_img.convert("RGB")
                            save_kwargs["quality"] = 95
                            save_kwargs["optimize"] = True
                    output_path = save_path / (file_name.stem + "_new" + ext)
                    if dpi_x>0 and dpi_y>0:
                        new_img.save(output_path,dpi=(dpi_x,dpi_y))
                    else:
                        new_img.save(output_path)

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
        self.cfg_g_f_label = QLabel("文件位置：")
        self.cfg_g_f_label.setMinimumWidth(69)
        self.cfg_g_f_input = QLineEdit()
        self.cfg_g_f_btn = QPushButton("📂 选择位置")
        self.cfg_g_f_btn.clicked.connect(self.open_g_f_path)

        self.config_get_file_lay.addWidget(self.cfg_g_f_label)
        self.config_get_file_lay.addWidget(self.cfg_g_f_input)
        self.config_get_file_lay.addWidget(self.cfg_g_f_btn)

        self.config_size_lay = QHBoxLayout()
        self.cfg_size_label = QLabel("图片尺寸：")
        self.cfg_size_label.setMinimumWidth(69)
        self.cfg_size_w_input = QLineEdit(placeholderText="宽")
        validator = QIntValidator()
        self.cfg_size_w_input.setValidator(validator)
        self.cfg_size_label1 = QLabel("x")
        self.cfg_size_h_input = QLineEdit(placeholderText="高")
        self.cfg_size_h_input.setValidator(validator)
        self.config_size_lay.addWidget(self.cfg_size_label)
        self.config_size_lay.addWidget(self.cfg_size_w_input)
        self.config_size_lay.addWidget(self.cfg_size_label1)
        self.config_size_lay.addWidget(self.cfg_size_h_input)

        self.config_dpi_lay = QHBoxLayout()
        self.cfg_dpi_label = QLabel("图片DPI：")
        self.cfg_dpi_label.setMinimumWidth(69)
        self.cfg_dpi_w_input = QLineEdit(placeholderText="x")
        validator = QIntValidator()
        self.cfg_dpi_w_input.setValidator(validator)
        self.cfg_dpi_label1 = QLabel("x")
        self.cfg_dpi_h_input = QLineEdit(placeholderText="y")
        self.cfg_dpi_h_input.setValidator(validator)
        self.config_dpi_lay.addWidget(self.cfg_dpi_label)
        self.config_dpi_lay.addWidget(self.cfg_dpi_w_input)
        self.config_dpi_lay.addWidget(self.cfg_dpi_label1)
        self.config_dpi_lay.addWidget(self.cfg_dpi_h_input)

        self.config_save_file_lay = QHBoxLayout()
        self.cfg_s_f_label = QLabel("存储位置：")
        self.cfg_s_f_label.setMinimumWidth(69)
        self.cfg_s_f_input = QLineEdit()
        self.cfg_s_f_btn = QPushButton("📂 选择位置")
        self.cfg_s_f_btn.clicked.connect(self.open_s_f_path)

        self.config_save_file_lay.addWidget(self.cfg_s_f_label)
        self.config_save_file_lay.addWidget(self.cfg_s_f_input)
        self.config_save_file_lay.addWidget(self.cfg_s_f_btn)

        self.save_btn = QPushButton("💾 批量缩放")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
        self.group_lay.addLayout(self.config_size_lay)
        self.group_lay.addLayout(self.config_dpi_lay)
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
        width = self.cfg_size_w_input.text()
        width = width.strip()
        if width == "":
            QMessageBox.warning(self, "警告", "宽度设置不可为空")
            return
        if not width.isnumeric():
            QMessageBox.warning(self, "警告", "宽度设置格式错误")
            return
        width = int(width)

        height = self.cfg_size_h_input.text()
        height = height.strip()
        if height == "":
            QMessageBox.warning(self, "警告", "高度设置不可为空")
            return
        if not height.isnumeric():
            QMessageBox.warning(self, "警告", "高度设置格式错误")
            return
        height = int(height)

        dpi_x = self.cfg_dpi_w_input.text()
        dpi_x = dpi_x.strip()
        if dpi_x == "":
            dpi_x = "0"
        if not dpi_x.isnumeric():
            QMessageBox.warning(self, "警告", "水平DPI设置格式错误")
            return
        dpi_x = int(dpi_x)

        dpi_y = self.cfg_dpi_h_input.text()
        dpi_y = dpi_y.strip()
        if dpi_y == "":
            dpi_y = "0"
        if not dpi_y.isnumeric():
            QMessageBox.warning(self, "警告", "垂直DPI设置格式错误")
            return
        dpi_y = int(dpi_y)

        datas = {
            "folder_path": folder_path,
            "save_path": save_path,
            "width": width,
            "height": height,
            "dpi_x": dpi_x,
            "dpi_y": dpi_y,
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
