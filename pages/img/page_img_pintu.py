import os

from PIL import Image
from PySide6.QtCore import QDir, QByteArray, QBuffer, QIODevice, Qt, QDateTime
from PySide6.QtGui import QIntValidator, QColor, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLineEdit, QPushButton, \
    QMessageBox, QFileDialog, QColorDialog


class Ui_page(QWidget):
    def __init__(self, /):
        super().__init__()
        self.layout = QHBoxLayout()
        self.group_box_config = QGroupBox()
        self.group_box_config.setTitle("配置参数")
        self.group_box_config.setFixedWidth(400)
        self.group_box_config_lay=QVBoxLayout()

        self.config_img_orientation_lay=QHBoxLayout()
        self.cfg_img_orientation_label=QLabel("拼图方向：")
        self.cfg_img_orientation_combo=QComboBox()
        self.cfg_img_orientation_combo.addItems(["横向(水平)","纵向(垂直)"])
        self.config_img_orientation_lay.addWidget(self.cfg_img_orientation_label)
        self.config_img_orientation_lay.addWidget(self.cfg_img_orientation_combo,1)

        self.config_bg_color_lay = QHBoxLayout()
        self.cfg_bg_label = QLabel("背景颜色：")
        self.cfg_bg_input = QLineEdit()
        self.cfg_bg_input.setPlaceholderText("支持16进制和颜色单词")
        self.cfg_bg_btn = QPushButton("🎨 打开调色盘")
        self.cfg_bg_btn.clicked.connect(self.open_color_picker)

        self.config_bg_color_lay.addWidget(self.cfg_bg_label)
        self.config_bg_color_lay.addWidget(self.cfg_bg_input)
        self.config_bg_color_lay.addWidget(self.cfg_bg_btn)

        self.config_img_interval_lay = QHBoxLayout()
        self.cfg_i_i_label = QLabel("图片间距：")
        self.cfg_i_i_input = QLineEdit(placeholderText="请输入间距大小（仅支持数字）")
        validator = QIntValidator()
        self.cfg_i_i_input.setValidator(validator)
        self.config_img_interval_lay.addWidget(self.cfg_i_i_label)
        self.config_img_interval_lay.addWidget(self.cfg_i_i_input)

        self.config_img1_lay = QHBoxLayout()
        self.cfg_img1_label = QLabel("图一位置：")
        self.cfg_img1_input = QLineEdit()
        self.cfg_img1_input.setPlaceholderText("点击右侧按钮选择图片位置")
        self.cfg_img1_btn = QPushButton("📂 选择图一")
        self.cfg_img1_btn.clicked.connect(lambda :self.open_img_picker("img1"))
        self.config_img1_lay.addWidget(self.cfg_img1_label)
        self.config_img1_lay.addWidget(self.cfg_img1_input)
        self.config_img1_lay.addWidget(self.cfg_img1_btn)

        self.config_img2_lay = QHBoxLayout()
        self.cfg_img2_label = QLabel("图二位置：")
        self.cfg_img2_input = QLineEdit()
        self.cfg_img2_input.setPlaceholderText("点击右侧按钮选择图片位置")
        self.cfg_img2_btn = QPushButton("📂 选择图二")
        self.cfg_img2_btn.clicked.connect(lambda :self.open_img_picker("img2"))
        self.config_img2_lay.addWidget(self.cfg_img2_label)
        self.config_img2_lay.addWidget(self.cfg_img2_input)
        self.config_img2_lay.addWidget(self.cfg_img2_btn)

        self.config_save_lay = QHBoxLayout()
        self.cfg_save_label = QLabel("存储位置：")
        self.cfg_save_input = QLineEdit()
        self.cfg_save_input.setPlaceholderText("不会填则点击按钮获取")
        self.cfg_save_btn = QPushButton("📂 选择位置")
        self.cfg_save_btn.clicked.connect(self.open_save_picker)
        self.config_save_lay.addWidget(self.cfg_save_label)
        self.config_save_lay.addWidget(self.cfg_save_input)
        self.config_save_lay.addWidget(self.cfg_save_btn)

        self.save_btn=QPushButton("💾 保存拼图")
        self.save_btn.clicked.connect(self.save_img)

        self.status_label=QLabel("任务未开始")

        self.jc_label = QLabel()
        show_text = """
        <html>
            💡 拼图规则：<br>
            水平拼接 → 以最高图为准，顶部对齐<br>
            垂直拼接 → 以最宽图为准，左对齐<br>
            空白区域自动填充背景色<br>
            💾 设置完成后点击 "保存拼图" 即可<br><br><br><br>
        </html>
        """
        self.jc_label.setText(show_text)
        self.group_box_config_lay.addWidget(self.jc_label)

        self.group_box_config_lay.addLayout(self.config_img_orientation_lay)
        self.group_box_config_lay.addLayout(self.config_bg_color_lay)
        self.group_box_config_lay.addLayout(self.config_img_interval_lay)
        self.group_box_config_lay.addLayout(self.config_img1_lay)
        self.group_box_config_lay.addLayout(self.config_img2_lay)
        self.group_box_config_lay.addLayout(self.config_save_lay)
        self.group_box_config_lay.addWidget(self.save_btn)
        self.group_box_config_lay.addStretch()
        self.group_box_config_lay.addWidget(self.status_label)
        self.group_box_config.setLayout(self.group_box_config_lay)




        self.group_box_show=QGroupBox()
        self.group_box_show.setTitle("预览")
        self.img_layout = QHBoxLayout()
        self.show_label = QLabel()

        self.img_layout.addStretch()
        self.img_layout.addWidget(self.show_label)
        self.img_layout.addStretch()
        self.group_box_show.setLayout(self.img_layout)

        self.layout.addWidget(self.group_box_config)
        self.layout.addWidget(self.group_box_show)

        self.setLayout(self.layout)
        self.cfg_img_orientation_combo.currentTextChanged.connect(self.show_img)
        self.cfg_bg_input.textChanged.connect(self.show_img)
        self.cfg_i_i_input.textChanged.connect(self.show_img)
        self.cfg_img1_input.textChanged.connect(self.show_img)
        self.cfg_img2_input.textChanged.connect(self.show_img)

    def open_color_picker(self):
        init_color = self.cfg_bg_input.text()
        q_init_color = QColor(init_color)
        q_init_color_isValid = q_init_color.isValid()
        if q_init_color_isValid:
            color = QColorDialog.getColor(q_init_color, parent=self)
        else:
            color = QColorDialog.getColor(parent=self)
        if color.isValid():
            hex_color = color.name()
            self.cfg_bg_input.setText(hex_color)

    def create_img(self):
        img_orientation = self.cfg_img_orientation_combo.currentIndex()
        image1_path=self.cfg_img1_input.text()
        image2_path=self.cfg_img2_input.text()
        if image1_path=="" or image2_path=="":
            return
        bg_color=self.cfg_bg_input.text()
        if bg_color=="":
            bg_color="#000"
        set_color = QColor(bg_color)
        if not set_color.isValid():
            return

        img_interval=self.cfg_i_i_input.text()
        if img_interval=="":
            img_interval=0
        img_interval=int(img_interval)
        try:
            with Image.open(image1_path) as img1, Image.open(image2_path) as img2:
                if img_orientation == 0:
                    max_height = max(img1.height, img2.height)
                    new_img = Image.new('RGB', (img1.width + img2.width + img_interval, max_height),color=bg_color)
                    new_img.paste(img1, (0, 0))
                    new_img.paste(img2, (img1.width + img_interval, 0))
                else :
                    max_with = max(img1.width, img2.width)
                    new_img = Image.new('RGB', (max_with, img1.height + img2.height + img_interval), color=bg_color)
                    new_img.paste(img1, (0, 0))
                    new_img.paste(img2, (0,img1.height + img_interval))
                return new_img
        except:
            return

    def show_img(self):
        img = self.create_img()
        if img==None:
            return
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag(2))

        img.save(buffer, "JPEG")

        buffer.close()

        pixmap = QPixmap()
        pixmap.loadFromData(byte_array)
        scaled = pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.show_label.setPixmap(scaled)

    def save_img(self):
        save_path = self.cfg_save_input.text()
        if save_path == "":
            QMessageBox.warning(self, "警告", "未设置存储位置")
            return
        if not os.path.isdir(save_path):
            QMessageBox.warning(self, "警告", "文件夹路径无效")
            return
        img=self.create_img()
        img.save(save_path+"/output.jpg")
        current_time = QDateTime.currentDateTime().toString("hh 时 mm 分 ss")

        # 显示带时间戳的完成信息
        self.status_label.setText(f"✅️ 任务完成  (完成于 {current_time})")




    def open_img_picker(self,img_name):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择一张图片",
            QDir.homePath(),
        )
        if file_path:
            if img_name=="img1":
                self.cfg_img1_input.setText(file_path)
            if img_name=="img2":
                self.cfg_img2_input.setText(file_path)
    def open_save_picker(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            QDir.homePath(),  # 默认打开用户主目录
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder_path:
            self.cfg_save_input.setText(folder_path)