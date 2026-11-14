import re
from pathlib import Path

from PySide6.QtCore import QDir, QThread, QObject, Signal, Qt

from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox,
                               QPushButton, QLineEdit, QFileDialog, QMessageBox, QPlainTextEdit)


class WorkChaiFen(QObject):
    finished = Signal(str)
    progress = Signal(str)

    def normalize_header(self, h):
        """表头标准化：全角转半角、去空格、去常见括号/冒号、统一小写"""
        if h is None:
            return ""
        s = str(h)
        # 全角转半角
        s = "".join(chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in s)
        s = s.replace("\u3000", " ")  # 全角空格
        s = re.sub(r"[\s\(\)\[\]（）【】:：]", "", s)  # 去空格和常见括号/冒号
        return s.strip().lower()

    # ========== 2. 读取辅助 ==========
    def list_sheets(self, path):
        from openpyxl import load_workbook
        """列出工作簿中所有工作表名"""
        wb = load_workbook(path, read_only=True)
        names = wb.sheetnames
        wb.close()
        return names

    def read_table(self, path, sheet_name, header_row=0):
        import pandas as pd
        """读取一个 Sheet 为 DataFrame，表头行可配置，列名标准化"""
        df = pd.read_excel(path, sheet_name=sheet_name, header=header_row, dtype=object)
        df.columns = [self.normalize_header(c) for c in df.columns]
        return df

    # ========== 3. 列名汇总与映射 ==========
    def collect_headers(self, tables):
        """tables: list of (source_label, df)，汇总所有标准化列名（保持首次出现顺序）"""
        all_cols = []
        for _, df in tables:
            for c in df.columns:
                if c and c not in all_cols:
                    all_cols.append(c)
        return all_cols

    def build_mapping(self, all_cols, user_mapping=None):
        """
        返回 {标准化列名: 目标列名} 的映射。
        默认恒等映射；user_mapping 用于同义词覆盖，如 {"客户id": "客户编号"}
        """
        mapping = {c: c for c in all_cols}
        if user_mapping:
            mapping.update(user_mapping)
        return mapping

    # ========== 4. 合并 ==========
    def merge_tables(self, tables, mapping, add_source=True):
        import pandas as pd
        """
        tables: list of (source_label, df)
        mapping: {源标准化列名: 目标列名}
        纵向拼接，缺失列留空，同义词合并后去重列
        """
        frames = []
        for label, df in tables:
            # 按映射重命名列
            df = df.rename(columns={c: mapping.get(c, c) for c in df.columns})
            # 同义词合并后可能出现重复列名，保留第一个
            df = df.loc[:, ~df.columns.duplicated()]
            if add_source:
                df["来源"] = label
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True, sort=False)

    # ========== 5. 主入口 ==========
    def merge_excel_files(self, paths, out_path, header_row=0, user_mapping=None):
        import os
        """
        合并多个 Excel 文件（含各自所有 Sheet）到一张总表。
        paths: 文件路径列表
        out_path: 输出 xlsx 路径
        header_row: 表头所在行（0 表示第一行）
        user_mapping: 同义词映射，如 {"客户id": "客户编号"}
        """
        tables = []
        for p in paths:
            for sh in self.list_sheets(p):
                df = self.read_table(p, sh, header_row=header_row)
                if df.empty and len(df.columns) == 0:
                    continue
                label = f"{os.path.basename(p)}::{sh}"
                tables.append((label, df))

        all_cols = self.collect_headers(tables)
        mapping = self.build_mapping(all_cols, user_mapping)
        result = self.merge_tables(tables, mapping, add_source=True)

        result.to_excel(out_path, index=False)

    def run(self, get_data):
        from natsort import natsorted
        folder_path = get_data["folder_path"]
        save_path = get_data["save_path"]
        hebing_map = get_data["hebing"]

        get_directory = Path(folder_path).resolve()
        save_directory = Path(save_path).resolve()
        output_path = save_directory / "output.xlsx"
        xlsx_files = natsorted(
            p for p in get_directory.iterdir()
            if p.is_file() and p.suffix.lower() == ".xlsx"
            and p.resolve() != output_path.resolve()
        )
        if not xlsx_files:
            self.finished.emit("⚠️ 该目录下没有找到 xlsx 文件。")
            return
        try:
            if not hebing_map:
                self.merge_excel_files(xlsx_files, output_path)
            else:
                self.merge_excel_files(xlsx_files, output_path, user_mapping=hebing_map)
        except:
            self.finished.emit("❌️ 未知错误，联系开发者")
            return
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

        self.text_label = QLabel("同义列名合并（可选）：")
        self.text_plain_edit = QPlainTextEdit(
            placeholderText="每行一组，格式：别名=统一列名\n例如：\n联系电话=电话\n客户id=客户编号")

        self.save_btn = QPushButton("💾 批量合并")
        self.save_btn.clicked.connect(self.begin_task)
        self.status_label = QLabel("任务未开始")

        self.group_lay.addLayout(self.config_get_file_lay)
        self.group_lay.addLayout(self.config_save_file_lay)
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
<div class="title">📖 批量合并说明</div>

