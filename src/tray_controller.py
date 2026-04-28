"""
系统托盘控制器及主界面逻辑
包含了托盘图标、右键菜单等。
由于无主界面，此模块即为用户交互界面。
2.0版可以加入主界面，并增加其他功能。

作者：上海外国语大学/王迈
"""

import os
import sys
from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QCheckBox, QLineEdit, QTextEdit, QDialog,
                             QMessageBox, QApplication, QComboBox)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QTimer
# PreviewDialog 已随 ui_dialogs 移除


class TrayController(QWidget):
    """继承了QWidget，但不显示，只用来挂托盘图标"""

    def __init__(self, settings, converter):
        super().__init__()
        self.settings = settings          # 保存用户设置对象
        self.converter = converter        # Markdown转换器

        # ---------- 创建托盘图标 ----
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Markdown转Word粘贴助手 V1.0")

        # 加载图标，如找不到则启用系统默认
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            #  默认图标
            self.tray_icon.setIcon(QIcon.fromTheme("accessories-text-editor"))

        # 搭建菜单
        self.create_tray_menu()

        # 双击托盘图标（暂时无操作）
        # self.tray_icon.activated.connect(self.on_tray_activated)
        # 留个连接以备后用
        self.tray_icon.activated.connect(lambda reason: None)

        # 此窗口无用，隐藏起来
        self.hide()

    def create_tray_menu(self):
        """组装托盘右键菜单，顺序符合一般习惯"""
        menu = QMenu()

        # 手动转换粘贴，仅写入剪贴板，用户需自行Ctrl+V
        action_convert = QAction("转换并粘贴(&P)", self)
        action_convert.triggered.connect(self.manual_convert_paste)
        menu.addAction(action_convert)

        # 清空剪切板
        action_clear = QAction("清空剪贴板(&C)", self)
        action_clear.triggered.connect(self.clear_clipboard)
        menu.addAction(action_clear)

        menu.addSeparator()

        # 打开设置（暂未开放）
        action_settings = QAction("设置(&S)", self)
        action_settings.triggered.connect(self.open_settings)
        menu.addAction(action_settings)

        menu.addSeparator()

        # 关于窗口，显示基本信息
        action_about = QAction("关于(&A)", self)
        action_about.triggered.connect(self.show_about)
        menu.addAction(action_about)

        # 退出
        action_exit = QAction("退出(&X)", self)
        action_exit.triggered.connect(self.exit_app)
        menu.addAction(action_exit)

        self.tray_icon.setContextMenu(menu)

    # 双击响应暂时停用
    # def on_tray_activated(self, reason):
    #     """处理托盘图标的激活事件，目前只响应双击（打开预览）"""
    #     if reason == QSystemTrayIcon.DoubleClick:
    #         self.preview_markdown()

    def manual_convert_paste(self):
        """用户通过菜单点击"转换并粘贴"时调用，仅转换写入剪贴板，不模拟Ctrl+V"""
        success, preview = self.converter.convert_and_copy_to_clipboard()
        if success:
            if self.settings.get_show_tips():
                self.show_message("转换成功", "已转换为Word格式并写入剪贴板，请手动粘贴")
        else:
            self.show_message("转换失败", preview)

    # 预览方法已移除
    # def preview_markdown(self):
    #     """弹出预览窗口，查看当前剪贴板Markdown内容及转换后样式"""
    #     ...

    def clear_clipboard(self):
        """清空剪贴板，避免隐私泄漏"""
        self.converter.clear_clipboard()
        self.show_message("操作完成", "剪贴板已清空")

    def open_settings(self):
        """设置功能暂未开放"""
        QMessageBox.information(None, "提示", "设置功能暂未开放，敬请期待。")

    def show_about(self):
        """弹出关于对话框，显示作者、版本等信息"""
        about_text = (
            "<h2>Markdown转Word格式优化粘贴助手 V1.0</h2>"
            "<p>本软件将Markdown格式转换为Word格式，并保留基本排版信息。</p>"
            "<p>本地离线运行，无须联网，不收集任何数据。</p>"
            '<p>"上海外国语大学中国语言文学国际传播平台建设与研究项目"使用</p>'
            "<p>开发者：王迈 (上海外国语大学)</p>"
            "<p>邮箱：wangmai@shisu.edu.cn</p>"
            "<hr>"
            "<p>使用方法：复制Markdown文本，右键托盘图标选择\"转换并粘贴\"，然后在Word中Ctrl+V粘贴。</p>"
        )
        QMessageBox.about(None, "关于", about_text)

    def exit_app(self):
        """完全退出程序：隐藏图标，退出Qt循环"""
        self.tray_icon.hide()
        QApplication.quit()

    def show(self):
        """显示托盘图标，在程序启动时调用"""
        self.tray_icon.show()

    def show_message(self, title, message, duration=2000):
        """在托盘区弹出气泡提示"""
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, duration)

    def set_auto_start(self, enable):
        """将开机自启信息写入注册表（HKEY_CURRENT_USER下）（省去了配置文件）"""
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "MarkdownWordPasteHelper"

        try:
            # 打开注册表键，准备写入
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enable:
                # 获取当前运行的可执行文件路径
                exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                # 关闭自启则删去键值
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    # 未写入，忽略
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            # 权限不够或者其他原因时，忽略
            return False