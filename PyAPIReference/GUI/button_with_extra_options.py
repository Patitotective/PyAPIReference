import sys
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QMainWindow, QMenu, QAction, QHBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QCursor, QFont, QFontMetrics

from typing import List, Tuple, Callable

def get_text_size(text: str):
	font = QFont()
	font = QFont(font.defaultFamily())
	font_metrics = QFontMetrics(font)

	return QSize(font_metrics.width(text), font_metrics.height())


class MainWindow(QMainWindow):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		widget = QWidget()
		widget.setLayout(QHBoxLayout())

		button = ButtonWithExtraOptions("Button")
		widget.layout().addWidget(button)

		self.setCentralWidget(widget)

		self.show()

class ButtonWithExtraOptions(QWidget):
	def __init__(self, text, actions: List[Tuple[str, Callable]]=[("Example", lambda: print("example"))], extra_button_text: str="+", parent=None):
		super().__init__(parent=parent)

		self.actions = actions
		self.parent = parent

		self.setLayout(QHBoxLayout())

		self.main_button = QPushButton(text)

		self.extra_button = QPushButton(extra_button_text)
		self.extra_button.clicked.connect(self.extra_options_context_menu)

		self.extra_button.setFixedWidth(get_text_size(extra_button_text).width() + 15)

		self.layout().addWidget(self.main_button)
		self.layout().addWidget(self.extra_button)

	def extra_options_context_menu(self):
		menu = QMenu(self.parent)

		for action_name, action_callback in self.actions:
			action = QAction(action_name)
			action.triggered.connect(action_callback)

			menu.addAction(action)

		menu.exec_(QCursor.pos())

if __name__ == "__main__":
	app = QApplication(sys.argv)

	main_window = MainWindow()

	sys.exit(app.exec_())
