"""PyApiReference is a GUI application to generate Python Api References.

About:
	GitHub: https://github.com/Patitotective/PyApiReference
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
			directory=os.path.basename(os.getcwd()), # Get basename of current directory, e.g.: PyApiReference/PyApiReference/main.py -> PyApiReference/PyApiReference
			filter="Python files (*.py)") # Filter Python files

		filename = os.path.basename(filename_with_path) # filename means only the filename without the path, e.g.: PyApiReference/PyApiReference/main.py -> main.py

		# If filename equals empty string means no selected file
		if filename == '':
			return

		# Get spec from file path and load module from spec
		filename_without_extension = os.path.splitext(filename)[0]
		spec = spec_from_file_location(filename_without_extension, filename)
		module = module_from_spec(spec)
		spec.loader.exec_module(module)

		# Get non-built in objects 
		print(inspect_statement(module)) # For now just print members on module

def inspect_object(object, include_dunder_methods=True, dunder_methods_to_include=("__init__")):
	"""Find all members of Python object, if class call itself.

	Errors:
		Right now when inspecting module, class in that module will be create a nested dictionary, ignoring class type.
		Not working with nested functions. (Need to implement a way to show member type on nested dictionaries)
	"""
	result = {}
	module_members = inspect.getmembers(object)

	for member_name, member in module_members:
		# If the member name starts with __ (means dunder method) and the member name is not onto the 
		# dunder_methods_to_include check if include_dunder_methods is True, if it is 
		# Add /ignore (backslash ignore) at the end of the member name 
		# (this way we can identify dunder methods to ignore when showing onto the screen) 
		if member_name.startswith("__") and member_name not in dunder_methods_to_include:
			if not include_dunder_methods:
				continue

			member_base_name = member_name
			member_name += r"\ignore"

		# If the member it's a class call itself to get all members in the class
		# (Need to add same with functions, because of nested functions)
		if inspect.isclass(member):
			if member_base_name == "__class__" or member_base_name == "__base__":
				# If not ignore __class__ and __base__ dunder methods will end on
				# RecursionError: maximum recursion depth exceeded while calling a Python object
				continue
			
			result[member_name] = inspect_object(member)
			continue

		# If the member is not a class
		# Add it to result with name as key and member as value
		result[member_name] = member

	return result


def init_app():
	app = QApplication(sys.argv)
	main_window = MainWindow()

	sys.exit(app.exec_())

class Test:
	def __init__(self):
		self.name = "Test"

	def print_name(self):
		def hello():
			pass
		
		print(self.name)


if __name__ == "__main__":
	print(inspect_object(Test, include_dunder_methods=False)) # Testing inspect_object
	#init_app() # Uncomment this to run the gui
