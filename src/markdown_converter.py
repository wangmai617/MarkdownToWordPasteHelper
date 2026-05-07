"""
Markdown转Word格式转换模块
将Markdown文本转换为HTML格式，并通过剪贴板以HTML格式写入，
使得在Word中粘贴时样式完整保留。同时也提供纯文本备用。
作者：上海外国语大学，王迈
"""

import markdown
import re
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QApplication

class MarkdownConverter:
    """Markdown到Word格式的转换器，核心是生成内嵌样式表的HTML """
    def __init__(self):
        #初始化markdown解析器，开启常用的几个扩展
        #extra包含表格、代码块等，codehilite做代码高亮（虽然Word支持有限，但也尽量保留）
        #toc是目录，留着备用；sane_lists能解决列表嵌套问题；nl2br把换行转成<br>
        self.md = markdown.Markdown(extensions=[
            'extra',
            'codehilite',
            'toc',
            'sane_lists',
            'nl2br',
        ])

        #self._debug_mode = False
        #此处CSS是调试后的最佳组合（还可精简），目的是让Word粘贴后看起来更自然。
        #基于Word默认的Calibri字体，标题层级、段落间距、引用块样式都尽量接近学术文档习惯。
        #等宽字体使用Consolas，如电脑未安装，Word会回退使用Courier New，都能接受。
        self.css_style = """
        <style>
            body { 
                font-family: 'Calibri', 'Segoe UI', Arial, sans-serif; 
                font-size: 11pt; 
            }
            h1 { font-size: 20pt; font-weight: bold; margin: 12pt 0 6pt 0; }
            h2 { font-size: 16pt; font-weight: bold; margin: 10pt 0 4pt 0; }
            h3 { font-size: 14pt; font-weight: bold; margin: 8pt 0 4pt 0; }
            h4 { font-size: 12pt; font-weight: bold; margin: 6pt 0 2pt 0; }
            h5, h6 { font-size: 11pt; font-weight: bold; margin: 4pt 0 2pt 0; }
            p { margin: 0 0 8pt 0; line-height: 1.4; }
            strong, b { font-weight: bold; }
            em, i { font-style: italic; }
            del, s, strike { text-decoration: line-through; }
            ul, ol { margin: 0 0 8pt 0; padding-left: 20pt; }
            li { margin: 0; }
            blockquote { 
                margin: 8pt 20pt; 
                padding: 4pt 10pt; 
                background: #f0f0f0; 
                border-left: 4px solid #cccccc; 
            }
            pre { 
                background: #f5f5f5; 
                padding: 8pt; 
                font-family: 'Consolas', 'Courier New', monospace; 
                font-size: 10pt; 
                white-space: pre-wrap; 
                word-wrap: break-word;
                margin: 8pt 0;
            }
            code { 
                font-family: 'Consolas', 'Courier New', monospace; 
                background: #f5f5f5; 
                padding: 1pt 2pt; 
                font-size: 10pt;
            }
            table { 
                border-collapse: collapse; 
                margin: 8pt 0; 
                width: auto; 
            }
            th, td { 
                border: 1px solid #999; 
                padding: 4pt 6pt; 
                text-align: left; 
            }
            th { background: #e0e0e0; font-weight: bold; }
            hr { 
                border: none; 
                border-top: 1px solid #aaa; 
                margin: 12pt 0; 
            }
            a { color: #0563c1; text-decoration: underline; }
        </style>
        """

    def convert_to_html(self, markdown_text):
        """把markdown文本拼成一个可以直接粘贴到Word的完整HTML页面。
        返回：字符串形式的HTML文档。"""
        #先使用markdown库把内容转成body里的html
        body_html = self.md.convert(markdown_text)
        #再把css和body拼成一份标准html文件，这样Word能完整识别样式
        full_html = (
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            '<meta charset="utf-8">\n'
            f"{self.css_style}\n"
            "</head>\n"
            "<body>\n"
            f"{body_html}\n"
            "</body>\n"
            "</html>"
        )
        #full_html = full_html.replace('<html>', '<html lang="zh">')  #保留，加语言标记
        return full_html

    def convert_and_copy_to_clipboard(self, markdown_text=None):
        """ 核心方法：读剪贴板里的markdown，转成HTML，再写回剪贴板。
        如果markdown_text参数不为空，就直接转换给定的文本（用于预览等场景）。
        返回：(是否成功, 转换后的纯文本预览或错误信息)"""
        clipboard = QApplication.clipboard()

        # 如果没有传入文本，就从系统剪贴板读取
        if markdown_text is None:
            mime = clipboard.mimeData()
            if mime.hasText():
                markdown_text = mime.text()
            else:
                return False, "剪贴板内无文本内容，请先复制入剪切板"

        #空内容或全是空白符也直接返回，免得生成空页面
        if not markdown_text or not markdown_text.strip():
            return False, "剪贴板内容为空"

        #有些编辑器会在开头加BOM头，需要去除，不然转换后可能会有乱码
        if markdown_text.startswith('\ufeff'):
            markdown_text = markdown_text[1:]
            # else:
            #     pass

        try:
            html_content = self.convert_to_html(markdown_text)
            # 准备一个MimeData对象，同时放入HTML和纯文本两种格式
            # 这样在Word里粘贴用的是HTML，在记事本里粘贴也能看到纯文本
            mime_data = QMimeData()
            mime_data.setHtml(html_content)
            mime_data.setText(markdown_text)  #纯文本版本留着备用
            clipboard.setMimeData(mime_data, QClipboard.Clipboard)

            # 生成一个去掉大部分标记符号的纯文本，给预览窗口用
            preview_text = self.markdown_to_plain_preview(markdown_text)
            return True, preview_text
        except Exception as e:
            # 把异常信息传出去，让上层显示
            return False, f"转换失败：{str(e)}"

    def markdown_to_plain_preview(self, markdown_text):
        """把Markdown转成纯文本预览，只用于预览功能，不参与正式转换。
        这里使用一组正则替换，按顺序处理，注意不能随意更改顺序。"""
        text = markdown_text

        # ---逐层剥除Markdown格式符号
        #去掉标题的#号
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        #去加粗和斜体：**text** 和 *text*
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)

        #删除线 ~~text~~
        text = re.sub(r'~~(.*?)~~', r'\1', text)

        #引用符号 >
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

        #无序列表标记 - * +
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        #有序列表标记 1. 2. 等
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        #代码块：用[代码块]占位，避免内部内容干扰
        text = re.sub(r'```.*?```', '[代码块]', text, flags=re.DOTALL)
        #内联代码
        text = re.sub(r'`(.*?)`', r'\1', text)

        #链接：只保留文字
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        #图片：替换成[图片]
        text = re.sub(r'!\[.*?\]\(.*?\)', '[图片]', text)

        #分割线 --- *** ___ 等，统一换成三个横线
        text = re.sub(r'^[-*_]{3,}$', '---', text, flags=re.MULTILINE)

        return text.strip()

    def clear_clipboard(self):
        """清空剪贴板，连HTML和纯文本都清掉 """
        clipboard = QApplication.clipboard()
        clipboard.clear(QClipboard.Clipboard)
        return True

    # 调试用
    # def _debug_print_html(self, html_snippet):
    #     """打印部分html片段，用于调试转换结果"""
    #     # print(html_snippet[:200])
    #     pass