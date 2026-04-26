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
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QClipboard


class TrayController(QWidget):
    """继承了QWidget，但不显示，只用来挂托盘图标"""

    def __init__(self):
        super().__init__()
        # 提示气泡默认开启
        self.show_tips = True

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

    def _paste_demo_html(self):
        """生成一段固定的示例HTML内容并写入剪贴板，模拟转换结果"""
        # 这是一段写死的演示内容，包含标题、列表和加粗
        demo_html = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            '<meta charset="utf-8">\n'
            "<style>\n"
            "body { font-family: 'Calibri', sans-serif; font-size: 11pt; }\n"
            "h2 { font-size: 16pt; font-weight: bold; }\n"
            "strong { font-weight: bold; }\n"
            "ul { margin-left: 20pt; }\n"
            "</style>\n"
            "</head>\n"
            "<body>\n"
            "<h2>示例转换结果</h2>\n"
            "<p>这是一个 <strong>演示</strong> 段落，Markdown 转换模块尚未集成。</p>\n"
            "<ul>\n"
            "<li>功能仍在开发中</li>\n"
            "<li>请期待后续更新</li>\n"
            "</ul>\n"
            "</body>\n"
            "</html>"
        )
        plain_text = "示例转换结果\n这是一个演示段落，Markdown转换模块尚未集成。\n- 功能仍在开发中\n- 请期待后续更新"
        
        mime_data = QMimeData()
        mime_data.setHtml(demo_html)
        mime_data.setText(plain_text)
        
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime_data, QClipboard.Clipboard)
        return True, plain_text

    def manual_convert_paste(self):
        """用户通过菜单点击"转换并粘贴"时调用，写入固定演示内容到剪贴板"""
        success, preview = self._paste_demo_html()
        if success:
            if self.show_tips:
                self.show_message("已写入剪贴板", "演示内容已就绪，请在Word中按Ctrl+V粘贴")
        else:
            self.show_message("操作失败", preview)

    def clear_clipboard(self):
        """清空剪贴板，避免隐私泄漏"""
        clipboard = QApplication.clipboard()
        clipboard.clear(QClipboard.Clipboard)
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
            "<p>使用方法：右键托盘图标选择\"转换并粘贴\"，然后在Word中Ctrl+V粘贴。</p>"
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