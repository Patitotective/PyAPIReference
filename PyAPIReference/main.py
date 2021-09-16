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

import PREFS

# PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QPushButton, QGridLayout, QFormLayout, QMessageBox, QVBoxLayout
from PyQt5.QtCore import Qt

# Dependencies
from inspect_object import inspect_object
from collapsible_widget import CollapsibleWidget
from scrollarea import ScrollArea
from settings_dialog import create_settings_dialog
from extra import create_qaction, get_module_from_path

class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__()

		print("PyAPIReference started")

		self.init_window()
		self.create_menu_bar()

		self.show()

	def init_window(self):
		self.setWindowTitle("PyAPIReference")

		self.main_widget = MainWidget(parent=self)
		
		theme = self.main_widget.theme

		self.setStyleSheet(f"""
			QMainWindow, QWidget {{
				background-color: {theme[self.main_widget.current_theme]['background_color']};
			}}
			QWidget {{
				color: {theme[self.main_widget.current_theme]['font_color']};
			}}
			QPushButton {{
				border: none;
				padding: 2px 2px 2px 2px;
				background-color: {theme[self.main_widget.current_theme]['button']['background_color']};
			}}
			QPushButton:hover {{
				background-color: {theme[self.main_widget.current_theme]['button']['background_color_hover']};			
			}}
			QMenuBar, QMenu {{
				background-color: {theme['menubar']['background_color']};
				color: {theme['menubar']['font_color']};
			}}

			QMenuBar:item {{
				padding: 1px 4px;
				background: transparent;
				border-radius: 4px;
			}}

			QMenu:item {{
				color: {theme['menubar']['item']['menu_item_font_color']};
			}}

			QMenu::item:selected, QMenuBar::item:selected {{
				background-color: {theme['menubar']['item']['background_color_selected']};
				color: {theme['menubar']['item']['menu_item_font_color_selected']};
			}}
		"""
		)

		self.setCentralWidget(self.main_widget)

	def create_menu_bar(self):
		"""Create menu bar."""
		bar = self.menuBar() # Get the menu bar of the mainwindow
		
		## File menu ##
		file_menu = bar.addMenu('&File')

		# Create a export action to export as json
		json_action = create_qaction(
			menu=file_menu, 
			text="Export as JSON", 
			shortcut="Ctrl+J", 
			callback=self.export_as_json, 
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

	def export_as_json(self) -> None:
		"""Export the object tree as a json file"""

		if not self.main_widget.module_content:
			# If user has not loaded a file, display export error
			error_message = QMessageBox.warning(self, "Export as JSON", "Nothing to save.")
			return
		
		default_filename = f"{tuple(self.main_widget.module_content)[0]}.json"
		path, file_filter = QFileDialog.getSaveFileName(self, "Export as JSON", default_filename, "JSON Files (*.json)")
		if path == '':
			return

		with open(path, "w") as file:
			json.dump(self.main_widget.module_content, file, indent=4)

	def open_settings_dialog(self):
		answer = create_settings_dialog(self.main_widget.prefs, parent=self)

		if answer == 1: # Means apply
			self.reset_app()

	def reset_app(self):
		self.close() # Close
		self.__init__() # Init again

	def close_app(self):
		print("Closed PyAPIReference")

		# Close window and exit program to close all dialogs open.
		self.close()

	def closeEvent(self, event) -> None:
		"""This will be called when the windows is closed."""
		self.close_app()
		event.accept()


class MainWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__()

		self.widgets = {
			"module_content_scrollarea": [], 
		}

		self.theme = PREFS.read_prefs_file("theme")
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
			"current_module": {}, 
			"theme": "light", 
		}

		self.prefs = PREFS.PREFS(default_prefs, filename="Prefs/prefs")

	def main_frame(self):
		logo = QLabel("PyAPIReference")
		logo.setStyleSheet("font-size: 20px; font-weight: bold;")
		logo.setAlignment(Qt.AlignCenter)

		load_file_button = QPushButton("Load file")
		load_file_button.clicked.connect(self.load_file)

		self.layout().addWidget(logo, 0, 0, 1, 0, Qt.AlignTop)
		self.layout().addWidget(load_file_button, 1, 0, Qt.AlignTop)
		self.layout().setRowStretch(1, 1)

	def load_file(self):
		path, file_filter = QFileDialog.getOpenFileName(
			parent=self, 
			caption="Select a file", 
			directory=os.getcwd(), # Get current directory
			filter="Python files (*.py)") # Filter Python files

		# If filename equals empty string means no selected file
		if path == '':
			return

		module = get_module_from_path(path)
		self.module_content = inspect_object(module)
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

		module_collapsible = self.create_collapsible_object(self.module_content)
		module_collapsible.uncollapse()

		module_content_widget.layout().addWidget(module_collapsible)
		module_content_widget.layout().addStretch(1)

		module_content_scrollarea = ScrollArea(module_content_widget)

		self.widgets["module_content_scrollarea"].append(module_content_scrollarea)
		return module_content_scrollarea

	def create_collapsible_widget(self, title: str) -> QWidget:
		collapsible_widget = CollapsibleWidget(
			title, 
			collapse_button_hover_background_color=self.theme[self.current_theme]["collapsible"]["background_color_hover"], 
			collapse_button_background_color=self.theme[self.current_theme]["background_color"])

		return collapsible_widget

	def create_collapsible_object(self, object_content: dict):
		"""Generates a collapsible widget for a given object_content generated by inspect_object
		"""

		def create_propety_collapsible(property_content: dict):
			"""Given a dicionary with {property_name: property_value}, where property_value could be a dictionary or a list
			return a collapsible widget.
			"""		
			property_name = tuple(property_content)[0]
			property_value = property_content[property_name]
			property_collapsible = self.create_collapsible_widget(property_name)

			if isinstance(property_value, list):
				for nested_property_value in property_value:
					property_collapsible.addWidget(QLabel(str(nested_property_value)))
			
			elif isinstance(property_value, dict):
				for nested_property_name, nested_property_value in property_value.items():
					if isinstance(nested_property_value, dict):
						nested_property_content = {nested_property_name: nested_property_value}
						property_collapsible.addWidget(create_propety_collapsible(nested_property_content))
						continue
					
					property_collapsible.addWidget(QLabel(f"{nested_property_name}: {nested_property_value}"))
		
			return property_collapsible

		def create_object_properties_widget(object_properties: dict):
			"""Given an dictionary with the object_properties return a widget with properties positioned on labels.
			"""
			object_properties_widget = QWidget()
			object_properties_widget.setLayout(QFormLayout())

			for property_name, property_value in object_properties.items():
				if property_name == "content":
					continue

				elif property_name == "parameters" or property_name == "inherits":
					property_content = {property_name: property_value}

					property_collapsible = create_propety_collapsible(property_content)
					object_properties_widget.layout().addRow(property_collapsible)
					continue

				object_properties_widget.layout().addRow(QLabel(f"{property_name}: {property_value}"))
		
			return object_properties_widget

		object_name = tuple(object_content)[0]
		object_properties = object_content[object_name]

		collapsible_object = self.create_collapsible_widget(object_name)
		collapsible_object.addWidget(create_object_properties_widget(object_content[object_name]))

		if "content" in object_properties:
			property_name = "content"
		elif "parameters" in object_properties:
			property_name = "parameters"		
		else:
			print(f"Not valid object {object_name} with {object_properties} properties")
			return collapsible_object

		for member_name, member_properties in object_content[object_name][property_name].items():
			member_content = {member_name: member_properties}
			
			if "content" in member_properties or "parameters" in member_properties:
				collapsible_object.addWidget(self.create_collapsible_object(member_content))
				continue

		return collapsible_object

def init_app():
	app = QApplication(sys.argv)
	main_window = MainWindow()

	sys.exit(app.exec_())

if __name__ == "__main__":
	init_app()
