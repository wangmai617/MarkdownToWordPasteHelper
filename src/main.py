"""
软件名称：Markdown转Word格式优化粘贴助手
版本号：V1.0
作者：上海外国语大学/王迈
项目来源：上海外国语大学重大攻关项目（中国语言文学国际传播平建设与研究）

软件功能简介：工作学习中，经常需要从各种AI助手复制Markdown格式的内容粘贴到Word或WPS，
Markdown符号成为干扰源，格式常显混乱，手动删除又费时费力。
本程序可将Markdown格式的内容转换为Word/WPS兼容的HTML格式，并保留原文基本格式。
可快捷键一键转换粘贴，轻量、离线、常驻系统托盘，不用时无打扰，不收集个人信息。
"""

import sys
import os
import ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer

# 将软件功能分写为如下模块：
from tray_controller import TrayController      #系统托盘图标和右键菜单
# clipboard_monitor 模块已移除
from hotkey_manager import HotkeyManager        #注册全局快捷键Ctrl+Shift+V
from settings_manager import SettingsManager    #读写配置文件，保存用户设置
from markdown_converter import MarkdownConverter  #核心转换逻辑，Markdown到HTML

# import math  #以前好像用过，留着备用


# ---------- 单实例检测 -------
# 使用一个全局互斥体来保证只运行一个实例，避免托盘区出现多个图标
MUTEX_NAME = "Global\\MarkdownWordPasteHelper_SingleInstance_Mutex"

def check_single_instance():
    """检查是否已有实例在运行。返回True表示这是第一个实例，False则表示已有实例"""
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    # 如果实例已经存在，GetLastError返回183(ERROR_ALREADY_EXISTS)
    if kernel32.GetLastError()==183:
        if handle:
            kernel32.CloseHandle(handle)
        return False
    # 互斥体创建成功，当前进程成为第一个实例，退出时会自动释放
    return True


def main():
    """
    程序入口，完成以下操作：
    0.检查是否已有实例运行
    1.初始化Qt应用
    2.创建各个功能模块
    3.注册快捷键
    4.打开系统托盘图标
    5.弹出启动提示对话框
    6.进入事件循环
    """
    # 单实例检查
    if check_single_instance() == False:
        # 使用Windows原生消息框提示
        ctypes.windll.user32.MessageBoxW(
            0,
            "Markdown转Word粘贴助手已经在运行中，请查看系统托盘图标。",
            "提示",
            0x40  # MB_ICONINFORMATION
        )
        sys.exit(0)

    # 高分屏适配，高分辨率的屏幕，无此两行界面会糊
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    # 注意：关闭主窗口（实则无主窗口）时不退出程序，只退到托盘
    app.setQuitOnLastWindowClosed(False)

    # ---- 创建各模块实例
    # 配置管理：用户保存的快捷键、开机启动等设置
    settings = SettingsManager()
    # 核心转换器：把Markdown转成Word能识别的HTML
    converter = MarkdownConverter()

    # 托盘控制器：包含了整个托盘菜单和交互逻辑
    tray = TrayController(settings, converter)

    # 快捷键管理器：注册Ctrl+Shift+V，键入执行转换+粘贴
    hotkey = HotkeyManager(settings, tray, converter)  # 不再需要 monitor
    hotkey.register_hotkey()  # 注册到系统，当被其他软件占用，则提示失败。

    # 把快捷键的引用传给托盘，方便在设置里修改热键。
    tray.set_hotkey(hotkey)

    # 开机自启选项写入注册表，这里先做出判断
    if settings.get_auto_start():
        tray.set_auto_start(True)

    # 显示系统托盘图标
    tray.show()

    # 弹出启动提示对话框，告知用户程序已就绪并显示当前快捷键
    hotkey_str = f"{hotkey.modifiers_to_string()} + {chr(hotkey.vk_code)}"
    QMessageBox.information(
        None,  # 父窗口为空，对话框居中显示
        "提示",
        f"程序已启动，常驻系统托盘。\n请复制Markdown文本，然后使用快捷键{hotkey_str}转换并粘贴文本。"
    )

    # 预留一个后台定时器，将来需要定时任务时可使用
    timer = QTimer()
    timer.start(1000)  # 每秒触发一次，预留。
    # timer.timeout.connect(lambda: None)  # 将来可以接心跳检测之类

    # 进入Qt主循环，程序持续运行
    sys.exit(app.exec_())


# 标准的Python入口
if __name__ == "__main__":
    main()