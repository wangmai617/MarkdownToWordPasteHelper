"""
UI对话框模块
主要处理设置窗口及预览窗口

作者：上海外国语大学/王迈
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QLineEdit, QTextEdit,
    QGroupBox, QFormLayout, QComboBox, QTabWidget,
    QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence


#  ===== 设置对话框  ========
class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        # hotkey_manager 参数已移除
        self.setWindowTitle("设置")
        self.setMinimumWidth(350)
        self.init_ui()
        self.load_settings()
        # 上面载入顺序可任意

    def init_ui(self):
        layout = QVBoxLayout()

        # 快捷键设置组已移除

        # 常规设置组
        general_group = QGroupBox("常规设置")
        general_layout = QVBoxLayout()
        self.tips_check = QCheckBox("显示操作提示气泡")
        self.autostart_check = QCheckBox("开机自动启动")
        general_layout.addWidget(self.tips_check)
        general_layout.addWidget(self.autostart_check)
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # 保存和取消按钮
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("保存")
        btn_save.clicked.connect(self.save_settings)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_settings(self):
        # 加载提示气泡和开机自启设置
        self.tips_check.setChecked(self.settings.get_show_tips())
        self.autostart_check.setChecked(self.settings.get_auto_start())

    def save_settings(self):
        # 保存其他设置
        self.settings.set_show_tips(self.tips_check.isChecked())
        self.settings.set_auto_start(self.autostart_check.isChecked())

        # 处理开机自启
        if hasattr(self.parent(), 'set_auto_start'):
            self.parent().set_auto_start(self.autostart_check.isChecked())

        self.accept()


# ================================================ #
# 预览窗口，用来展示markdown转换结果，共三个页面 #
# ================================================ #
class PreviewDialog(QDialog):
    def __init__(self, markdown_text, plain_preview, html_preview, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Markdown预览")
        self.resize(700, 500)
        # self.setWindowIcon(...)   # 以后可以加个预览专用图标

        layout = QVBoxLayout()

        tab_widget = QTabWidget()

        # 页面一: 原始markdown内容
        md_tab = QWidget()
        md_layout = QVBoxLayout()
        md_edit = QTextEdit()
        md_edit.setPlainText(markdown_text)
        md_edit.setReadOnly(True)
        md_layout.addWidget(md_edit)
        md_tab.setLayout(md_layout)
        tab_widget.addTab(md_tab, "原始Markdown")

        # 页面二: 纯文本预览（转换后）
        plain_tab = QWidget()
        plain_layout = QVBoxLayout()
        plain_edit = QTextEdit()
        plain_edit.setPlainText(plain_preview)
        plain_edit.setReadOnly(True)
        plain_layout.addWidget(plain_edit)
        plain_tab.setLayout(plain_layout)
        tab_widget.addTab(plain_tab, "转换后文本预览")

        # 页面三: HTML源码，供预览
        html_tab = QWidget()
        html_layout = QVBoxLayout()
        html_edit = QTextEdit()
        html_edit.setPlainText(html_preview)
        html_edit.setReadOnly(True)
        html_layout.addWidget(html_edit)
        html_tab.setLayout(html_layout)
        tab_widget.addTab(html_tab, "HTML源码")

        layout.addWidget(tab_widget)

        # 关闭按钮
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)