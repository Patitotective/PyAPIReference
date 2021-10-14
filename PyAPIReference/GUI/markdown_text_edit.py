from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui import QTextOption

class MarkdownTextEdit(QTextEdit):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWordWrapMode(QTextOption.NoWrap)
		self.setCursorWidth(2)
