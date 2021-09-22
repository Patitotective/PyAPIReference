import os
from importlib.util import spec_from_file_location, module_from_spec
from PyQt5.QtWidgets import QAction, QDialog, QLabel, QVBoxLayout, QWidget

TAB = "&nbsp;" * 4 

def create_qaction(menu, text: str, shortcut: str="", callback: callable=lambda: print("No callback"), parent=None) -> QAction:
	"""This function will create a QAction and return it"""
	action = QAction(parent) # Create a qaction in the window (self)

	action.setText(text) # Set the text of the QAction 
	action.setShortcut(shortcut) # Set the shortcut of the QAction

	menu.addAction(action) # Add the action to the menu
	
	action.triggered.connect(callback) # Connect callback to callback argument

	return action # Return QAction

def get_module_from_path(path: str):
	"""Given a path of a Python module, returns it. If some exception when executing the module returns None, error
	"""

	filename = os.path.basename(path) # filename means only the filename without the path, e.g.: PyAPIReference/PyAPIReference/main.py -> main.py
	filename_without_extension = os.path.splitext(filename)[0]

	spec = spec_from_file_location(filename_without_extension, path)
	module = module_from_spec(spec)
	
	try:
		spec.loader.exec_module(module)
	except Exception as error:
		return None, error

	return module, None

def convert_to_code_block(string: str, stylesheet: str="background-color: #484848; color: white;") -> str:
	if not isinstance(string, str):
		return convert_to_code_block("None", stylesheet=stylesheet)


	result = f"<span style='{stylesheet}'>"
	result += str(string).replace("\t", TAB).replace("\n", "<br>")
	result += "</span>"

	return result

def stylesheet_to_dict(stylesheet: str) -> dict:
	result = {}
	stylesheet = stylesheet.split(";")
	
	for e, property_value in enumerate(stylesheet):
		if not len((property_value := property_value.split(":"))) == 2:
			continue

		property_, value = property_value
		
		result[property_] = value.strip() 

	return result

def dict_to_stylesheet(stylesheet_dict: dict) -> str:
	result = ""

	for property_, value in stylesheet_dict.items():
		result += f"{property_}: {value};"

	return result

def change_widget_stylesheet(widget: QWidget, property_: str, value: str):
	stylesheet = widget.styleSheet()

	stylesheet = stylesheet_to_dict(stylesheet)
	stylesheet[property_] = value
	stylesheet = dict_to_stylesheet(stylesheet)

	widget.setStyleSheet(stylesheet)

#print(get_module_from_path("trial.py"))
