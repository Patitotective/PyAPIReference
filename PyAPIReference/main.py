"""PyAPIReference is a GUI application to generate Python Api References.

About:
	GitHub: https://github.com/Patitotective/PyAPIReference
	Patitotective:
		Discord: patitotective#0127
		GitHub: https://github.com/Patitotective
	Sharkface:
		Discord: Sharkface#9495
		GitHub: https://github.com/devp4
"""

# Libraries
import inspect
import sys
import os
import time
import json
import yaml
from enum import Enum, auto

import PREFS

# PyQt5
import qdarktheme # Dark theme

from PyQt5.QtWidgets import (
	QApplication, QMainWindow,  
	QWidget, QLabel, 
	QFileDialog, QPushButton, 
	QGridLayout, QFormLayout, 
	QMessageBox, QVBoxLayout, 
	QMenu, QDesktopWidget, 
	QTabWidget, QTextEdit, 
	QShortcut
)

from PyQt5.QtGui import QIcon, QPixmap, QFontDatabase, QFont, QKeySequence, QTextOption
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QFile, QTextStream

# Dependencies
from GUI.collapsible_widget import CollapsibleWidget, CheckBoxCollapseButton, CollapseButton
from GUI.scrollarea import ScrollArea
from GUI.settings_dialog import SettingsDialog
from GUI.markdownhighlighter import MarkdownHighlighter
from GUI.warning_dialog import WarningDialog

import resources # Qt resources resources.qrc
from inspect_object import inspect_object
from extra import create_qaction, convert_to_code_block, get_module_from_path, change_widget_stylesheet, add_text_to_text_edit, get_widgets_from_layout


class ExportTypes(Enum):
	PREFS = "prefs"
	JSON = "json"
	YAML = "yaml"


class InspectModule(QObject):
	finished = pyqtSignal()
	expection_found = pyqtSignal()

	def __init__(self, path):
		super().__init__()
		self.path = path
		self.running = False

	def run(self):
		self.running = True
		module, error = get_module_from_path(self.path)

		if error is not None: # Means exception
			self.exception = error
			self.expection_found.emit()
			self.running = False
			return

		self.module_content = inspect_object(module)

		self.finished.emit()
		self.running = False


