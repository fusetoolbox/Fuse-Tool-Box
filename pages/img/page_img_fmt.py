from pathlib import Path

from PIL import Image
from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt, QDateTime
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QFileDialog, QMessageBox,QComboBox)
import os

class WorkChaiFen(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def _prepare_mode(self,img, target_format):
        """根据目标格式调整图像模式，避免保存报错。"""
        # 不支持透明的格式：去掉 Alpha
        if target_format in ("JPEG", "BMP"):
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            elif img.mode not in ("RGB", "L"):
                img = img.convert("RGB")

        # ICO 需要 RGBA 才能保留透明
        elif target_format == "ICO":
            if img.mode != "RGBA":
                img = img.convert("RGBA")

        # PNG 保留透明，但 P 模式带透明时转 RGBA 更稳
        elif target_format == "PNG":
            if img.mode == "P":
                img = img.convert("RGBA")

        return img

    def save_ico(self,img, dst_path):
        """保存为多尺寸 ICO，并保证是正方形。"""
        ico_sizes = [16, 32, 48, 64, 128, 256]

        # ICO 最佳实践：先变成正方形，短边补透明
        max_dim = max(img.size)
        if img.size[0] != img.size[1]:
            square = Image.new("RGBA", (max_dim, max_dim), (0, 0, 0, 0))
            offset = ((max_dim - img.size[0]) // 2, (max_dim - img.size[1]) // 2)
            square.paste(img, offset)
            img = square

        # Pillow 的 ICO 保存要求 sizes 是 (w, h) 元组列表
        sizes = [(s, s) for s in ico_sizes if s <= max_dim]
        img.save(f"{dst_path}.ico", format="ICO", sizes=sizes, bitmap_format="bmp")

    def run(self, get_data):
        folder_path = get_data["folder_path"]
        save_path = get_data["save_path"]
        fmt_id = get_data["fmt_id"]

        if fmt_id==0:
            target_fmt="JPG"
        elif fmt_id==1:
            target_fmt="PNG"
        elif fmt_id==2:
            target_fmt="WEBP"
        elif fmt_id==3:
            target_fmt="BMP"
        else:
            target_fmt="ICO"

        folder_path = Path(folder_path).resolve()
        save_dir_path = Path(save_path).resolve()
        files = [
            f for f in folder_path.iterdir()
            if f.is_file()
        ]
        if not files:
            self.finished.emit(f"[提示] 目录 {folder_path} 中没有找到文件")
            return

        all_task = len(files)
        for idx, now_image in enumerate(files, 1):
            file_name=now_image.stem
            file_save_path=save_dir_path/f"{file_name}_new"
            try:
                with Image.open(now_image) as img:
                    img = self._prepare_mode(img, target_fmt)
                    if target_fmt == "ICO":
                        self.save_ico(img, file_save_path)
                    elif target_fmt == "JPG":
                        img.save(f"{file_save_path}.jpg", format="JPEG", quality=95, optimize=True)
                    elif target_fmt == "WEBP":
                        img.save(f"{file_save_path}.webp", format="WEBP", quality=95)
                    elif target_fmt == "PNG":
                        img.save(f"{file_save_path}.png", format="PNG")
                    elif target_fmt == "BMP":
                        img.save(f"{file_save_path}.bmp", format="BMP")
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

        self.config_fmt_lay = QHBoxLayout()
        self.cfg_fmt_label = QLabel("目标格式：")
        self.cfg_fmt_label.setMinimumWidth(69)
        self.cfg_fmt_combox=QComboBox()
        self.cfg_fmt_combox.addItems(["JPG","PNG","WEBP","BMP","ICO"])
        self.config_fmt_lay.addWidget(self.cfg_fmt_label)
        self.config_fmt_lay.addWidget(self.cfg_fmt_combox,1)

        self.config_save_file_lay = QHBoxLayout()
        self.cfg_s_f_label = QLabel("存储位置：")
        self.cfg_s_f_label.setMinimumWidth(69)
        self.cfg_s_f_input = QLineEdit()
        self.cfg_s_f_btn = QPushButton("📂 选择位置")
        self.cfg_s_f_btn.clicked.connect(self.open_s_f_path)

        self.config_save_file_lay.addWidget(self.cfg_s_f_label)
        self.config_save_file_lay.addWidget(self.cfg_s_f_input)
        self.config_save_file_lay.addWidget(self.cfg_s_f_btn)

        self.save_btn = QPushButton("💾 批量转格式")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
        self.group_lay.addLayout(self.config_fmt_lay)
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
                <div class="title">📖 批量转格式说明</div>

                <div class="highlight">🎯 一次处理整个文件夹里的所有图片</div>

                <div class="section">🚀 操作步骤</div>
                <div class="item">  选文件夹 → 选目标格式 → 选输出位置 → 点批量转格式</div>
                <div class="example">支持格式：JPG、PNG、WEBP、BMP、ICO</div>

                <div class="section">📁 输出结果</div>
                <div class="example">转换后文件名加 _new 后缀，原文件不动</div>

                <div class="section">⚠️ 注意</div>
                <div class="item">• 不支持动图，GIF/WebP 动图只保留第一帧</div>
                <div class="item">• 转 JPG/BMP 时透明背景会丢失</div>
                <div class="item">• 同名文件会被覆盖；请勿使用以 _new 结尾的图片</div>
                <div class="item">• 转ICO时，图片尺寸请大于16*16</div>

                <div class="section">✅ 放心</div>
                <div class="item">• 会生成新文件，原文件不动</div>
                <div class="item">• ICO 自动生成多尺寸（16~256）</div>
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

        fmt_id=self.cfg_fmt_combox.currentIndex()
        datas = {
            "folder_path": folder_path,
            "save_path": save_path,
            "fmt_id": fmt_id
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
