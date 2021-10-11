import sys
import commonmark

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QTextBrowser
from PyQt5.QtWebEngineWidgets import QWebEngineView

if __name__ == "__main__":
    from github_markdown_style import GITHUB_MARKDOWN_STYLE
else:
    from GUI.github_markdown_style import GITHUB_MARKDOWN_STYLE

class MarkdownPreviewer(QWidget):
    def __init__(self, initial_md_text="", title="Markdown preview", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout())
        self.setWindowTitle(title)
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.markdown_to_html(initial_md_text))

        self.layout().addWidget(self.web_view)

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
