import random
import sys
import time

from PySide6.QtCore import QTimer, QEasingCurve
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QTreeWidgetItem
from Ui_main import Ui_Form
from qt_material import apply_stylesheet

from menus import menus
import importlib

with open("yulu.txt", "r", encoding="utf-8") as f:
    res = f.read()
yulu_list = res.split("\n")


class MyWindow(Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Fuse工具箱")
        self.setWindowIcon(QIcon("logo.png"))
        self.version_label.setText("v1.0.4")
        self.stackedWidget.setCurrentIndex(0)
        self.SOFTWARE_CREATED_AT = 1787229900
        self.treeWidget.itemClicked.connect(self.item_click)
        self.loaded_page = []
        self.init_menu()
        self.select_daily_quote()
        self.setup_timer()
        self.set_birth_and_tool_num()

    def init_menu(self):

        for menu in menus:
            menu_name = menu.get("menu_name", "")
            if menu_name != "":
                item = QTreeWidgetItem([menu_name])
                self.treeWidget.addTopLevelItem(item)
                child = menu.get("child", [])
                if child != []:
                    for child_menu in child:
                        child_menu_name = child_menu.get("tool_name", "")
                        if child_menu_name != "":
                            child_tiem = QTreeWidgetItem([child_menu_name])
                            item.addChild(child_tiem)

    def item_click(self, item):
        if item.parent() is None:
            item.setExpanded(not item.isExpanded())
        else:
            child_menu_name = item.data(0, 0)
            for menu in menus:
                menu_name = menu.get("menu_name", "")
                if menu_name == "":
                    return
                child = menu.get("child", [])
                if child == []:
                    return
                for child_menu in child:
                    tool_name = child_menu.get("tool_name", "")
                    if tool_name == "":
                        return

                    if child_menu_name == tool_name:

                        page_id = child_menu.get("page_id", "")
                        if page_id == "":
                            return
                        cateary = page_id.split("_")[1]
                        module_name = f"pages.{cateary}.{page_id}"
                        module = importlib.import_module(module_name)
                        ui_class = getattr(module, "Ui_page")
                        new_page = ui_class()
                        new_page.setObjectName(page_id)
                        if page_id in self.loaded_page:
                            page_index = self.loaded_page.index(page_id)
                            self.stackedWidget.setCurrentIndex(page_index + 1)
                        else:
                            self.stackedWidget.addWidget(new_page)
                            self.loaded_page.append(page_id)
                            self.stackedWidget.setCurrentWidget(new_page)

    def select_daily_quote(self):
        quote = random.choice(yulu_list)
        self.quote_label.setText(f"「{quote}」")

    def setup_timer(self):
        """定时刷新语录（每30秒更换）"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.select_daily_quote)
        self.timer.start(30000)


    def set_birth_and_tool_num(self):
        now_time=time.time()

        age=now_time-self.SOFTWARE_CREATED_AT
        days=int(age/86400)
        tool_num=0
        for menu in menus:
            child=menu.get("child",[])
            len_child=len(child)
            tool_num+=len_child
        self.count_label.setText(f"📦 已服务 {days} 天 · 共有 {tool_num} 个工具")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    apply_stylesheet(app, theme='light_blue_500.xml')

    sys.exit(app.exec())
