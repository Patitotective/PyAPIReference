"""PyApiReference is a GUI application to generate Python Api References.

About:
	Patitotective:
		Discord: patitotective#0127
		GitHub: https://github.com/Patitotective
	Sharkface:
		Discord: Sharkface#9495
		GitHub: https://github.com/devp4

"""

# Libraries
import inspect
import os
import sys
import PREFS
from importlib.util import spec_from_file_location, module_from_spec
# PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QPushButton, QGridLayout

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__()

		self.init_window()

	def init_window(self):
		self.setWindowTitle("PyApiReference")

		self.main_widget = MainWidget(parent=self)
		self.setCentralWidget(self.main_widget)


class MainWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__()

		self.init_window()

		self.show()

	def init_window(self):
		self.setLayout(QGridLayout())

		self.load_file()

	def load_file(self):
		filename_with_path, file_filter = QFileDialog.getOpenFileName(
			parent=self, 
			caption="Select a file", 
			directory=os.path.basename(os.getcwd()), 
			filter="Python files (*.py)")

		filename = os.path.basename(filename_with_path)

		# Get spec from file path and load module from spec
		spec = spec_from_file_location(os.path.splitext(filename)[0], filename)
		module = module_from_spec(spec)
		spec.loader.exec_module(module)

		# Get non-built in objects 
		members = inspect.getmembers(module)
		for member in members:
			if not member[0].startswith("__"):
				print(member)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	main_window = MainWindow()

	sys.exit(app.exec_())
