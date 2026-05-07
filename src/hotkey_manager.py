"""
全局快捷键管理模块
功能：注册全局快捷键Ctrl+Shift+V（也可自定义），键入时触发Markdown转换粘贴。
主要靠RegisterHotKey这个API实现，因要全局监听，不能只用Qt的快捷键，否则只在应用激活时有效。
作者：上海外国语大学，王迈
"""

from PyQt5.QtCore import QObject, pyqtSignal
import ctypes
from ctypes import wintypes
import threading
import time

### WindowsAPI常量，修饰键的值是固定的，勿动
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
WM_HOTKEY = 0x0312   # 快捷键消息ID

class HotkeyManager(QObject):
    #自定义信号：快捷键被按下时发出，在主线程中处理
    hotkey_triggered = pyqtSignal()

    def __init__(self, settings, tray, converter, monitor):
        super().__init__()
        self.settings = settings
        self.tray = tray
        self.converter = converter
        self.monitor = monitor
        self.hotkey_id = 1   #指定一个ID，之后注册和注销都用这个
        self.modifiers = MOD_CONTROL | MOD_SHIFT  #默认为Ctrl+Shift
        self.vk_code = ord('V')     # 默认为V键
        self.is_registered = False
        self.running = True

        # 把上次保存的快捷键配置读出来
        self.load_settings()

        # 将信号连到处理函数，这样线程里收到消息后能安全地操作UI
        self.hotkey_triggered.connect(self.on_hotkey_pressed)

    def load_settings(self):
        """从配置文件里读热键设置，覆盖默认值"""
        config = self.settings.get_hotkey_config()
        #解析修饰键字符串，如'Ctrl+Shift' => MOD_CONTROL | MOD_SHIFT
        if 'modifiers' in config:
            mod_str = config['modifiers']
            self.modifiers = 0
            if 'Ctrl' in mod_str:
                self.modifiers |= MOD_CONTROL
            # else:
            #     #不包含Ctrl，啥也不做
            #     pass
            if 'Shift' in mod_str:
                self.modifiers |= MOD_SHIFT
            if 'Alt' in mod_str:
                self.modifiers |= MOD_ALT
            #若配置文件为空，则默认使用此配置
            if self.modifiers == 0:
                self.modifiers = MOD_CONTROL | MOD_SHIFT
        if 'key' in config:
            key_str = config['key']
            if len(key_str) == 1:
                self.vk_code = ord(key_str.upper())
            #若key_str长度不对，仍使用默认的V
            #else的情况不需要特别处理，默认值已设好

    def save_settings(self):
        """把当前热键设置持久化到配置文件 """
        mod_names = []
        if self.modifiers & MOD_CONTROL:
            mod_names.append('Ctrl')
        if self.modifiers & MOD_SHIFT:
            mod_names.append('Shift')
        if self.modifiers & MOD_ALT:
            mod_names.append('Alt')
        mod_str = '+'.join(mod_names) if mod_names else 'Ctrl+Shift'
        key_char = chr(self.vk_code)
        self.settings.set_hotkey_config(mod_str, key_char)

    def modifiers_to_string(self):
        """返回修饰键的可读字符串，如Ctrl+Shift，给设置界面显示用"""
        parts = []
        if self.modifiers & MOD_CONTROL:
            parts.append('Ctrl')
        if self.modifiers & MOD_SHIFT:
            parts.append('Shift')
        if self.modifiers & MOD_ALT:
            parts.append('Alt')
        return '+'.join(parts) if parts else 'Ctrl+Shift'

    def register_hotkey(self):
        """注册全局热键，放在独立线程里跑消息循环，以免阻塞主线程"""
        if self.is_registered:
            return True

        def hotkey_thread():
            # user32已在上面import过，这里直接获取
            user32 = ctypes.windll.user32
            # 尝试注册，如果失败，则考虑组合键已被其他程序占用
            if not user32.RegisterHotKey(None, self.hotkey_id, self.modifiers, self.vk_code):
                self.tray.show_message(
                    "快捷键注册失败",
                    "快捷键可能被占用，请在设置里更换组合键"
                )
                return

            self.is_registered = True

            #进入消息循环，不停Peek消息
            msg = wintypes.MSG()
            while self.running and self.is_registered:
                # PM_REMOVE=1，取到消息就删除
                if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                    # 是我们注册的快捷键吗？
                    if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                        #发射信号，实际转换操作让主线程去做
                        self.hotkey_triggered.emit()
                    # 其它消息按标准流程分发
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                else:
                    #没消息就休息，不占据CPU
                    time.sleep(0.05)

            # 退出循环后注销热键
            user32.UnregisterHotKey(None, self.hotkey_id)

        # 启动守护线程，主程序退出时它会自动结束
        self.thread = threading.Thread(target=hotkey_thread, daemon=True)
        self.thread.start()
        return True

    def unregister_hotkey(self):
        """停止监听，线程自动结束"""
        self.running = False
        self.is_registered = False
        #如需主动等待线程结束：
        # if hasattr(self, 'thread') and self.thread.is_alive():
        #     self.thread.join(timeout=1)

    def update_hotkey(self, modifiers, vk_code):
        """更换快捷键组合时调用"""
        #先将旧快捷键注销
        if self.is_registered:
            user32 = ctypes.windll.user32
            user32.UnregisterHotKey(None, self.hotkey_id)
            self.is_registered = False

        #换成新值
        self.modifiers = modifiers
        self.vk_code = vk_code
        self.save_settings()

        #立即重新注册
        self.register_hotkey()

    def on_hotkey_pressed(self):
        """热键实际触发后的业务逻辑（在主线程执行）"""
        # 执行Markdown到HTML转换并推入剪切板
        success, preview = self.converter.convert_and_copy_to_clipboard()
        if success:
            #模拟Ctrl+V把内容粘贴出去
            self.simulate_paste()
            #如果用户没关提示，就弹气泡
            if self.settings.get_show_tips():
                self.tray.show_message("转换成功", "已转换为Word格式并粘贴")
        else:
            #失败则弹出气泡显示原因
            self.tray.show_message("转换失败", preview)

    def simulate_paste(self):
        """用keybd_event模拟Ctrl+V。这里先按Ctrl再按V，松开时倒序，不能错"""
        user32 = ctypes.windll.user32
        #按下Ctrl
        user32.keybd_event(0x11, 0, 0, 0)   # VK_CONTROL
        #按下V
        user32.keybd_event(0x56, 0, 0, 0)   # VK_V
        #松开V
        user32.keybd_event(0x56, 0, 2, 0)   # KEYEVENTF_KEYUP = 2
        #松开Ctrl
        user32.keybd_event(0x11, 0, 2, 0)
        #注意：顺序不能错，否则组合键状态可能卡住