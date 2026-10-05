from PIL import Image, ImageFont, ImageDraw
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt, QDir, QObject, Signal, QThread, QCoreApplication
from PySide6.QtGui import QColor, QIntValidator, QPixmap
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QGroupBox, QVBoxLayout, QLineEdit,
                               QPushButton, QColorDialog, QComboBox, QFileDialog, QPlainTextEdit,
                               QMessageBox, )
import os


class Worker(QObject):
    progress = Signal(str)
    finished = Signal(str)

    def run(self, get_data):
        num_task=1
        for i in range(get_data["id_begin"], get_data["id_end"]):

            plain_text_list = get_data["plain_text"].split("\n")
            img = Image.new("RGB", (get_data["width"], get_data["height"]), color=get_data["back_color"])
            draw = ImageDraw.Draw(img)
            img_font = ImageFont.truetype(get_data["font_family"], get_data["font_size"])
            left, top, right, bottom = draw.textbbox((0, 0), get_data["plain_text"], font=img_font)

            h = bottom + get_data["font_jiange"] * (len(plain_text_list) - 1)
            first_y = ((img.height - h) / 2) - top

            for line_text in range(len(plain_text_list)):
                now_line = plain_text_list[line_text]
                now_line = now_line.replace("{i}", str(i))
                left, top, right, bottom = draw.textbbox((0, 0), now_line, font=img_font)
                line_width, line_height = right - left, bottom
                x = (img.width - line_width) / 2
                y = first_y + (line_text * line_height) + (line_text * get_data["font_jiange"])
                draw.text((x, y), now_line, font=img_font, fill=get_data["font_color"])
            img.save(get_data["save_path"] + f"/{i}.jpg")

            self.progress.emit(f"{num_task}/{get_data['all_num']}")
            num_task+=1
        self.finished.emit("over")


