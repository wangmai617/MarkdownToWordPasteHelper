"""
配置管理模块
读写JSON配置文件，保存用户的偏好设置。
配置会放在用户目录下的一个隐藏文件夹里，这样不同用户互不干扰。

作者：上海外国语大学/王迈
"""

import json
import os

class SettingsManager:
    def __init__(self, config_file="config.json"):
        # 配置文件保存在用户主目录下，用句点打头的文件夹下
        self.config_dir = os.path.join(os.path.expanduser("~"), ".MarkdownWordPasteHelper")
        # 如果文件夹不存在就新建，exist_ok=True更简洁，但这里用老写法兼容性更好
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        self.config_path = os.path.join(self.config_dir, config_file)

        # 这是默认设置，如果配置文件缺了某些字段，就用它补上
        self.default_config = {
            "hotkey": {
                "modifiers": "Ctrl+Shift",
                "key": "V"
            },
            "clipboard_monitor": True,
            "show_tips": True,
            "auto_start": False
        }

        # 加载配置（不存在时自动生成默认的）
        self.config = self.load_config()
        # 有些时候可能需要恢复默认，预留一个方法
        # self.reset_to_default()

    def load_config(self):
        """从文件读取配置，如果文件坏了或者不存在，就用默认值 """
        # print('loading config...')  # 以前用来观察加载时机
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 把默认配置里有的、但文件里缺失的字段补上
                # 防止升级版本后新加的设置项找不到
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception:
                # 文件可能损坏，返回默认配置的副本
                pass
        # 文件不存在或读取失败，返回默认配置的深拷贝
        return self.default_config.copy()

    def save_config(self):
        """将当前配置写回文件。静默处理写入异常，避免程序闪退"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                # f.flush()  # 保险起见，但os.fsync可能更好，先不管
            return True
        except Exception:
            # 权限不足或者磁盘无空间，吞掉异常
            return False

    # 调试用，预留打印配置的方法
    # def debug_print_config(self):
    #     print(json.dumps(self.config, indent=2))

    # ---- 下面是具体设置项的getter/setter

    def get_hotkey_config(self):
        # 热键配置是一个字典，包含修饰键和按键
        return self.config.get("hotkey", self.default_config["hotkey"])

    def set_hotkey_config(self, modifiers_str, key_char):
        self.config["hotkey"] = {"modifiers": modifiers_str, "key": key_char}
        self.save_config()

    def get_clipboard_monitor_enabled(self):
        return self.config.get("clipboard_monitor", True)

    def set_clipboard_monitor_enabled(self, enabled):
        self.config["clipboard_monitor"] = enabled
        self.save_config()

    def get_show_tips(self):
        # 是否显示托盘气泡提示，可关闭
        return self.config.get("show_tips", True)

    def set_show_tips(self, enabled):
        self.config["show_tips"] = enabled
        self.save_config()

    def get_auto_start(self):
        return self.config.get("auto_start", False)

    def set_auto_start(self, enabled):
        self.config["auto_start"] = enabled
        self.save_config()

    # 重置功能暂不启用
    # def reset_to_default(self):
    #     self.config = self.default_config.copy()
    #     self.save_config()