"""
系统托盘控制器（初始框架）
目前仅包含托盘图标和基础菜单，后续功能将逐步添加。

作者：上海外国语大学/王迈
"""

import os
from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction, QWidget,
                             QMessageBox, QApplication)
from PyQt5.QtGui import QIcon


class TrayController(QWidget):
    """托盘控制器基础版，只有图标和两个菜单项"""

    def __init__(self):
        super().__init__()
        # ---------- 创建托盘图标 ----------
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Markdown转Word粘贴助手 V0.1")

        # 加载图标
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("accessories-text-editor"))

        # 搭建菜单
        self.create_tray_menu()

        # 托盘激活事件暂不处理
        self.tray_icon.activated.connect(lambda reason: None)

        # 隐藏无用窗口
        self.hide()

    def create_tray_menu(self):
        """组装托盘右键菜单，目前只有关于和退出"""
        menu = QMenu()

        # 关于
        action_about = QAction("关于(&A)", self)
        action_about.triggered.connect(self.show_about)
        menu.addAction(action_about)

        # 退出
        action_exit = QAction("退出(&X)", self)
        action_exit.triggered.connect(self.exit_app)
        menu.addAction(action_exit)

        self.tray_icon.setContextMenu(menu)

    def show_about(self):
        """显示关于信息"""
        about_text = (
            "<h2>Markdown转Word格式优化粘贴助手</h2>"
            "<p>版本：V0.1（初始框架）</p>"
            "<p>功能正在开发中，当前仅提供系统托盘基础支持。</p>"
            "<p>开发者：王迈 (上海外国语大学)</p>"
            "<p>邮箱：wangmai@shisu.edu.cn</p>"
        )
        QMessageBox.about(None, "关于", about_text)

    def exit_app(self):
        """退出程序"""
        self.tray_icon.hide()
        QApplication.quit()

    def show(self):
        """显示托盘图标"""
        self.tray_icon.show()