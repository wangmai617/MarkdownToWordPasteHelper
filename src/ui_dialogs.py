"""
UI对话框模块
主要处理设置窗口及预览窗口
作者：上海外国语大学，王迈
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
    def __init__(self, settings, hotkey_manager, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.hotkey_manager = hotkey_manager
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)
        self.init_ui()
        self.load_settings()
        #上面载入顺序可任意

    def init_ui(self):
        layout = QVBoxLayout()

        #快捷键部分
        hotkey_group = QGroupBox("快捷键设置")
        form = QFormLayout()
        self.mod_combo = QComboBox()
        self.mod_combo.addItems(["Ctrl+Shift", "Ctrl+Alt", "Shift+Alt", "Ctrl+Shift+Alt"])
        form.addRow("修饰键:", self.mod_combo)

        #按键输入，一个字母或数字
        key_layout = QHBoxLayout()
        self.key_edit = QLineEdit()
        self.key_edit.setMaxLength(1)
        self.key_edit.setPlaceholderText("例如: V")
        key_layout.addWidget(self.key_edit)
        key_layout.addWidget(QLabel("(单个字母或数字)"))
        form.addRow("按键:", key_layout)

        hotkey_group.setLayout(form)
        layout.addWidget(hotkey_group)

        #常规设置组
        general_group = QGroupBox("常规设置")
        general_layout = QVBoxLayout()
        self.monitor_check = QCheckBox("启用剪贴板监控（检测到Markdown时提示）")
        self.tips_check = QCheckBox("显示操作提示气泡")
        self.autostart_check = QCheckBox("开机自动启动")
        general_layout.addWidget(self.monitor_check)
        general_layout.addWidget(self.tips_check)
        general_layout.addWidget(self.autostart_check)
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        #保存和取消按钮
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
        config = self.settings.get_hotkey_config()
        mod_str = config.get('modifiers', 'Ctrl+Shift')
        # 找出匹配的索引
        index = self.mod_combo.findText(mod_str)
        if index >= 0:
            self.mod_combo.setCurrentIndex(index)
        self.key_edit.setText(config.get('key', 'V'))
        self.monitor_check.setChecked(self.settings.get_clipboard_monitor_enabled())
        self.tips_check.setChecked(self.settings.get_show_tips())
        self.autostart_check.setChecked(self.settings.get_auto_start())

    def save_settings(self):
        #修饰键解析
        mod_str = self.mod_combo.currentText()
        mod_str_orig = mod_str  #保留原始值
        key_char = self.key_edit.text().strip().upper()
        if not key_char or len(key_char) != 1:
            QMessageBox.warning(self, "输入错误", "请输入单个字母或数字作为快捷键按键")
            return

        modifiers = 0
        if 'Ctrl' in mod_str:
            modifiers |= 0x0002
        if 'Shift' in mod_str:
            modifiers |= 0x0004
        if 'Alt' in mod_str:
            modifiers |= 0x0001

        vk_code = ord(key_char)

        #更新快捷键，如果管理器还存在
        if self.hotkey_manager:
            self.hotkey_manager.update_hotkey(modifiers, vk_code)

        #保存其他设置
        self.settings.set_clipboard_monitor_enabled(self.monitor_check.isChecked())
        self.settings.set_show_tips(self.tips_check.isChecked())
        self.settings.set_auto_start(self.autostart_check.isChecked())

        #处理开机自启
        if hasattr(self.parent(), 'set_auto_start'):
            self.parent().set_auto_start(self.autostart_check.isChecked())

        self.accept()

# ===预览窗口，用来展示markdown转换结果，共三个页面===   #
class PreviewDialog(QDialog):
    def __init__(self, markdown_text, plain_preview, html_preview, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Markdown预览")
        self.resize(700, 500)

        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        #页面一: 原始markdown内容
        md_tab = QWidget()
        md_layout = QVBoxLayout()
        md_edit = QTextEdit()
        md_edit.setPlainText(markdown_text)
        md_edit.setReadOnly(True)
        md_layout.addWidget(md_edit)
        md_tab.setLayout(md_layout)
        tab_widget.addTab(md_tab, "原始Markdown")

        #页面二: 纯文本预览（转换后）
        plain_tab = QWidget()
        plain_layout = QVBoxLayout()
        plain_edit = QTextEdit()
        plain_edit.setPlainText(plain_preview)
        plain_edit.setReadOnly(True)
        plain_layout.addWidget(plain_edit)
        plain_tab.setLayout(plain_layout)
        tab_widget.addTab(plain_tab, "转换后文本预览")

        #页面三: HTML源码，供预览
        html_tab = QWidget()
        html_layout = QVBoxLayout()
        html_edit = QTextEdit()
        html_edit.setPlainText(html_preview)
        html_edit.setReadOnly(True)
        html_layout.addWidget(html_edit)
        html_tab.setLayout(html_layout)
        tab_widget.addTab(html_tab, "HTML源码")

        layout.addWidget(tab_widget)

        #关闭按钮
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)