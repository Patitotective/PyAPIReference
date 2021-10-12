import sys
import commonmark

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView

if __name__ == "__main__":
    from github_markdown_style import GITHUB_MARKDOWN_STYLE
else:
    from GUI.github_markdown_style import GITHUB_MARKDOWN_STYLE

class MarkdownPreviewer(QWidget):
    closed = pyqtSignal()
    def __init__(self, prefs, initial_md_text="", title="Markdown Preview", scroll_link=None, *args, **kwargs):
        """
        Parameters:
            scroll_link=None: A scrollbar to synchronize with (only y not x).
        """
        super().__init__(*args, **kwargs)

        self.prefs = prefs
        self.scroll_link = scroll_link
        self.mouse_hover = False

        self.installEventFilter(self)
        self.setAttribute(Qt.WA_Hover, True)

        self.setLayout(QVBoxLayout())
        self.setWindowTitle(title)

        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.markdown_to_html(initial_md_text))

        self.synchronize_scrollbars()

        self.layout().addWidget(self.web_view)

    @property
    def scroll_pos(self):
        return self.web_view.page().scrollPosition()

    def set_scroll_pos(self, x:  int, y: int):
        self.web_view.page().runJavaScript(f"window.scrollTo({x}, {y});")

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()

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
        self.web_view.setHtml(self.markdown_to_html(md_text))

    def markdown_to_html(self, text: str) -> str:
        text = f"<head><style>{GITHUB_MARKDOWN_STYLE}</style></head><body>{commonmark.commonmark(text)}</body>"

        return text


if __name__ == '__main__':
   app = QApplication(sys.argv)
   
   markdown_previewer_dialog = MarkdownPreviewer(path)
   markdown_previewer_dialog.show()

   sys.exit(app.exec_())