class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent=parent)

		print("PyAPIReference started")

		self.init_window()
		self.create_menu_bar()

		self.show()
		self.restore_geometry()

	def init_window(self):
		self.setWindowTitle("PyAPIReference")
		self.setWindowIcon(QIcon(':/Images/icon.png'))

		self.main_widget = MainWidget(parent=self)
		
		#self.set_stylesheet()
		self.setStyleSheet(qdarktheme.load_stylesheet(self.main_widget.current_theme))

		self.setCentralWidget(self.main_widget)

	def create_menu_bar(self):
		"""Create menu bar."""
		bar = self.menuBar() # Get the menu bar of the mainwindow
		
		## File menu ##
		file_menu = bar.addMenu('&File')

		load_file_action = create_qaction(
			menu=file_menu, 
			text="Load file", 
			shortcut="Ctrl+O", 
			callback=self.main_widget.load_file, 
			parent=self)			

		## Export menu ##
		export_menu = file_menu.addMenu("Export tree...")
		
		# Create a export action to export as PREFS
		export_prefs_action = create_qaction(
			menu=export_menu, 
			text="Export as PREFS", 
			#shortcut="Ctrl+P", 
			callback=lambda x: self.export_module_content(ExportTypes.PREFS), 
			parent=self)
		
		# Create a export action to export as JSON
		export_json_action = create_qaction(
			menu=export_menu, 
			text="Export as JSON", 
			#shortcut="Ctrl+J", 
			callback=lambda x: self.export_module_content(ExportTypes.JSON), 
			parent=self)

		# Create a export action to export as YAML
		export_yaml_action = create_qaction(
			menu=export_menu, 
			text="Export as YAML", 
			#shortcut="Ctrl+Y", 
			callback=lambda x: self.export_module_content(ExportTypes.YAML), 
			parent=self)


		# Create a close action that will call self.close_app
		close_action = create_qaction(
			menu=file_menu, 
			text="Close", 
			shortcut="Ctrl+Q", 
			callback=self.close_app, 
			parent=self)

		## Edit menu ##
		edit_menu = bar.addMenu('&Edit') # Add a menu called edit

		# Create a settings action that will open the settings dialog
		settings_action = create_qaction( 
			menu=edit_menu, 
			text="&Settings", 
			shortcut="Ctrl+S", 
			callback=self.open_settings_dialog, 
			parent=self)

		## About menu ##
		about_menu = bar.addMenu('&About') # Add a menu called about

		# Create an about action that will create an instance of AboutDialog
		about_qt_action = create_qaction(
			menu=about_menu, 
			text="About Q&t", 
			shortcut="Ctrl+t", 
			callback=lambda: QMessageBox.aboutQt(self), 
			parent=self)

	def export_module_content(self, file_type) -> None:
		"""Export the object tree as a file"""

		if not self.main_widget.module_content:
			# If user has not loaded a file, display export error
			error_message = QMessageBox.warning(self, f"Export as {file_type.name}", "Nothing to save.")
			return
		
		default_filename = f"{tuple(self.main_widget.module_content)[0]}.{file_type.value}"
		path, file_filter = QFileDialog.getSaveFileName(self, f"Export as {file_type.name}", default_filename, f"{file_type.name} Files (*.{file_type.value})")
		
		if path == '':
			return

		with open(path, "w") as file:
			if file_type == ExportTypes.PREFS:
				file.write(PREFS.convert_to_prefs(self.main_widget.module_content))
			
			elif file_type == ExportTypes.JSON:
				json.dump(self.main_widget.module_content, file, indent=4)
			
			elif file_type == ExportTypes.YAML:
				yaml.dump(self.main_widget.module_content, file)
	
	def open_settings_dialog(self):
		settings_dialog = SettingsDialog(self.main_widget.prefs, parent=self)
		answer = settings_dialog.exec_()

		if answer == 1: # Means apply
			self.reset_app()

	def reset_app(self):
		self.close() # Close
		self.__init__() # Init again

	def restore_geometry(self):
		pos, size = self.main_widget.prefs.file["state"]["pos"], self.main_widget.prefs.file["state"]["size"]
		is_maximized = self.main_widget.prefs.file["state"]["is_maximized"]
		
		if pos == (-100, -100):
			win_rec = self.frameGeometry()
			
			center = QDesktopWidget().availableGeometry().center()
			win_rec.moveCenter(center)
			
			width, height = QDesktopWidget().availableGeometry().width(), QDesktopWidget().availableGeometry().height()
			win_rec_width, win_rec_height = width // 5, height * 1 // 3
			
			self.resize(win_rec_width, win_rec_height)
			self.move(width // 2 - win_rec_width // 2, height // 2 - win_rec_height // 2)

			return

		if is_maximized:
			self.showMaximized()
			return

		self.move(*pos)
		self.resize(*size)

	def save_geometry(self):
		geometry = self.geometry()

		pos = geometry.x(), geometry.y()
		size = geometry.width(), geometry.height()

		self.main_widget.prefs.write_prefs("state/pos", pos)
		self.main_widget.prefs.write_prefs("state/size", size)
		self.main_widget.prefs.write_prefs("state/is_maximized", self.isMaximized())

	def close_app(self):
		self.save_geometry()

		# Close window and exit program to close all dialogs open.
		self.close()

	def closeEvent(self, event) -> None:
		"""This will be called when the windows is closed."""		
		self.close_app()
		event.accept()

		print("Closed PyAPIReference")


class MainWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__()

		self.FONTS = ("UbuntuMono-B.ttf", "UbuntuMono-BI.ttf", "UbuntuMono-R.ttf", "UbuntuMono-RI.ttf")

		self.widgets = {
			"module_tabs": [], 
			"module_content_scrollarea": [], 
			"load_file_button": [], 
			"retry_button": [], 
			"markdown_tab": [], 
			"markdown_text_edit": []
		}

		self.THEME = PREFS.read_prefs_file("GUI/theme.prefs")
		self.module_content = None

		self.load_fonts()
		self.init_prefs()
		self.init_window()

	@property	
	def current_theme(self):
		return self.prefs.file["theme"]

	def load_fonts(self):
		for font in self.FONTS:
			QFontDatabase.addApplicationFont(f':/Fonts/{font}')

	def init_window(self):
		self.setLayout(QGridLayout())

		self.main_frame()

	def init_prefs(self):
		default_prefs = {
			"current_module": "", # The path when you open a file to restore it 
			"theme": "dark", 
			"state": {
				"pos": (-100, -100), 
				"size": (0, 0), 
				"is_maximized": False, 
			},
			"colors": {
				"class": "#b140bf",
				"function": "#ce5c00",
				"parameters": "#4e9a06",
				"int": "#5B82D7",
				"str": "#5B82D7", 
				"tuple": "#5B82D7", 
				"list": "#5B82D7", 
				"dict": "#5B82D7",
			}
		}

		self.prefs = PREFS.PREFS(default_prefs, filename="Prefs/settings.prefs")

	def main_frame(self):
		logo = QLabel()

		pixmap = QPixmap(":/Images/logo_without_background.png")
		logo.setPixmap(pixmap)

		logo.setStyleSheet("margin-bottom: 10px;")
		logo.setAlignment(Qt.AlignCenter)

		load_file_button = QPushButton("Load file")
		load_file_button.clicked.connect(self.load_file)

		self.widgets["load_file_button"].append(load_file_button)

		self.layout().addWidget(logo, 0, 0, 1, 0, Qt.AlignTop)
		self.layout().addWidget(load_file_button, 1, 0, Qt.AlignTop)
		self.layout().setRowStretch(1, 1)

		self.load_last_module()

	def load_file(self):
		path, file_filter = QFileDialog.getOpenFileName(
			parent=self, 
			caption="Select a file", 
			directory=os.getcwd() if self.prefs.file["current_module"] == "" else self.prefs.file["current_module"], # Get current directory
			filter="Python files (*.py)") # Filter Python files

		# If filename equals empty string means no selected file
		if path == '':
			return

		self.prefs.write_prefs("current_module", path)

		self.create_inspect_module_thread(path)

	def load_last_module(self):
		if not self.prefs.file["current_module"] == "":
			if not os.path.isfile(self.prefs.file["current_module"]):
				return # Ignore it because is not a valid path

			self.create_inspect_module_thread(self.prefs.file["current_module"])		

	def create_inspect_module_thread(self, module):
		# Disable Load File button
		self.widgets["load_file_button"][-1].setEnabled(False)

		loading_label = QLabel("Loading...")
		loading_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		loading_label.setStyleSheet(f"font-size: 20px; font-family: {self.THEME['module_collapsible_font_family']};")

		self.layout().addWidget(loading_label, 2, 0)
		self.layout().setRowStretch(2, 100)
		
		if len(self.widgets["retry_button"]) > 0:
			self.widgets["retry_button"][-1].setParent(None)
			self.widgets["retry_button"].pop()

		self.widgets["module_content_scrollarea"].append(loading_label)

		self.thread = QThread()
		self.worker = InspectModule(module)
		self.worker.moveToThread(self.thread)

		# Start: inspect object / Finish: create widget 
		self.thread.started.connect(self.worker.run)	

		# Delete thread and inspect objects
		self.worker.finished.connect(self.inspect_object_worker_finished)
		self.worker.expection_found.connect(self.inspect_object_worker_exception)

		self.thread.start()

	def inspect_object_worker_exception(self):
		self.thread.quit()		
		self.thread.deleteLater()
		self.worker.deleteLater()

		self.widgets["load_file_button"][-1].setEnabled(True)

		exception_message = f"Couldn't load file, exception found: \n{self.worker.exception}"
		change_widget_stylesheet(self.widgets["module_content_scrollarea"][-1], "font-size", "15px")
		self.widgets["module_content_scrollarea"][-1].setText(exception_message)

		retry_button = QPushButton("Retry")
		retry_button.clicked.connect(lambda: self.create_inspect_module_thread(self.prefs.file["current_module"]))

		self.widgets["retry_button"].append(retry_button)

		self.layout().addWidget(retry_button, 3, 0)
		self.layout().setRowStretch(4, 100)

	def inspect_object_worker_finished(self):
		self.thread.quit()
		self.worker.deleteLater()
		self.thread.deleteLater()

		self.layout().setRowStretch(4, 0)

		self.widgets["load_file_button"][-1].setEnabled(True)
		self.module_content = self.worker.module_content

		self.create_module_tabs()
		
	def create_module_tabs(self):
		if len(self.widgets["module_tabs"]) > 0:	
			self.widgets["module_tabs"][-1].setParent(None)
			self.widgets["module_tabs"] = []
		
		if len(self.widgets["module_content_scrollarea"]) > 0:	
			self.widgets["module_content_scrollarea"][-1].setParent(None)
			self.widgets["module_content_scrollarea"] = []

		module_tabs = QTabWidget()

		module_tabs_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), module_tabs)
		module_tabs_shortcut.activated.connect(lambda: module_tabs.setCurrentIndex((module_tabs.currentIndex() + 1) % module_tabs.count()))


		self.layout().addWidget(module_tabs, 2, 0, 1, 0)
		self.layout().setRowStretch(2, 1)		
		self.layout().setRowStretch(1, 0)

		module_tabs.addTab(self.create_module_content_tab(), "Tree")		
		module_tabs.addTab(self.create_markdown_tab(), "Markdown")		

		self.widgets["module_tabs"].append(module_tabs)

	def create_markdown_tab(self):
		def create_markdown_text_edit():
			markdown_text = self.convert_tree_to_markdown(tree=self.filter_tree())

			if len(self.widgets["markdown_text_edit"]) > 0:
				# If markdown_text_edit was already created just update it.
				self.widgets["markdown_text_edit"][-1].setText(markdown_text)
				return

			text_edit = QTextEdit()
			text_edit.setPlainText(markdown_text)
			text_edit.setWordWrapMode(QTextOption.NoWrap)

			highlighter = MarkdownHighlighter(text_edit)

			markdown_tab = self.widgets["markdown_tab"][-1]
			self.widgets["markdown_text_edit"].append(text_edit)

			markdown_tab.layout().addWidget(text_edit, 1, 0)
			markdown_tab.layout().setRowStretch(1, 0)

			return text_edit

		def convert_to_markdown_button_clicked():
			nonlocal convert_to_markdown_clicked

			if not convert_to_markdown_clicked:
				convert_to_markdown_clicked = True
				convert_to_markdown_button.setText("Update Markdown")				
				create_markdown_text_edit()
				return

			warning = WarningDialog("Overwrite text", "Do you want to overwrite current Markdown text?", parent=self).exec_() # Return 1 if yes, 0 if no

			if not warning:
				return

			create_markdown_text_edit()

		convert_to_markdown_clicked = False

		markdown_tab = QWidget()
		markdown_tab.setLayout(QGridLayout())

		convert_to_markdown_button = QPushButton("Convert to Markdown")
		convert_to_markdown_button.clicked.connect(convert_to_markdown_button_clicked)

		markdown_tab.layout().addWidget(convert_to_markdown_button, 0, 0)
		markdown_tab.layout().setRowStretch(1, 1)

		self.widgets["markdown_tab"].append(markdown_tab)

		return markdown_tab

	def convert_tree_to_markdown(self, tree: dict=None):
		def content_to_markdown(content: dict) -> str:
			markdown = ""

			for member_name, member_props in content.items():
				member_type = member_props["type"]
				member_docstring = member_props["docstring"]

				markdown += f"## {member_name} ({member_type})\n"
				markdown += f"{member_docstring if member_docstring is not None else ''}".strip() + "\n\n"

			return markdown

		if tree is None:
			tree = self.module_content

		module_name = tuple(tree)[0]
		module_content = tree[module_name]

		markdown = f"# {module_name}\n"

		for property_name, property_val in module_content.items():
			if isinstance(property_val, dict):
				markdown += content_to_markdown(property_val)

			if property_name == "type":
				continue
			elif property_name == "docstring":
				markdown += f"{property_val if property_val is not None else f'{module_name} has no docstring.'}".strip() + "\n\n"
				continue

		return markdown.strip() + "\n" # This way it only lefts one line at the end

	def filter_tree(self, filter_dict: dict=None, dict_to_filter: dict=None):
		"""Given a filter_dict and a dict_to_filter returns dict_to_filter if keys existed in filter_dict:

		Example:
			print(self.filter_dict(filter_dict={"abc": True}, dict_to_filter={"abc": {"a": 0, "b": 1, "c": 2, "d": 3}, "123: {1: 0, 2: 1}}))

			>>> {"abc": {"a": 0, "b": 1, "c": 2, "d": 3}
		"""
		if filter_dict is None:
			module_content_scrollarea = self.widgets["module_content_scrollarea"][-1]
			module_collapsible = list(get_widgets_from_layout(module_content_scrollarea.main_widget.layout()))[0]

			filter_dict = module_collapsible.tree_to_dict()

		#if not not not filter_dict: # Means empty
			#return dict_to_filter

		if dict_to_filter is None:
			dict_to_filter = self.module_content

		result = {}

		for key, val in dict_to_filter.items():
			if not key in filter_dict or filter_dict[key] == True:
				result[key] = val
				continue

			if filter_dict[key] == False:
				continue

			elif isinstance(val, dict):
				result[key] = self.filter_tree(filter_dict[key], val)		
				continue

		return result

	def create_module_content_tab(self):
		module_content_widget = QWidget()
		module_content_widget.setLayout(QVBoxLayout())
		font = QFont()
		module_content_widget.setStyleSheet(
		f"""
		*{{
			font-family: {self.THEME['module_collapsible_font_family']};
		}}
		QToolTip {{
			font-family: {font.defaultFamily()};
		}}
		""")

		module_collapsible = self.create_collapsible_object(self.module_content, collapse_button=CollapseButton)
		
		module_collapsible.uncollapse()

		module_content_widget.layout().addWidget(module_collapsible)
		module_content_widget.layout().addStretch(1)

		module_content_scrollarea = ScrollArea(module_content_widget)

		self.widgets["module_content_scrollarea"].append(module_content_scrollarea)
		return module_content_scrollarea

	def create_collapsible_widget(self, title: str, color=None, collapse_button=CheckBoxCollapseButton, parent=None) -> QWidget:
		if parent is None:
			parent = self

		collapsible_widget = CollapsibleWidget(
			self.THEME, 
			self.current_theme, 
			title, 
			color, 
			collapse_button, 
			parent)

		return collapsible_widget

	def create_collapsible_object(self, object_content: dict, collapse_button=CheckBoxCollapseButton):
		"""Generates a collapsible widget for a given object_content generated by inspect_object
		"""

		def create_property_collapsible(
			property_content: dict, 
			properties_without_checkbox: (tuple)=("docstring", "inherits"), 
			properties_disabled_by_default: (tuple)=("self"), 
			):
			
			"""Given a dicionary with {property_name: property_value}, where property_value could be a dictionary or a list
			return a collapsible widget.
			"""
			property_name = tuple(property_content)[0]
			property_value = property_content[property_name]
			
			if not not not property_value: # Means empty
				return

			if "type" in property_value and isinstance(property_value, dict):
				color = self.find_object_type_color(property_value["type"])
			else:
				color = self.find_object_type_color(property_name)

			if property_name in properties_without_checkbox:
				property_collapsible = self.create_collapsible_widget(property_name, color, collapse_button=CollapseButton)
			else:
				property_collapsible = self.create_collapsible_widget(property_name, color)

			if property_name in properties_disabled_by_default:
				property_collapsible.disable_checkbox()

			if isinstance(property_value, (list, tuple)):
				for nested_property_value in property_value:
					if not not not nested_property_value: # Means emtpy
						continue

					nested_property_label = QLabel(str(nested_property_value))

					property_collapsible.addWidget(nested_property_label)
			
			elif isinstance(property_value, dict):
				for nested_property_name, nested_property_value in property_value.items():

					if not not not nested_property_value: # Means empty
						continue
					
					multiple_line_string = "\n" in nested_property_value if isinstance(nested_property_value, str) else ""

					if isinstance(nested_property_value, (list, tuple, dict)) or multiple_line_string:
						nested_property_content = {nested_property_name: nested_property_value}
						
						nested_property_collapsible = create_property_collapsible(nested_property_content)
						if nested_property_collapsible is None:
							continue

						property_collapsible.addWidget(nested_property_collapsible)
						continue
					
					nested_property_color = self.find_object_type_color(nested_property_name)
					nested_property_label = QLabel(f"{nested_property_name}: {self.convert_to_code_block(nested_property_value)}")
					nested_property_label.setStyleSheet(f"color: {nested_property_color};")

					property_collapsible.addWidget(nested_property_label)
		
			elif isinstance(property_value, str):
				property_value = property_value.strip()

				property_label = QLabel(self.convert_to_code_block(property_value))
				property_label.setStyleSheet(f"color {color}")

				property_collapsible.addWidget(property_label)

			return property_collapsible

		def add_object_properties_to_collapsible(object_properties: dict, collapsible: CollapsibleWidget):
			"""Given a dictionary with the properties of an object an a collapsible, add widgest to the collapsible representing the properties.
			"""
			for property_name, property_value in object_properties.items():
				multiple_line_string = "\n" in property_value if isinstance(property_value, str) else ""

				if isinstance(property_value, (list, tuple, dict)) or multiple_line_string:
					property_content = {property_name: property_value}

					property_collapsible = create_property_collapsible(property_content)
					
					if property_collapsible is None:
						continue
					
					collapsible.addWidget(property_collapsible)
					continue

				property_color = self.find_object_type_color(property_name)
				property_label = QLabel(f"{property_name}: {self.convert_to_code_block(property_value)}")
				property_label.setStyleSheet(f"color: {property_color};")

				collapsible.addWidget(property_label)
		
		object_name = tuple(object_content)[0]
		object_properties = object_content[object_name]

		color = self.find_object_type_color(object_properties["type"])

		collapsible_object = self.create_collapsible_widget(object_name, color, collapse_button=collapse_button)
		add_object_properties_to_collapsible(object_content[object_name], collapsible_object)

		return collapsible_object

	def find_object_type_color(self, object_type: str) -> str:
		for color_object_type in self.prefs.file["colors"]:

			if object_type == color_object_type:
				return self.prefs.file["colors"][color_object_type]
				
		return self.THEME[self.current_theme]["font_color"]

	def convert_to_code_block(self, string):
		background_color = self.THEME[self.current_theme]["code_block"]["background_color"]
		font_color = self.THEME[self.current_theme]["code_block"]["font_color"]

		return convert_to_code_block(string, stylesheet=f"background-color: {background_color}; color: {font_color};")


def init_app():
	"""Init PyAPIReference application and main window.
	"""
	app = QApplication(sys.argv)
	app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps) # https://github.com/5yutan5/PyQtDarkTheme#usage
	main_window = MainWindow()

	sys.exit(app.exec_())

if __name__ == "__main__":
	init_app()
