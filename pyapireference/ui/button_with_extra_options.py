import sys
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QMainWindow, QMenu, QAction, QHBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QCursor, QFont, QFontMetrics

from typing import List, Tuple, Callable

if __name__ == "__main__":
    raise RuntimeError("button_with_extra_options.py requires get_text_size from pyapireference.extra.py which is outside this folder, you can't run this script as main")
else:
    import pyapireference.ui.collapsible_widget_resources
    from pyapireference.extra import get_text_size, create_menu

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
	def __init__(self, text, actions: List[Tuple[str, Callable]]=[("Example", lambda: print("example")), ("Example 1", lambda: print("example 1")), ("Example 2", lambda: print("example 2"))], extra_button_text: str="+", parent=None):
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
			if isinstance(action_callback, dict):
				menu.addMenu(create_menu(action_callback, action_name, parent=self))
				continue

			menu.addAction(action_name, action_callback)

		menu.exec_(QCursor.pos())

if __name__ == "__main__":
	app = QApplication(sys.argv)

	main_window = MainWindow()

	sys.exit(app.exec_())
