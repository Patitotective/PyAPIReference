import sys
import commonmark

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QCursor

if __name__ == "__main__":
    raise RuntimeError("This module requires extra.py module which is outside this folder, you can't run this script as main")
else:
    from pyapireference.ui.github_markdown_style import GITHUB_MARKDOWN_STYLE
    from pyapireference.extra import create_menu

class MarkdownPreviewer(QWebEngineView):    
    stop = pyqtSignal()

    def __init__(self, prefs, initial_md_text="", title="Markdown Preview", scroll_link=None, parent=None, *args, **kwargs):
        """
        Parameters:
            scroll_link=None: A scrollbar to synchronize with (only y not x).
        """
        super().__init__(*args, **kwargs)

        self.parent = parent
        self.prefs = prefs
        self.scroll_link = scroll_link
        self.mouse_hover = False

        self.installEventFilter(self)
        self.setAttribute(Qt.WA_Hover, True)

        self.setHtml(self.markdown_to_html(initial_md_text))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        self.synchronize_scrollbars()

    @property
    def scroll_pos(self):
        return self.page().scrollPosition()

    def set_scroll_pos(self, x:  int, y: int):
        self.page().runJavaScript(f"window.scrollTo({x}, {y});")

    def open_context_menu(self):
        menu = create_menu(
            {
                "Stop previewing": {
                    "callback": self.stop.emit, 
                }, 
            }, 
            parent=self.parent
        )

        menu.exec_(QCursor.pos())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.HoverEnter:
            self.mouse_hover = True

        elif event.type() == QEvent.HoverLeave:
            self.mouse_hover = False

        return super().eventFilter(obj, event)      

    def synchronize_scrollbars(self):
        def scrollbar_changed(value):
            if not self.mouse_hover and self.prefs.file["settings"]["preview_markdown"]["synchronize_scrollbars"]["value"]:
                self.set_scroll_pos(self.scroll_pos.y(), value)

        self.scroll_link.valueChanged.connect(scrollbar_changed)

    def update_markdown(self, md_text):
        self.setHtml(self.markdown_to_html(md_text))

    def markdown_to_html(self, text: str) -> str:
        text = f"<head><style>{GITHUB_MARKDOWN_STYLE}</style></head><body>{commonmark.commonmark(text)}</body>"

        return text

