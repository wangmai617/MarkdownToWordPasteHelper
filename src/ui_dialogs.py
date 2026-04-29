"""
UI对话框模块
主要处理预览窗口（设置窗口已移除）

作者：上海外国语大学/王迈
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QLineEdit, QTextEdit,
    QGroupBox, QTabWidget,
    QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QKeySequence   # 暂时不用了


#  ===== 预览窗口，用来展示markdown转换结果，共三个页面 =====
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