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
from PyQt5.QtWidgets import (
	QApplication, 
	QMainWindow, 
	QWidget, 
	QLabel, 
	QFileDialog, 
	QPushButton, 
	QGridLayout, 
	QFormLayout, 
	QMessageBox, 
	QVBoxLayout, 
	QMenu, 
	)

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

# Dependencies
from GUI.collapsible_widget import CollapsibleWidget
from GUI.scrollarea import ScrollArea
from GUI.settings_dialog import SettingsDialog

import resources # Qt resources resources.qrc
from inspect_object import inspect_object
from extra import create_qaction, convert_to_code_block, get_module_from_path


class ExportTypes(Enum):
	PREFS = "prefs"
	JSON = "json"
	YAML = "yaml"


class InspectModule(QObject):
	module_content = None
	finished = pyqtSignal()

	def __init__(self, path):
		super().__init__()
		self.path = path

	def run(self):
		module = get_module_from_path(self.path)
		self.module_content = inspect_object(module)
		InspectModule.module_content = self.module_content
		self.finished.emit()


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
		self.setWindowIcon(QIcon(':/icon.png'))

		self.main_widget = MainWidget(parent=self)
		
		self.set_stylesheet()

		self.setCentralWidget(self.main_widget)

	def set_stylesheet(self):
		THEME = self.main_widget.THEME
		current_theme = self.main_widget.current_theme

		self.setStyleSheet(f"""
			QMainWindow, QWidget {{
				background-color: {THEME[current_theme]['background_color']};
				font-family: {THEME['font_family']};
			}}
			QWidget {{
				color: {THEME[current_theme]['font_color']};
			}}
			
			QPushButton {{
				border: none;
				padding: 2px 2px 2px 2px;
				background-color: {THEME[current_theme]['button']['background_color']};
			}}
			QPushButton:hover {{
				background-color: {THEME[current_theme]['button']['background_color_hover']};
			}}
			QPushButton:disabled {{
				background-color: {THEME[current_theme]['button']['background_color_disabled']};
			}}
			
			QMenuBar, QMenu {{
				background-color: {THEME['menubar']['background_color']};
				color: {THEME['menubar']['font_color']};
			}}
			QMenuBar:item {{
				padding: 1px 4px;
				background: transparent;
				border-radius: 4px;
			}}
			QMenu:item {{
				color: {THEME['menubar']['item']['menu_item_font_color']};
			}}
			QMenu::item:selected, QMenuBar::item:selected {{
				background-color: {THEME['menubar']['item']['background_color_selected']};
				color: {THEME['menubar']['item']['menu_item_font_color_selected']};
			}}
		"""
		)

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

		self.widgets = {
			"module_content_scrollarea": [], 
			"load_file_button": [], 
		}

		self.THEME = PREFS.read_prefs_file("GUI/theme.prefs")
		self.module_content = None

		self.init_prefs()
		self.init_window()

	@property	
	def current_theme(self):
		return self.prefs.file["theme"]

	def init_window(self):
		self.setLayout(QGridLayout())

		self.main_frame()

	def init_prefs(self):
		default_prefs = {
			"current_module": "", # The path when you open a file to restore it 
			"theme": "light", 
			"state": {
				"pos": (0, 0), 
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

		pixmap = QPixmap("Images/logo_without_background.png")
		logo.setPixmap(pixmap)

		logo.setStyleSheet("margin-bottom: 10px;")
		logo.setAlignment(Qt.AlignCenter)

		load_file_button = QPushButton("Load file")
		load_file_button.clicked.connect(self.load_file)

		self.widgets["load_file_button"].append(load_file_button)

		self.layout().addWidget(logo, 0, 0, 1, 0, Qt.AlignTop)
		self.layout().addWidget(load_file_button, 1, 0, Qt.AlignTop)
		self.layout().setRowStretch(1, 1)

		if not self.prefs.file["current_module"] == "":
			if not os.path.isfile(self.prefs.file["current_module"]):
				return # Ignore it because is not a valid path

			self.create_inspect_module_thread(self.prefs.file["current_module"])				

	def load_file(self):
		path, file_filter = QFileDialog.getOpenFileName(
			parent=self, 
			caption="Select a file", 
			directory=os.getcwd(), # Get current directory
			filter="Python files (*.py)") # Filter Python files

		# If filename equals empty string means no selected file
		if path == '':
			return

		self.prefs.write_prefs("current_module", path)

		self.create_inspect_module_thread(path)

	def create_inspect_module_thread(self, path):
		# Disable Load File button
		self.widgets["load_file_button"][-1].setEnabled(False)

		loading_label = QLabel("Loading...")
		loading_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		loading_label.setStyleSheet(f"font-size: 20px; font-family: {self.THEME['module_collapsible_font_family']};")

		self.layout().addWidget(loading_label, 2, 0)
		self.layout().setRowStretch(2, 10)

		self.widgets["module_content_scrollarea"].append(loading_label)

		self.thread = QThread()
		self.worker = InspectModule(path)
		self.worker.moveToThread(self.thread)

		# Start: inspect object / Finish: create widget 
		self.thread.started.connect(self.worker.run)
		self.worker.finished.connect(lambda: self.widgets["load_file_button"][-1].setEnabled(True))
		self.worker.finished.connect(self.inspect_module_thread_finished)
		
		# Delete thread and inspect objects
		self.worker.finished.connect(self.thread.quit)
		self.worker.finished.connect(self.worker.deleteLater)
		self.thread.finished.connect(self.thread.deleteLater)
		
		self.thread.start()	

	def inspect_module_thread_finished(self):
		self.module_content = InspectModule.module_content
		self.add_module_content_widget()
		
	def add_module_content_widget(self):
		if len(self.widgets["module_content_scrollarea"]) > 0:	
			self.widgets["module_content_scrollarea"][0].setParent(None)
			self.widgets["module_content_scrollarea"] = []
		
		self.layout().addWidget(self.create_module_content_widget(), 2, 0, 1, 0)
		self.layout().setRowStretch(2, 1)		
		self.layout().setRowStretch(1, 0)

	def create_module_content_widget(self):
		module_content_widget = QWidget()
		module_content_widget.setLayout(QVBoxLayout())
		module_content_widget.setStyleSheet(f"font-family: {self.THEME['module_collapsible_font_family']};")

		module_collapsible = self.create_collapsible_object(self.module_content)
		module_collapsible.uncollapse()

		module_content_widget.layout().addWidget(module_collapsible)
		module_content_widget.layout().addStretch(1)

		module_content_scrollarea = ScrollArea(module_content_widget)

		self.widgets["module_content_scrollarea"].append(module_content_scrollarea)
		return module_content_scrollarea

	def create_collapsible_widget(self, title: str, color=None, parent=None) -> QWidget:
		if parent is None:
			parent = self

		collapsible_widget = CollapsibleWidget(
			self.THEME, 
			self.current_theme, 
			title, 
			color, 
			parent)

		return collapsible_widget

	def create_collapsible_object(self, object_content: dict):
		"""Generates a collapsible widget for a given object_content generated by inspect_object
		"""

		def create_property_collapsible(property_content: dict):
			"""Given a dicionary with {property_name: property_value}, where property_value could be a dictionary or a list
			return a collapsible widget.
			"""			
			property_name = tuple(property_content)[0]
			property_value = property_content[property_name]
			
			if "type" in property_value:
				color = self.find_object_type_color(property_value["type"])
			else:
				color = self.find_object_type_color(property_name)

			property_collapsible = self.create_collapsible_widget(property_name, color)

			if not not not property_value: # Means empty
				return

			if isinstance(property_value, (list, tuple)):
				for nested_property_value in property_value:
					if not not not nested_property_value: # Means emtpy
						continue

					nested_property_label = QLabel(str(nested_property_value))

					property_collapsible.addWidget(nested_property_label)
			
			elif isinstance(property_value, dict):
				for nested_property_name, nested_property_value in property_value.items():
					
					multiple_line_string = "\n" in nested_property_value if isinstance(nested_property_value, str) else ""

					if not not not nested_property_value: # Means empty
						continue

					elif isinstance(nested_property_value, (list, tuple, dict)) or multiple_line_string:
						nested_property_content = {nested_property_name: nested_property_value}
						
						nested_property_collapsible = create_property_collapsible(nested_property_content)
						if nested_property_collapsible is None:
							continue

						property_collapsible.addWidget(nested_property_collapsible)
						continue
					
					nested_property_color = self.find_object_type_color(nested_property_name)
					nested_property_label = QLabel(f"{nested_property_name}: {convert_to_code_block(nested_property_value)}")
					nested_property_label.setStyleSheet(f"color: {nested_property_color};")

					property_collapsible.addWidget(nested_property_label)
		
			elif isinstance(property_value, str):
				property_label = QLabel(convert_to_code_block(property_value))
				property_label.setStyleSheet(f"color {color}")

				property_collapsible.addWidget(property_label)

			return property_collapsible

		def add_object_properties_to_collapsible(object_properties: dict, collapsible: CollapsibleWidget):
			"""Given an dictionary with the object_properties return a widget with properties positioned on labels.
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
				property_label = QLabel(f"{property_name}: {convert_to_code_block(property_value)}")
				property_label.setStyleSheet(f"color: {property_color};")

				collapsible.addWidget(property_label)
		
		object_name = tuple(object_content)[0]
		object_properties = object_content[object_name]

		color = self.find_object_type_color(object_properties["type"])

		collapsible_object = self.create_collapsible_widget(object_name, color)
		add_object_properties_to_collapsible(object_content[object_name], collapsible_object)

		return collapsible_object

	def find_object_type_color(self, object_type: str) -> str:
		for color_object_type in self.prefs.file["colors"]:

			if object_type == color_object_type:
				return self.prefs.file["colors"][color_object_type]
				
		return self.THEME[self.current_theme]["font_color"]


def init_app():
	app = QApplication(sys.argv)
	main_window = MainWindow()

	sys.exit(app.exec_())

if __name__ == "__main__":
	init_app()
