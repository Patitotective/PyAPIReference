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
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__()

		self.init_window()

		self.show()

	def init_window(self):
		self.setWindowTitle("PyApiReference")

		self.main_widget = MainWidget(parent=self)
		self.setCentralWidget(self.main_widget)


class MainWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__()

		self.init_window()

	def init_window(self):
		self.setLayout(QGridLayout())

		self.main_frame()

	def main_frame(self):
		logo = QLabel("PyApiReference")
		logo.setStyleSheet("font-size: 20px; font-weight: bold;")
		logo.setAlignment(Qt.AlignCenter | Qt.AlignTop)

		load_file_button = QPushButton("Load file")
		load_file_button.clicked.connect(self.load_file)

		self.layout().addWidget(logo, 0, 0, 1, 0)
		self.layout().addWidget(load_file_button, 1, 0)		

	def load_file(self):
		filename_with_path, file_filter = QFileDialog.getOpenFileName(
			parent=self, 
			caption="Select a file", 
			directory=os.path.basename(os.getcwd()), 
			filter="Python files (*.py)")

		filename = os.path.basename(filename_with_path)

		if filename == '':
			return

		# Get spec from file path and load module from spec
		spec = spec_from_file_location(os.path.splitext(filename)[0], filename)
		module = module_from_spec(spec)
		spec.loader.exec_module(module)

		# Get non-built in objects 
		members = inspect.getmembers(module)
		for member in members:
			if not member[0].startswith("__"):
				member_type = member[1]
				if inspect.isclass(member_type):
					print(f"class {member}")
				elif inspect.isfunction(member_type): 
					print(f"Function {member}")
				else:
					print(f"Unknown {member}")

if __name__ == "__main__":
	app = QApplication(sys.argv)
	main_window = MainWindow()

	sys.exit(app.exec_())
