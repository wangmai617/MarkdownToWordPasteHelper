"""
软件名称：Markdown转Word格式优化粘贴助手
版本号：V0.1（初始框架）
作者：上海外国语大学/王迈
项目来源：上海外国语大学重大攻关项目（中国语言文学国际传播平台建设与研究）

软件功能简介：工作学习中，经常需要从各种AI助手复制Markdown格式的内容粘贴到Word或WPS，
Markdown符号成为干扰源，格式常显混乱，手动删除又费时费力。
本程序将逐步完善，当前仅提供系统托盘基础框架。
"""

import sys
import os
import ctypes

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from tray_controller import TrayController


# ---------- 单实例检测 -------
MUTEX_NAME = "Global\\MarkdownWordPasteHelper_SingleInstance_Mutex"

def check_single_instance():
    """检查是否已有实例在运行"""
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if kernel32.GetLastError() == 183:
        if handle:
            kernel32.CloseHandle(handle)
        return False
    return True


def main():
    if not check_single_instance():
        ctypes.windll.user32.MessageBoxW(
            0,
            "Markdown转Word粘贴助手已经在运行中，请查看系统托盘图标。",
            "提示",
            0x40
        )
        sys.exit(0)

    # 高分屏适配
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 创建托盘控制器
    tray = TrayController()
    tray.show()

    # 简单启动提示
    from PyQt5.QtWidgets import QMessageBox
    QMessageBox.information(None, "提示", "程序已启动，常驻系统托盘。")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()