"""
系统托盘控制器及主界面逻辑
包含了托盘图标、右键菜单、设置窗口、预览窗口等。
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
from ui_dialogs import SettingsDialog, PreviewDialog


class TrayController(QWidget):
    """继承了QWidget，但不显示，只用来挂托盘图标"""

    def __init__(self, settings, converter):
        super().__init__()
        self.settings = settings          # 保存用户设置对象
        self.converter = converter        # Markdown转换器
        self.hotkey_manager = None        # 热键管理器
        # self.debug = False  # 也许以后加个调试模式

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

        # 双击托盘图标以预览剪贴板内容
        self.tray_icon.activated.connect(self.on_tray_activated)

        # 此窗口无用，隐藏起来
        self.hide()

    def set_hotkey(self, hotkey):
        """将外部创建的热键对象传入，方便菜单里操作"""
        self.hotkey_manager = hotkey

    def create_tray_menu(self):
        """组装托盘右键菜单，顺序符合一般习惯"""
        menu = QMenu()

        # 手动转换粘贴，与快捷键功能相同
        # 暂时去除此菜单项。由于焦点不在Word/WPS，托盘图标右键粘贴无法实现。
        # action_convert = QAction("转换并粘贴(&P)", self)
        # action_convert.triggered.connect(self.manual_convert_paste)
        # menu.addAction(action_convert)

        # 预览剪贴板中Markdown原文及转换结果
        action_preview = QAction("预览Markdown(&M)", self)
        action_preview.triggered.connect(self.preview_markdown)
        menu.addAction(action_preview)

        # 清空剪切板
        action_clear = QAction("清空剪贴板(&C)", self)
        action_clear.triggered.connect(self.clear_clipboard)
        menu.addAction(action_clear)

        menu.addSeparator()

        # 剪贴板监控菜单项已移除
        # menu.addSeparator()

        # 打开设置对话框，修改快捷键
        action_settings = QAction("设置(&S)", self)
        action_settings.triggered.connect(self.open_settings)
        menu.addAction(action_settings)

        # 也许将来加个导出功能
        # action_export = QAction("导出HTML", self)
        # action_export.triggered.connect(self.export_html)
        # menu.addAction(action_export)

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

    def on_tray_activated(self, reason):
        """处理托盘图标的激活事件，目前只响应双击（打开预览）"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.preview_markdown()

    # 同上，转换粘贴菜单项已去除，仅保留代码
    # def manual_convert_paste(self):
    #     """用户通过菜单点击“转换并粘贴”时调用，功能同快捷键"""
    #     if self.hotkey_manager:
    #         self.hotkey_manager.on_hotkey_pressed()

    def _get_clipboard_text(self):
        """直接从系统剪贴板获取纯文本，无文本则返回空字符串"""
        mime_data = QApplication.clipboard().mimeData()
        if mime_data.hasText():
            return mime_data.text()
        return ""

    def preview_markdown(self):
        """弹出预览窗口，查看当前剪贴板Markdown内容及转换后样式"""
        md_text = self._get_clipboard_text()
        if not md_text:
            QMessageBox.information(None, "预览", "剪贴板中没有文本内容")
            return

        # 生成预览用的HTML和纯文本，注意：并未更改剪切板内容。
        preview_html = self.converter.convert_to_html(md_text)
        preview_plain = self.converter.markdown_to_plain_preview(md_text)

        dialog = PreviewDialog(md_text, preview_plain, preview_html, self)
        dialog.exec_()

    def clear_clipboard(self):
        """清空剪贴板，避免隐私泄漏"""
        self.converter.clear_clipboard()
        self.show_message("操作完成", "剪贴板已清空")

    # toggle_monitor 方法已移除

    def open_settings(self):
        """打开设置对话框，若用户点击保存，则同步监控开关状态"""
        dialog = SettingsDialog(self.settings, self.hotkey_manager, self)
        # 用exec_显示模态对话框，返回是否点击保存
        if dialog.exec_() == QDialog.Accepted:
            # 设置对话框内已无监控选项，无需同步菜单项
            pass

    def show_about(self):
        """弹出关于对话框，显示作者、版本、快捷键等信息"""
        hotkey_str = "未设置"
        if self.hotkey_manager:
            # modifiers_to_string返回像"Ctrl+Shift"这样的字符串
            hotkey_str = f"{self.hotkey_manager.modifiers_to_string()} + {chr(self.hotkey_manager.vk_code)}"

        # 用HTML格式写简单的软件说明，注意项目名两边的引号用单引号字符串避免冲突
        about_text = (
            "<h2>Markdown转Word格式优化粘贴助手 V1.0</h2>"
            "<p>本软件将Markdown格式转换为Word格式，并保留基本排版信息。</p>"
            "<p>本地离线运行，无须联网，不收集任何数据。</p>"
            '<p>"上海外国语大学中国语言文学国际传播平台建设与研究项目"使用</p>'
            "<p>开发者：王迈 (上海外国语大学)</p>"
            "<p>邮箱：wangmai@shisu.edu.cn</p>"
            "<hr>"
            f"<p>当前快捷键：{hotkey_str}</p>"
        )
        QMessageBox.about(None, "关于", about_text)

    def exit_app(self):
        """完全退出程序：注销快捷键，隐藏图标，退出Qt循环"""
        if self.hotkey_manager:
            self.hotkey_manager.unregister_hotkey()
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
            # print(e)  # 调试时可以看看异常类型
            # 权限不够或者其他原因时，忽略
            return False