class Ui_page(QWidget):
    def __init__(self, /):
        super().__init__()

        self.layout = QHBoxLayout()
        self.group_box = QGroupBox()
        self.group_box.setTitle("配置图片参数")
        self.group_box.setFixedWidth(400)
        self.config_lay = QVBoxLayout()

        self.config_back_lay = QHBoxLayout()
        self.cfg_back_label = QLabel("背景颜色：")
        self.cfg_back_input = QLineEdit()
        self.cfg_back_input.setPlaceholderText("支持16进制和颜色单词")
        self.cfg_back_btn = QPushButton("🎨 打开调色盘")
        self.cfg_back_btn.clicked.connect(self.open_color_picker)
        self.config_back_lay.addWidget(self.cfg_back_label)
        self.config_back_lay.addWidget(self.cfg_back_input)
        self.config_back_lay.addWidget(self.cfg_back_btn)

        self.config_size_lay = QHBoxLayout()
        self.cfg_size_label = QLabel("图片尺寸：")
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

        self.config_font_family_lay = QHBoxLayout()
        self.cfg_f_f_label = QLabel("字体风格：")
        self.cfg_f_f_combo = QComboBox()
        self.cfg_f_f_combo.setMaxVisibleItems(10)

        self.cfg_f_f_combo.setStyleSheet("""
            QComboBox {
                combobox-popup: 0;
            }
        """)
        self.config_font_family_lay.addWidget(self.cfg_f_f_label)
        self.config_font_family_lay.addWidget(self.cfg_f_f_combo, 1)

        self.config_font_size_lay = QHBoxLayout()
        self.cfg_f_s_label = QLabel("字体大小：")
        self.cfg_f_s_input = QLineEdit(placeholderText="请输入字体大小（仅支持数字）")
        self.cfg_f_s_input.setValidator(validator)
        self.config_font_size_lay.addWidget(self.cfg_f_s_label)
        self.config_font_size_lay.addWidget(self.cfg_f_s_input)

        self.config_font_color_lay = QHBoxLayout()
        self.cfg_f_c_label = QLabel("字体颜色：")
        self.cfg_f_c_input = QLineEdit()
        self.cfg_f_c_input.setPlaceholderText("支持16进制和颜色单词")

        self.cfg_f_c_btn = QPushButton("🎨 打开调色盘")
        self.cfg_f_c_btn.clicked.connect(self.open_color_picker_f_c)

        self.config_font_color_lay.addWidget(self.cfg_f_c_label)
        self.config_font_color_lay.addWidget(self.cfg_f_c_input)
        self.config_font_color_lay.addWidget(self.cfg_f_c_btn)

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

        self.config_font_interval_lay = QHBoxLayout()
        self.cfg_f_i_label = QLabel("每行间距：")
        self.cfg_f_i_input = QLineEdit(placeholderText="请输入间距大小（仅支持数字）")
        self.cfg_f_i_input.setValidator(validator)
        self.config_font_interval_lay.addWidget(self.cfg_f_i_label)
        self.config_font_interval_lay.addWidget(self.cfg_f_i_input)

        self.config_save_lay = QHBoxLayout()
        self.cfg_save_label = QLabel("存储位置：")
        self.cfg_save_input = QLineEdit()
        self.cfg_save_input.setPlaceholderText("不会填则点击按钮获取")
        self.cfg_save_btn = QPushButton("📂 选择位置")
        self.cfg_save_btn.clicked.connect(self.open_save_picker)
        self.config_save_lay.addWidget(self.cfg_save_label)
        self.config_save_lay.addWidget(self.cfg_save_input)
        self.config_save_lay.addWidget(self.cfg_save_btn)

        self.text_label = QLabel("编辑文字：")
        self.text_plain_edit = QPlainTextEdit("我是文字内容\n请使用 {i} 代替编号")

        self.save_btn = QPushButton("💾 批量生成")
        self.save_btn.clicked.connect(self.save_img)

        self.status_label = QLabel("任务未开始")

        self.config_lay.addLayout(self.config_back_lay)
        self.config_lay.addLayout(self.config_size_lay)
        self.config_lay.addLayout(self.config_font_family_lay)
        self.config_lay.addLayout(self.config_font_size_lay)
        self.config_lay.addLayout(self.config_font_color_lay)
        self.config_lay.addLayout(self.config_id_lay)
        self.config_lay.addLayout(self.config_font_interval_lay)
        self.config_lay.addLayout(self.config_save_lay)
        self.config_lay.addWidget(self.text_label)
        self.config_lay.addWidget(self.text_plain_edit)
        self.config_lay.addWidget(self.save_btn)

        self.config_lay.addStretch()
        self.config_lay.addWidget(self.status_label)
        self.group_box.setLayout(self.config_lay)

        self.img_box = QGroupBox()
        self.img_box.setTitle("预览")
        self.img_layout = QHBoxLayout()
        self.show_label = QLabel()

        self.img_layout.addStretch()
        self.img_layout.addWidget(self.show_label)
        self.img_layout.addStretch()
        self.img_box.setLayout(self.img_layout)

        self.layout.addWidget(self.group_box)
        self.layout.addWidget(self.img_box)
        self.setLayout(self.layout)

        self.cfg_f_f_add_item()
        self.show_img()
        self.cfg_back_input.textChanged.connect(self.show_img)
        self.cfg_size_w_input.textChanged.connect(self.show_img)
        self.cfg_size_h_input.textChanged.connect(self.show_img)
        self.cfg_f_f_combo.currentTextChanged.connect(self.show_img)
        self.cfg_f_s_input.textChanged.connect(self.show_img)
        self.cfg_f_c_input.textChanged.connect(self.show_img)
        self.cfg_f_i_input.textChanged.connect(self.show_img)
        self.text_plain_edit.textChanged.connect(self.show_img)

    def open_color_picker(self):
        init_color = self.cfg_back_input.text()
        q_init_color = QColor(init_color)
        q_init_color_isValid = q_init_color.isValid()
        if q_init_color_isValid:
            color = QColorDialog.getColor(q_init_color, parent=self)
        else:
            color = QColorDialog.getColor(parent=self)
        if color.isValid():
            hex_color = color.name()
            self.cfg_back_input.setText(hex_color)

    def open_color_picker_f_c(self):
        init_color = self.cfg_f_c_input.text()
        q_init_color = QColor(init_color)
        q_init_color_isValid = q_init_color.isValid()
        if q_init_color_isValid:
            color = QColorDialog.getColor(q_init_color, parent=self)
        else:
            color = QColorDialog.getColor(parent=self)
        if color.isValid():
            hex_color = color.name()
            self.cfg_f_c_input.setText(hex_color)

    def open_save_picker(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            QDir.homePath(),  # 默认打开用户主目录
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder_path:
            self.cfg_save_input.setText(folder_path)

    def cfg_f_f_add_item(self):
        path = "C:\Windows\Fonts"
        all_font_family = []
        files = os.listdir(path)
        for file in files:
            if file.endswith(".ttc") or file.endswith(".ttf"):
                all_font_family.append(file)

        self.cfg_f_f_combo.addItems(all_font_family)
        if "msyh.ttc" in all_font_family:
            self.cfg_f_f_combo.setCurrentText("msyh.ttc")

    def show_img(self):
        img = self.create_img(1)
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag(2))

        img.save(buffer, "JPEG")

        buffer.close()

        pixmap = QPixmap()
        pixmap.loadFromData(byte_array)
        scaled = pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.show_label.setPixmap(scaled)

    def get_info(self):
        back_color = self.cfg_back_input.text()
        if back_color == "":
            back_color = "#000000"
        set_color = QColor(back_color)
        if not set_color.isValid():
            return {"msg": "error"}
        width = self.cfg_size_w_input.text()
        height = self.cfg_size_h_input.text()
        if width == "":
            width = 512
        if height == "":
            height = 512
        width = int(width)
        height = int(height)
        font_family = self.cfg_f_f_combo.currentText()
        if font_family == "":
            font_family = "arial.ttf"
        font_size = self.cfg_f_s_input.text()
        if font_size == "":
            font_size = 30
        font_size = int(font_size)
        font_color = self.cfg_f_c_input.text()
        if font_color == "":
            font_color = "#ffffff"
        set_color = QColor(font_color)
        if not set_color.isValid():
            return {"msg": "error"}
        font_jiange = self.cfg_f_i_input.text()
        if font_jiange == "":
            font_jiange = 20
        font_jiange = int(font_jiange)

        plain_text = self.text_plain_edit.toPlainText()

        datas = {
            "back_color": back_color,
            "width": width,
            "height": height,
            "font_family": font_family,
            "font_size": font_size,
            "font_color": font_color,
            "font_jiange": font_jiange,
            "plain_text": plain_text,
            "msg": "success"
        }
        return datas

    def create_img(self, bianhao):
        get_data = self.get_info()

        plain_text_list = get_data["plain_text"].split("\n")

        img = Image.new("RGB", (get_data["width"], get_data["height"]), color=get_data["back_color"])
        draw = ImageDraw.Draw(img)
        img_font = ImageFont.truetype(get_data["font_family"], get_data["font_size"])
        left, top, right, bottom = draw.textbbox((0, 0), get_data["plain_text"], font=img_font)

        h = bottom + get_data["font_jiange"] * (len(plain_text_list) - 1)
        first_y = ((img.height - h) / 2) - top

        for line_text in range(len(plain_text_list)):
            now_line = plain_text_list[line_text]
            now_line = now_line.replace("{i}", str(bianhao))
            left, top, right, bottom = draw.textbbox((0, 0), now_line, font=img_font)
            line_width, line_height = right - left, bottom
            x = (img.width - line_width) / 2
            y = first_y + (line_text * line_height) + (line_text * get_data["font_jiange"])
            draw.text((x, y), now_line, font=img_font, fill=get_data["font_color"])

        return img

    def save_img(self):

        id_begin = self.cfg_id_begin_input.text()
        if id_begin == "":
            id_begin = 1
        id_begin = int(id_begin)

        id_end = self.cfg_id_end_input.text()
        if id_end == "":
            id_end = 10
        id_end = int(id_end) + 1

        all_num = id_end - id_begin

        save_path = self.cfg_save_input.text()
        if save_path == "":
            QMessageBox.warning(self, "警告", "未设置存储位置")
            return
        if not os.path.isdir(save_path):
            QMessageBox.warning(self, "警告", "文件夹路径无效")
            return

        datas = self.get_info()
        datas["id_begin"] = id_begin
        datas["id_end"] = id_end
        datas["save_path"] = save_path
        datas["all_num"] = all_num

        self.thread = QThread()
        self.processor = Worker()
        self.processor.moveToThread(self.thread)
        self.thread.started.connect(lambda: self.processor.run(datas), Qt.DirectConnection)

        self.processor.progress.connect(self.status_update)
        self.processor.finished.connect(self.processor_finished)

        self.thread.start()

    def status_update(self, show_text):
        self.status_label.setText(f"任务进行中：{show_text}")
        # QApplication.processEvents()

    def processor_finished(self):
        self.status_label.setText(f"✅️ 任务完成")
        self.thread.terminate()