<div class="highlight">🎯 一次把整个文件夹的 Excel 合成一份</div>

<div class="section">🚀 三步搞定</div>
<div class="item">📂 选文件夹</div>
<div class="example">文件夹里有多少 Excel，就自动并多少</div>
<div class="item">💾 选存储位置</div>
<div class="example">合并后的文件就放在这里</div>
<div class="item">🔗 点合并</div>
<div class="example">一键批量处理，无需逐个打开</div>

<div class="section">📁 输出长这样</div>
<div class="example">📂 待合并/（里面有 3 个 Excel）</div>
<div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 一月.xlsx</div>
<div class="example">&nbsp;&nbsp;&nbsp;├─ 📄 二月.xlsx</div>
<div class="example">&nbsp;&nbsp;&nbsp;└─ 📄 三月.xlsx</div>
<div class="example">👇 合并后，全部拼成一份</div>
<div class="example">📂 合并结果/</div>
<div class="example">&nbsp;&nbsp;&nbsp;└─ 📄 output.xlsx</div>

<div class="section">🔗 同义列名（可选）</div>
<div class="item">✅ 不同表里叫法不同、意思相同的列，可以在这里统一</div>
<div class="example">每行一组，格式：别名=统一列名</div>
<div class="example">例如：联系电话=电话，客户id=客户编号</div>
<div class="item">✅ 不填则按列名完全一致对齐</div>

<div class="section">⚠️ 小提示</div>
<div class="item">✅ 只认 .xlsx，其他文件自动跳过</div>
<div class="item">✅ 原文件不动，放心并</div>
<div class="item">📑 按文件名排序，顺序即合并顺序</div>
<div class="item">❗ 原始文件夹中不要有output.xlsx </div><br><br>
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
        import os
        self.work_cf = WorkChaiFen()  # 因为需要借用一下标准化代码 所以把代码往上提
        folder_path = self.cfg_g_f_input.text()

        if not os.path.isdir(folder_path):
            QMessageBox.warning(self, "警告", "读取表格的文件夹路径无效")
            return

        save_path = self.cfg_s_f_input.text()

        if not os.path.isdir(save_path):
            QMessageBox.warning(self, "警告", "存储合并后表格的文件夹路径无效")
            return
        tongyihebing_text = self.text_plain_edit.toPlainText()
        mapping = {}
        try:
            for line in tongyihebing_text.splitlines():
                line = line.strip()
                if not line:
                    continue

                # 按第一个 = : ： 分割，最多切一刀
                parts = re.split(r"[=:：]", line, maxsplit=1)
                if len(parts) != 2:
                    continue  # 没有分隔符，跳过

                key = self.work_cf.normalize_header(parts[0].strip())

                value = parts[1].strip()
                if not key or not value:
                    continue

                mapping[key] = value
        except:
            QMessageBox.warning(self, "警告", "设置的同义列名合并出错")
            return

        datas = {
            "folder_path": folder_path,
            "save_path": save_path,
            "hebing": mapping
        }
        self.save_btn.setEnabled(False)

        self.thread_cf = QThread()

        self.work_cf.moveToThread(self.thread_cf)
        self.thread_cf.started.connect(lambda: self.work_cf.run(datas), Qt.DirectConnection)

        self.work_cf.progress.connect(self.status_update)
        self.work_cf.finished.connect(self.processor_finished)

        self.thread_cf.start()
        self.status_label.setText("⏳ 环境准备中")

    def status_update(self, show_text):
        self.status_label.setText(f"任务进行中：{show_text}")
        # QApplication.processEvents()

    def processor_finished(self, show_text):
        self.save_btn.setEnabled(True)
        self.status_label.setText(show_text)
        self.thread_cf.quit()
        self.thread_cf.wait()
        self.thread_cf.deleteLater()
