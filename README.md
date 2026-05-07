# Markdown转Word格式优化粘贴助手 V1.0

一键将Markdown格式文本转换为Word/WPS兼容格式，解决粘贴排版错乱问题。纯本地离线运行，轻量无扰。

## 一、项目简介

在日常办公与科研活动中，从AI大模型、技术文档或笔记软件中复制的内容常为Markdown格式（如 `#` 标题、`**` 加粗等），直接粘贴到Word或WPS中会出现格式混乱与符号残留，手动清理极为繁琐。

本工具即为解决这一痛点而开发。用户复制Markdown文本后，只需在Word中按下快捷键（默认 `Ctrl+Shift+V`），软件便会自动完成格式转换并粘贴到位。转换后的内容完整保留标题层级、加粗、斜体、列表、引用块、代码块、表格、分割线等排版样式，且保持纯文本可编辑状态，不影响后续修改。

**主要特点：**

- **一键转换粘贴**：全局热键触发，自动完成“读取→转换→回写→粘贴”全流程
- **格式完整保留**：支持标题（H1~H6）、加粗、斜体、删除线、有序/无序列表、引用块、代码块、表格、链接、分割线等
- **剪贴板智能监控**：自动识别剪贴板中的Markdown文本并弹出提醒
- **离线安全运行**：所有处理均在本地内存中完成，不产生临时文件，不发起任何网络请求
- **系统托盘常驻**：无主窗口，不占桌面空间，开机可选自启
- **灵活可配置**：支持自定义快捷键、开关监控与提示气泡
- **内容预览**：可查看原始Markdown、转换后纯文本及HTML源码三种视图
- **适配 Word 2016+ / WPS 2019+**

## 二、软件信息

| 项目   | 内容                            |
| ---- | ----------------------------- |
| 软件全称 | Markdown转Word格式优化粘贴助手         |
| 版本号  | V1.0                          |
| 开发语言 | Python 3.8+ / PyQt5           |
| 运行系统 | Windows 10 / Windows 11 (64位) |
| 开发者  | 上海外国语大学，王迈                   |

## 三、使用方法

1. 启动程序（系统托盘常驻，无主窗口界面）
2. 复制任意包含Markdown语法的文本
3. 在Word或WPS中定位光标，按下快捷键 `Ctrl+Shift+V`（默认）
4. 转换后的格式化文本自动粘贴到文档中

**其他功能入口：**

- **双击托盘图标**：快速打开Markdown预览窗口
- **右键托盘图标**：打开完整功能菜单（预览、清空剪贴板、监控开关、设置、关于、退出）

> 快捷键可在托盘菜单“设置”中自定义修改，支持 `Ctrl/Shift/Alt` 与单个字母或数字的组合。

## 四、运行环境要求

- **操作系统**：Windows 10 (64位) 或 Windows 11 (64位)
- **硬件**：1GHz以上处理器，512MB以上内存
- **运行exe**：无需安装Python或任何第三方库，直接双击运行即可
- **配合软件**：Microsoft Word 2016 及以上，或 WPS Office 2019 及以上（效果最佳）

## 五、环境搭建（开发者）

如果你希望从源码运行或二次开发，请按以下步骤操作。

### 1. 克隆仓库

```bash
git clone https://github.com/wangmai617/MarkdownToWordPasteHelper.git
cd MarkdownToWordPasteHelper

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
venv\Scripts\activate      # Windows PowerShell
# 或 venv\Scripts\activate.bat  （CMD）
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

项目仅依赖两个第三方库：

| 库名       | 用途                | 说明       |
| -------- | ----------------- | -------- |
| PyQt5    | GUI框架（系统托盘、对话框等）  | `>=5.15` |
| markdown | Markdown解析，生成HTML | `>=3.4`  |

其余 `import`（如 `re`、`json`、`os`、`sys`、`ctypes`、`threading` 等）均为 Python 标准库，无需额外安装。

### 4. 运行

```bash
python src/main.py
```

### 5. 打包为exe

如需将程序打包为独立可执行文件，使用 PyInstaller：

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "MarkdownWordPasteHelper_V1.0" --hidden-import "markdown.extensions.extra" --hidden-import "markdown.extensions.codehilite" --hidden-import "markdown.extensions.toc" --hidden-import "markdown.extensions.sane_lists" --hidden-import "markdown.extensions.nl2br" "src/main.py"
```

打包完成后，exe 文件位于 `dist\` 目录下，可直接复制给未安装 Python 的用户使用。

也可直接运行项目根目录的 `build_exe.bat` 一键打包（需先安装 PyInstaller）。

## 六、项目结构

```
MarkdownToWordPasteHelper/
├── src/
│   ├── main.py                 # 程序入口，单实例检测与模块初始化
│   ├── markdown_converter.py   # Markdown→HTML核心转换逻辑
│   ├── clipboard_monitor.py    # 剪贴板定时监控与Markdown识别
│   ├── hotkey_manager.py       # 全局快捷键注册与触发
│   ├── tray_controller.py      # 系统托盘图标、右键菜单交互
│   ├── settings_manager.py     # JSON配置文件读写
│   ├── ui_dialogs.py           # 设置对话框与预览窗口
│   └── resources/
│       └── icon.ico            # 程序图标
├── docs/                       # 说明文档
├── requirements.txt            # Python依赖清单
├── build_exe.bat               # 一键打包脚本（需PyInstaller）
├── README.md
├── LICENSE
└── .gitignore
```

## 七、注意事项

- 本工具为绿色免安装软件，直接运行exe即可
- 全程本地离线运行，不联网、不上传数据、不记录剪贴板历史
- 如果快捷键无响应，可能是被其他软件占用，请在设置中更换组合键
- 转换后的排版效果与Word/WPS版本有关，推荐使用较新版本

## 八、版权说明

本项目为个人开发，用于科研办公与教学辅助，已申请软件著作权登记。

© 2026 上海外国语大学，王迈
