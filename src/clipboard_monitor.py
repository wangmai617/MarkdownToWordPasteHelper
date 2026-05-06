"""
剪贴板监控模块
实时监测剪贴板内容变化，识别是否为Markdown文本。
为了省资源，用轮询的方式，每半秒多查一次。
王迈（上海外国语大学）
"""

from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QApplication
import re

class ClipboardMonitor(QObject):
    def __init__(self, converter, tray_controller):
        super().__init__()
        self.converter = converter# 转换器，预留，暂时不用
        self.tray = tray_controller# 托盘，用来弹出气泡
        self.clipboard = QApplication.clipboard()
        self.last_text = ""# 上一次的内容，用于去重
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.is_monitoring = False
        # 检测Markdown用的正则列表，简单检测。
        # 根据日常使用经验，这些特征组合起来误判率已经很低
        self.md_hints = [
            r'^#{1,6}\s',             # 标题
            r'\*\*.*\*\*',            # 加粗
            r'\*[^*].*\*',            # 斜体
            r'~~.*~~',                # 删除线
            r'^\s*[-*+]\s',           # 无序列表
            r'^\s*\d+\.\s',           # 有序列表
            r'^>\s',                  # 引用
            r'```',                   # 代码块
            # r'\|.*\|',                # 表格（先保留，有时误报太多）
            r'\[.*\]\(.*\)',          # 链接
        ]
        # 记录检测次数，调试用
        self._check_count = 0
        # self._debug_info = {} #记录每个特征命中次数

    def start(self):
        """开始监控，设置一个合适的定时器间隔"""
        if not self.is_monitoring:
            self.last_text = self.get_clipboard_text()
            # 间隔520毫秒
            self.timer.start(520)
            self.is_monitoring = True

    def stop(self):
        """停止监控，关掉定时器"""
        if self.is_monitoring:
            self.timer.stop()
            self.is_monitoring = False

    def get_clipboard_text(self):
        """从剪贴板里取出纯文本，没有就返回空字符串"""
        mime_data = self.clipboard.mimeData()
        if mime_data.hasText():
            return mime_data.text()
        return ""

    def is_markdown_text(self, text):
        """
        简单判断一段文本是不是Markdown。
        方法：计数命中了几个特征模式，超过1个就认为是。
              如果文本太短（少于3个字符）就直接跳过，避免误判。
        """
        if not text or len(text) < 3:
            return False
        txt_len = len(text)  #记录长度
        count = 0
        for pat in self.md_hints:
            if re.search(pat, text, re.MULTILINE):
                count += 1
                if count >= 2:   #命中两个就算
                    return True
        return False

    def check_clipboard(self):
        """
        定时器回调，每次检查一下剪贴板内容是否有改变。
        如有改变，则观察是不是Markdown，是就按设置决定是否弹提示。
        """
        # print(f'Check #{self._check_count}')  # 调试时开着，正式版注释掉
        self._check_count += 1   # 只是记个数，没实际作用，以后可去
        current_text = self.get_clipboard_text()
        # 剪切板没文本或者和上次一样，不处理
        if not current_text or current_text == self.last_text:
            return
        self.last_text = current_text
        if self.is_markdown_text(current_text):
            if self.tray.settings.get_show_tips():
                self.tray.show_message(
                    "检测到Markdown内容",
                    "可使用Ctrl+Shift+V转换粘贴"
                )

    def get_current_markdown(self):
        """直接返回当前剪贴板的文本，给预览功能用的"""
        return self.get_clipboard_text()