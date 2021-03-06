import os
import sys
import inspect
import traceback
import builtins
import types
from importlib.util import spec_from_file_location, module_from_spec

from PyQt5.QtWidgets import QAction, QDialog, QLabel, QVBoxLayout, QWidget, QTextEdit, QLayout, QMenu
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import QSize

HTML_SPACE = "&nbsp;"
HTML_TAB = HTML_SPACE * 4 

def create_menu(menu_dict: dict, menu_name: str="", parent=None) -> QMenu:
	menu = QMenu(menu_name, parent=parent)

	for action_name, action_props in menu_dict.items():
		if action_name[-1] == ">":
			menu.addMenu(create_menu(action_props, action_name[:-1], parent=parent))
			continue

		action = menu.addAction(action_name)
		action.setParent(parent)

		if "callback" in action_props:
			action.triggered.connect(action_props["callback"])
		if "shortcut" in action_props:
			action.setShortcut(action_props["shortcut"])

	return menu

def get_text_size(text: str):
	font = QFont()
	font = QFont(font.defaultFamily())
	font_metrics = QFontMetrics(font)

	return QSize(font_metrics.width(text), font_metrics.height())

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
		return None, traceback.format_exc()

	return module, None

def convert_to_code_block(string: str, stylesheet: str="background-color: #484848; color: white;") -> str:
	if not isinstance(string, str):
		return convert_to_code_block("None", stylesheet=stylesheet)


	result = f"<span style='{stylesheet}'>"
	result += str(string).replace("\t", HTML_TAB).replace("\n", "<br>")
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

def change_widget_stylesheet(widget: QWidget, property_: str, value: str) -> None:
	stylesheet = widget.styleSheet()

	stylesheet = stylesheet_to_dict(stylesheet)
	stylesheet[property_] = value
	stylesheet = dict_to_stylesheet(stylesheet)

	widget.setStyleSheet(stylesheet)

def add_text_to_text_edit(text_edit: QTextEdit, text: str) -> None:
	current_text = text_edit.toPlainText()
	new_text = current_text + text

	text_edit.setPlainText(new_text)

def get_widgets_from_layout(layout: QLayout, widget_type: QWidget=QWidget, exact_type: bool=False) -> iter:
    for indx in range(layout.count()):
        widget = layout.itemAt(indx).widget()
        
        if not isinstance(widget, widget_type) and not exact_type:
            continue
        elif not type(widget) is widget_type and exact_type:
            continue

        yield widget

def interpret_type(type_string: str):
    if type_string.startswith("types."):
        return getattr(types, type_string.removeprefix("types."))

    return getattr(builtins, type_string)

def remove_key_from_dict(my_dict: dict, key: str) -> dict:
	return {k:v for k, v in my_dict.items() if k != key}

def to_sentence_case(string: str) -> str:
	return string.replace("-", " ").replace("_", " ").capitalize()
