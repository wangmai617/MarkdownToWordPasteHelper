"""
Markdown转Word格式优化粘贴助手 V1.0 
基本框架
系统托盘图标和退出。
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    tray_icon = QSystemTrayIcon()
    tray_icon.setToolTip("Markdown转Word粘贴助手 V1.0")

    # 加载本地图标文件
    icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
    if os.path.exists(icon_path):
        tray_icon.setIcon(QIcon(icon_path))
    else:
        # 若找不到文件，回退到系统默认图标
        tray_icon.setIcon(QIcon.fromTheme("accessories-text-editor"))

    menu = QMenu()
    exit_action = QAction("退出", menu)
    exit_action.triggered.connect(lambda: (tray_icon.hide(), app.quit()))
    menu.addAction(exit_action)

    tray_icon.setContextMenu(menu)
    tray_icon.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()