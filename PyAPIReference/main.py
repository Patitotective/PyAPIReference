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
import os
import sys
import PREFS
from importlib.util import spec_from_file_location, module_from_spec
# PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QFileDialog, QPushButton, QGridLayout, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt

# Dependencies
from inspect_object import inspect_object
from collapsible_widget import CollapsibleWidget
from scrollarea import ScrollArea
from settings_dialog import create_settings_dialog
from extra import create_qaction

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

	def open_settings_dialog(self):
		answer = create_settings_dialog(self.main_widget.prefs, parent=self)

		if answer == 1: # Means apply
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
			directory=os.path.basename(os.getcwd()), # Get basename of current directory, e.g.: PyAPIReference/PyAPIReference/main.py -> PyAPIReference/PyAPIReference
			filter="Python files (*.py)") # Filter Python files

		# If filename equals empty string means no selected file
		if path == '':
			return

		self.module_content = inspect_object(self.get_module_from_path(path))

		if len(self.widgets["module_content_scrollarea"]) > 0:	
			self.widgets["module_content_scrollarea"][0].setParent(None)
			self.widgets["module_content_scrollarea"] = []
		
		self.layout().addWidget(self.create_module_content_widget(self.module_content), 2, 0, Qt.AlignTop)

	def get_module_from_path(self, path: str):
		filename = os.path.basename(path) # filename means only the filename without the path, e.g.: PyAPIReference/PyAPIReference/main.py -> main.py
		filename_without_extension = os.path.splitext(filename)[0]
	
		spec = spec_from_file_location(filename_without_extension, path)
		module = module_from_spec(spec)
		spec.loader.exec_module(module)

		return module

	def create_module_content_widget(self, module_content: dict):
		module_content_widget = QWidget()
		module_content_widget.setLayout(QGridLayout())

		module_collapsible = self.create_collapsible_object(module_content)
		module_collapsible.uncollapse()

		module_content_widget.layout().addWidget(module_collapsible, 0, 0, Qt.AlignTop)

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
		def create_object_properties_widget(object_properties: dict):
			"""Given an dictionary with the object_properties return a widget with properties positioned on labels.
			"""
			object_properties_widget = QWidget()
			object_properties_widget.setLayout(QFormLayout())

			for property_name, property_value in object_properties.items():
				property_content = {property_name: property_value}
				if property_name == "content":
					continue

				elif property_name == "parameters":
					parameters_collapsible = self.create_collapsible_widget(property_name)
					
					for parameter_name, parameter_properties in property_value.items():
					
						parameter_collapsible = self.create_collapsible_widget(parameter_name) 
						for parameter_property_name, parameter_property_value in parameter_properties.items():
							if parameter_property_name == "kind":
								parameter_property_value = parameter_property_value.description # 
							
							parameter_collapsible.addWidget(QLabel(f"{parameter_property_name}: {parameter_property_value}"))

						parameters_collapsible.addWidget(parameter_collapsible)

					object_properties_widget.layout().addRow(parameters_collapsible)	
					continue

				object_properties_widget.layout().addRow(property_name, QLabel(str(property_value)))
		
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
			return 	collapsible_object

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

def hello():
	def bye():
		pass

if __name__ == "__main__":
	#print(inspect.getmembers(hello)) # Testing inspect_object
	init_app() # Uncomment this to run the gui
