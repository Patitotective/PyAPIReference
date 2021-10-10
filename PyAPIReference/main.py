"""PyAPIReference is a GUI application to generate Python Api References.
https://patitotective.github.io/PyAPIReference/.
"""

# Libraries
import inspect
import sys
import os
import types
import time
import traceback
import grip
import json
import yaml
import webbrowser
from enum import Enum, auto
import multiprocessing

import PREFS
import markdown # Markdown to HTML converter
import m2r2 # Markdown to ReStructuredText converter

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
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QFile, QTextStream, QTimer
from PyQt5.QtMultimedia import QMediaPlayer

# Dependencies
from GUI.collapsible_widget import CollapsibleWidget, CheckBoxCollapseButton, CollapseButton
from GUI.scrollarea import ScrollArea
from GUI.settings_dialog import SettingsDialog
from GUI.markdownhighlighter import MarkdownHighlighter
from GUI.warning_dialog import WarningDialog
from GUI.button_with_extra_options import ButtonWithExtraOptions
from GUI.filter_dialog import FilterDialog

import resources # Qt resources resources.qrc
from inspect_object import inspect_object
from extra import (
	create_qaction, convert_to_code_block, 
	get_module_from_path, change_widget_stylesheet, 
	add_text_to_text_edit, get_widgets_from_layout, 
	HTML_TAB, interpret_type
)

from tree_to_markdown import convert_tree_to_markdown

THEME = PREFS.read_prefs_file("GUI/theme.prefs")


class TreeExportTypes(Enum):
	PREFS = ("PREFS", "prefs")
	JSON = ("JSON", "json")
	YAML = ("YAML", "yaml")


class MarkdownExportTypes(Enum):
	MARKDOWN = ("Markdown", "md")
	HTML = ("HTML", "html")
	RESTRUCTUREDTEXT = ("ReStructuredText", "rst")


class InspectModule(QObject):
	finished = pyqtSignal()
	expection_found = pyqtSignal()

	def __init__(self, path, prefs):
		super().__init__()
		self.path = path
		self.prefs = prefs
		self.running = False

	def get_filter(self):
		exclude_types = []
		kwargs = {}

		for filter_name, (filter_type, filter_checked) in self.prefs.file["filter"].items():
			if filter_type[0] == "#":
				kwargs[filter_type[1:]] = filter_checked
				continue

			if not filter_checked:
				exclude_types.append(interpret_type(filter_type))

		return tuple(exclude_types), kwargs

	def run(self):
		self.running = True
		module, error = get_module_from_path(self.path)

		if module is None: # Means exception
			error = error.replace('\n', '<br>').replace('    ', HTML_TAB)		

			self.exception_message = f"Couldn't load file. Exception found: <br>{self.convert_to_code_block(error)}" 
			self.expection_found.emit()
			self.running = False
		else:
			try:
				exclude_types, kwargs = self.get_filter()

				kwargs["recursion_limit"] = self.prefs.file["inspect"]["recursion_limit"]["value"]

				self.module_content = inspect_object(module, exclude_types=exclude_types, **kwargs)
			except BaseException as error:
				error = traceback.format_exc().replace('\n', '<br>').replace('\t', HTML_TAB).replace("  ", HTML_TAB[0] * 2).replace("   ", HTML_TAB[0] * 3)

				self.exception_message = f"""An unexpected error ocurred: <br>
				{self.convert_to_code_block(error)}<br>
				"""

				if isinstance(error, RecursionError): self.exception_message += "Try changing the <b>Recursion limit</b> on settings.<br>"
				self.exception_message += f"If you think it is and issue, please report it at <a style='color: {THEME[self.prefs.file['theme']]['link_color']};' href='https://github.com/Patitotective/PyAPIReference/issues'>GitHub issues</a>."

				self.expection_found.emit()
				self.running = False
			else:
				self.finished.emit()
				self.running = False

	def convert_to_code_block(self, string):
		background_color = THEME[self.prefs.file['theme']]["code_block"]["background_color"]
		font_color = THEME[self.prefs.file['theme']]["code_block"]["font_color"]

		return convert_to_code_block(string, stylesheet=f"background-color: {background_color}; color: {font_color};")


class PreviewMarkdownInBrowser(QObject):	
	adress_already_in_use_signal = pyqtSignal()
	def __init__(self, *args, **kwargs):
		super().__init__()

		self.args = args
		self.kwargs = kwargs
		self.app = None
		self.hyperlink = None
		self.server = None

	def init_app(self):
		try:
			self.app.run(open_browser=True)
		except OSError: # Means address already in use
			self.adress_already_in_use_signal.emit()

	def run(self):
		self.app = grip.create_app(*self.args, **self.kwargs)

		self.hyperlink = f"{self.app.config['HOST']}:{self.app.config['PORT']}"

		self.server = multiprocessing.Process(target=self.init_app)
		self.server.start()

	def stop(self):
		self.server.terminate()
		self.server.join()


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
			text="Load module", 
			shortcut="Ctrl+O", 
			callback=lambda: self.main_widget.load_module_file() if self.main_widget.widgets["load_file_button"][-1].isEnabled() else QMessageBox.critical(self, "Cannot load file", "There is a file already loading, wait for it to load another."), 
			parent=self)			

		## Export tree menu ##
		export_tree_menu = file_menu.addMenu("Export tree...")
		
		# Create a export action to export as PREFS
		export_prefs_action = create_qaction(
			menu=export_tree_menu, 
			text="Export as PREFS", 
			#shortcut="Ctrl+P", 
			callback=lambda x: self.main_widget.export_module_content(TreeExportTypes.PREFS), 
			parent=self)
		
		# Create a export action to export as JSON
		export_json_action = create_qaction(
			menu=export_tree_menu, 
			text="Export as JSON", 
			#shortcut="Ctrl+J", 
			callback=lambda x: self.main_widget.export_module_content(TreeExportTypes.JSON), 
			parent=self)

		# Create a export action to export as YAML
		export_yaml_action = create_qaction(
			menu=export_tree_menu, 
			text="Export as YAML", 
			#shortcut="Ctrl+Y", 
			callback=lambda x: self.main_widget.export_module_content(TreeExportTypes.YAML), 
			parent=self)


		## Export markdown menu ##
		export_markdown_menu = file_menu.addMenu("Export markdown...")
		
		# Create a export action to export as PREFS
		export_markdown_action = create_qaction(
			menu=export_markdown_menu, 
			text="Export as Markdown", 
			#shortcut="Ctrl+P", 
			callback=lambda x: self.main_widget.export_markdown(MarkdownExportTypes.MARKDOWN), 
			parent=self)
		
		# Create a export action to export as JSON
		export_html_action = create_qaction(
			menu=export_markdown_menu, 
			text="Export as HTML", 
			#shortcut="Ctrl+J", 
			callback=lambda x: self.main_widget.export_markdown(MarkdownExportTypes.HTML), 
			parent=self)

		# Create a export action to export as YAML
		export_restructuredtext_action = create_qaction(
			menu=export_markdown_menu, 
			text="Export as ReStructuredText", 
			callback=lambda x: self.main_widget.export_markdown(MarkdownExportTypes.RESTRUCTUREDTEXT), 
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

		# Filer tree action
		filter_tree_action = create_qaction(
			menu=edit_menu, 
			text="&Filter tree", 
			shortcut="Ctrl+F", 
			callback=self.main_widget.create_filter_dialog, 
			parent=self)

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
		settings_dialog = SettingsDialog(self.main_widget.prefs, parent=self)
		answer = settings_dialog.exec_()

		if answer == 1: # Means apply
			self.main_widget.prefs.write_prefs("current_module", {})
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
			win_rec_width, win_rec_height = width // 4, height - 350
			
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
		if self.main_widget.save_tree_at_end:
			self.main_widget.prefs.write_prefs("current_module", self.main_widget.get_tree())
		
			# self.main_widget.prefs.write_prefs("current_module", self.main_widget.get_tree()) # Save the state of the tree to restore it later

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

		self.module_content = None
		self.markdown_preview_worker = None
		self.markdown_preview_thread = None
		self.save_tree_at_end = True
		self.DEFAULT_MARKDOWN_FILENAME = "Prefs/temp.md"

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
			"current_module_path": "", # The path when you open a file to restore it 
			"current_module": {}, 
			"current_tab": 0, 
			"theme": "dark", 
			"state": {
				"pos": (-100, -100), 
				"size": (0, 0), 
				"is_maximized": False, 
			}, 
			"inspect": {
				"recursion_limit": {
					"tooltip": "Recursion limit when inspecting module (when large modules it should be bigger).", 
					"value": 10 ** 6, 
					"min_val": 1500, 
				}, 
			}, 
			"colors": {
				"Modules": ("types.ModuleType", "#4e9a06"),			
				"Classes": ("type", "#b140bf"),
				"Functions": ("types.FunctionType", "#ce5c00"),
				"Strings": ("str", "#5B82D7"), 
			}, 
			"filter": {
				"Modules": ('types.ModuleType', False), 
				"Classes": ('type', True), 
				"Functions": ('types.FunctionType', True), 
				"Include imported members": ("#include_imported_members", True), 
			}
		}

		self.prefs = PREFS.PREFS(default_prefs, filename="Prefs/settings.prefs")

	def main_frame(self):
		logo = QLabel()

		pixmap = QPixmap(":/Images/logo_without_background.png")
		logo.setPixmap(pixmap)

		logo.setStyleSheet("margin-bottom: 10px;")
		logo.setAlignment(Qt.AlignCenter)

		load_file_button = ButtonWithExtraOptions("Load module", parent=self, 
			actions=[
				("Reload module", self.load_last_module), 
				("Unload module", self.unload_file), 
				("Filter", self.create_filter_dialog)
			]
		)
		
		load_file_button.main_button.clicked.connect(self.load_module_file)

		self.widgets["load_file_button"].append(load_file_button)

		self.layout().addWidget(logo, 0, 0, 1, 0, Qt.AlignTop)
		self.layout().addWidget(load_file_button, 1, 0, Qt.AlignTop)
		self.layout().setRowStretch(1, 1)

		self.restore_module()

	def restore_module(self):
		"""Restore tree if tree available else load last module.
		"""
		self.timer = QTimer()
		
		if os.path.isfile(self.prefs.file["current_module_path"]): # Means the path really exist
			self.timer.timeout.connect(lambda: self.load_last_module(warning=False))	
		elif not self.prefs.file["current_module"] == {}: # Means it's not empty
			self.timer.timeout.connect(self.restore_tree)
		else:
			return
		
		# Disable Load File button
		self.widgets["load_file_button"][-1].setEnabled(False)

		loading_label = QLabel("Loading...")
		loading_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		loading_label.setStyleSheet(f"font-size: 20px; font-family: {THEME['module_collapsible_font_family']};")

		self.widgets["module_content_scrollarea"].append(loading_label)

		self.layout().addWidget(loading_label, 2, 0)
		self.layout().setRowStretch(2, 100)
		
		self.timer.timeout.connect(lambda: self.widgets["load_file_button"][-1].setEnabled(True))
		self.timer.timeout.connect(self.timer.stop)		
		self.timer.start(100)

	def load_file(self, file_filter, caption="Select a file", directory=None):
		if directory is None:
			directory = self.prefs.file["current_module_path"]

		path, _ = QFileDialog.getOpenFileName(
			parent=self, 
			caption=caption, 
			directory=directory, # Get current directory
			filter=file_filter) # Filter Python files

		return path

	def unload_file(self):
		if self.prefs.file["current_module_path"] == "":
			QMessageBox.warning(self, "No module to unload", "You must load a module first to unload it.")
			return

		if os.path.isfile(self.DEFAULT_MARKDOWN_FILENAME):
			warning = WarningDialog(
				"Lose Markdown", 
				"If you unload this module, this module's Markdown will get lost.\nExport it if you want to preserve it.", 
				no_btn_text="Cancel", 
				yes_btn_text="Continue", 
				parent=self).exec_()
			
			if not warning:
				return

		if len(self.widgets["module_tabs"]) > 0:
			self.widgets["module_tabs"][-1].setParent(None)
			self.widgets["module_tabs"] = []

		if len(self.widgets["module_content_scrollarea"]) > 0:	
			self.widgets["module_content_scrollarea"][-1].setParent(None)
			self.widgets["module_content_scrollarea"] = []
		
		os.remove(self.DEFAULT_MARKDOWN_FILENAME)
		self.prefs.write_prefs("current_module_path", "")
		self.prefs.write_prefs("current_module", {})

	def load_module_file(self):
		if os.path.isfile(self.DEFAULT_MARKDOWN_FILENAME):
			warning = WarningDialog(
				"Lose Markdown", 
				"If you load another file this file's Markdown will get lost.\nExport it if you want to preserve it.", 
				no_btn_text="Cancel", 
				yes_btn_text="Continue", 
				parent=self).exec_()
			
			if not warning:
				return

			os.remove(self.DEFAULT_MARKDOWN_FILENAME)

		if self.markdown_preview_worker is not None:
			self.markdown_preview_worker.stop()
			self.markdown_preview_thread.quit()
			self.markdown_preview_worker.deleteLater()
			self.markdown_preview_thread.deleteLater()

			self.markdown_preview_worker = None
			self.markdown_preview_thread = None

		path = self.load_file("Python files (*.py)")
		
		if path == '':
			return

		file_size = os.path.getsize(path)
		
		if file_size > 15000:
			warning = WarningDialog(
				"Inspect Markdown", 
				"File size is large.\nInspection may take some time.", 
				no_btn_text="Cancel", 
				yes_btn_text="Continue", 
				parent=self).exec_()
			
			if not warning:
				return

		self.prefs.write_prefs("current_module_path", path)

		self.create_inspect_module_thread(path)

	def load_last_module(self, warning: bool=True):
		if self.prefs.file["current_module_path"] == "" and warning:
			QMessageBox.warning(self, "No module to reload", "You must load a module first to reload it.")
			return

		if not self.prefs.file["current_module_path"] == "":
			if not os.path.isfile(self.prefs.file["current_module_path"]):
				return # Ignore it because is not a valid path

			self.create_inspect_module_thread(self.prefs.file["current_module_path"])		

	def create_inspect_module_thread(self, module):
		# Disable Load File button
		self.widgets["load_file_button"][-1].setEnabled(False)

		loading_label = QLabel("Loading...")
		loading_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		loading_label.setStyleSheet(f"font-size: 20px; font-family: {THEME['module_collapsible_font_family']};")

		self.save_tree_at_end = False

		if len(self.widgets["module_content_scrollarea"]) > 0:
			self.widgets["module_content_scrollarea"][-1].setParent(None)
			self.widgets["module_content_scrollarea"].pop()

		self.widgets["module_content_scrollarea"].append(loading_label)

		self.layout().addWidget(loading_label, 2, 0)
		self.layout().setRowStretch(2, 100)
		
		if len(self.widgets["retry_button"]) > 0:
			self.widgets["retry_button"][-1].setParent(None)
			self.widgets["retry_button"].pop()

		self.thread = QThread()
		self.worker = InspectModule(module, self.prefs)
		self.worker.moveToThread(self.thread)

		# Start: inspect object / Finish: create widget 
		self.thread.started.connect(self.worker.run)	

		# Delete thread and inspect objects
		self.worker.finished.connect(self.inspect_object_worker_finished)
		self.worker.expection_found.connect(self.inspect_object_worker_exception)

		self.timer = QTimer()
		self.timer.timeout.connect(self.thread.start)
		self.timer.timeout.connect(self.timer.stop)
		self.timer.start(100)

	def inspect_object_worker_exception(self):
		self.thread.quit()
		self.worker.deleteLater()		
		self.thread.deleteLater()

		self.widgets["load_file_button"][-1].setEnabled(True)

		self.save_tree_at_end = False
		self.prefs.write_prefs("current_module", {})

		change_widget_stylesheet(self.widgets["module_content_scrollarea"][-1], "font-size", "15px")
		
		self.widgets["module_content_scrollarea"][-1].setOpenExternalLinks(True)
		self.widgets["module_content_scrollarea"][-1].setTextFormat(Qt.TextFormat.RichText)		
		self.widgets["module_content_scrollarea"][-1].setText(self.worker.exception_message)

		retry_button = QPushButton("Retry")
		retry_button.clicked.connect(lambda: self.create_inspect_module_thread(self.prefs.file["current_module_path"]))

		self.widgets["retry_button"].append(retry_button)

		self.layout().addWidget(retry_button, 3, 0)

		self.layout().setRowStretch(2, 0)
		self.layout().setRowStretch(3, 0)
		self.layout().setRowStretch(4, 100)

	def inspect_object_worker_finished(self):
		self.thread.quit()
		self.worker.deleteLater()
		self.thread.deleteLater()

		self.layout().setRowStretch(4, 0)

		self.save_tree_at_end = True

		self.widgets["load_file_button"][-1].setEnabled(True)
		self.module_content = self.worker.module_content

		self.create_module_tabs()
		
	def create_module_tabs(self):
		def tab_changed(index: int):
			nonlocal first_time

			if first_time:
				first_time = False
				return

			self.prefs.write_prefs("current_tab", index)

		if len(self.widgets["module_tabs"]) > 0:	
			self.widgets["module_tabs"][-1].setParent(None)
			self.widgets["module_tabs"] = []
			self.widgets["markdown_text_edit"] = []
		
		if len(self.widgets["module_content_scrollarea"]) > 0:	
			self.widgets["module_content_scrollarea"][-1].setParent(None)
			self.widgets["module_content_scrollarea"] = []

		first_time = True

		module_tabs = QTabWidget()
		module_tabs.currentChanged.connect(tab_changed)

		module_tabs_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), module_tabs)
		module_tabs_shortcut.activated.connect(lambda: module_tabs.setCurrentIndex((module_tabs.currentIndex() + 1) % module_tabs.count()))

		self.layout().addWidget(module_tabs, 2, 0, 1, 0)
		self.layout().setRowStretch(2, 1)		
		self.layout().setRowStretch(1, 0)

		module_tabs.addTab(self.create_tree_tab(), "Tree")		
		module_tabs.addTab(self.create_markdown_tab(), "Markdown")		

		module_tabs.setCurrentIndex(self.prefs.file["current_tab"])

		self.widgets["module_tabs"].append(module_tabs)

	def create_markdown_tab(self):
		def update_markdown_file():
			if len(self.widgets["markdown_text_edit"]) < 1:
				return

			with open(self.DEFAULT_MARKDOWN_FILENAME, "w+") as file:
				file.write(self.widgets["markdown_text_edit"][-1].toPlainText())

		def create_markdown_text_edit(text: str=None):
			if text is None:
				markdown_text = convert_tree_to_markdown(tree=self.filter_tree())
			else:
				markdown_text = text

			if len(self.widgets["markdown_text_edit"]) > 0:
				# If markdown_text_edit was already created just update it.
				self.widgets["markdown_text_edit"][-1].setText(markdown_text)
				return

			text_edit = QTextEdit()
			text_edit.textChanged.connect(update_markdown_file)
			text_edit.setPlainText(markdown_text)
			text_edit.setWordWrapMode(QTextOption.NoWrap)
			text_edit.setStyleSheet(f"background-color: {THEME[self.current_theme]['markdown_highlighter']['background-color']};")


			highlighter = MarkdownHighlighter(text_edit, current_theme=self.current_theme)

			markdown_tab = self.widgets["markdown_tab"][-1]
			self.widgets["markdown_text_edit"].append(text_edit)

			markdown_tab.layout().addWidget(text_edit, 1, 0)
			markdown_tab.layout().setRowStretch(1, 0)

			return text_edit

		def convert_to_markdown_button_clicked(ignore=None, text: str=None):
			nonlocal convert_to_markdown_clicked

			if not convert_to_markdown_clicked:
				convert_to_markdown_clicked = True
				convert_to_markdown_button.main_button.setText("Update Markdown")				
				create_markdown_text_edit(text)
				update_markdown_file()

				return

			warning = WarningDialog("Overwrite Markdown", "Do you want to overwrite current Markdown text?", parent=self).exec_() # Return 1 if yes, 0 if no

			if not warning:
				return

			create_markdown_text_edit()

		def load_markdown_file():
			path = self.load_file("Markdown files (*.md)", directory="") # If directory not empty, filter doesn't work
			
			if path == "":
				return

			with open(path, "r") as file:
				content = file.read()

			convert_to_markdown_clicked(text=content)

		def stop_markdown_preview():
			self.markdown_preview_worker.stop()
			self.markdown_preview_thread.quit()
			self.markdown_preview_worker.deleteLater()
			self.markdown_preview_thread.deleteLater()

			self.markdown_preview_worker = None
			self.markdown_preview_thread = None

		def preview_markdown_in_browser():
			def addres_already_in_use():
				answer = WarningDialog(
					"Preview Markdown already live", 
					f"You are already previewing the Markdown at {self.markdown_preview_worker.hyperlink}.", 
					yes_btn_text="Open", 
					yes_btn_callback=2, 
					no_btn_text="Stop", 
					no_btn_callback=1, 
					parent=self
				).exec_()
				
				if answer == 2: # Means open
					webbrowser.open_new_tab(self.markdown_preview_worker.hyperlink)
				elif answer == 1: # Means stop
					stop_markdown_preview()

			if len(self.widgets["markdown_text_edit"]) < 1:
				QMessageBox.critical(self, "No markdown to preview", "You must create a markdown first to preview.")
				return

			if self.markdown_preview_thread is not None and self.markdown_preview_worker is not None:
				addres_already_in_use()
				return

			self.markdown_preview_thread = QThread()
			self.markdown_preview_worker = PreviewMarkdownInBrowser(path=self.DEFAULT_MARKDOWN_FILENAME, title=tuple(self.module_content)[0])
			self.markdown_preview_worker.moveToThread(self.markdown_preview_thread)

			self.markdown_preview_worker.adress_already_in_use_signal.connect(addres_already_in_use)

			self.markdown_preview_thread.started.connect(self.markdown_preview_worker.run)	

			self.markdown_preview_thread.start()

		if len(self.widgets["markdown_text_edit"]) > 0:
			self.widgets["markdown_text_edit"][-1].setParent(None)
			self.widgets["markdown_text_edit"].pop()

		self.markdown_preview_thread = None
		self.markdown_preview_worker = None

		convert_to_markdown_clicked = False

		markdown_tab = QWidget()
		markdown_tab.setLayout(QGridLayout())

		convert_to_markdown_button = ButtonWithExtraOptions("Convert to Markdown", parent=self, 
			actions=[
				("Export", lambda: self.export_markdown(MarkdownExportTypes.MARKDOWN)), 
				("Load Markdown file", load_markdown_file), 
				("Preview Markdown", preview_markdown_in_browser)
			]
		)
		
		convert_to_markdown_button.main_button.clicked.connect(convert_to_markdown_button_clicked)

		markdown_tab.layout().addWidget(convert_to_markdown_button, 0, 0)
		markdown_tab.layout().setRowStretch(1, 1)

		self.widgets["markdown_tab"].append(markdown_tab)

		if os.path.isfile(self.DEFAULT_MARKDOWN_FILENAME):
			convert_to_markdown_button_clicked(text=self.read_markdown_file())

		return markdown_tab

	def read_markdown_file(self):
		with open(self.DEFAULT_MARKDOWN_FILENAME, "r") as file:
			text = file.read()

		return text

	def restore_tree(self, tree=None):
		if tree is None:
			tree = self.prefs.file["current_module"]

		if tree == {}:
			return

		self.module_content = tree
		self.create_module_tabs()

	def get_tree(self, tree: dict=None, collapsible_tree: dict=None):
		"""Get the tree, add collapsed and checked key to restore it later. 
		"""
		if collapsible_tree is None:
			if len(self.widgets["module_content_scrollarea"]) < 1:
				return {}

			module_content_scrollarea = self.widgets["module_content_scrollarea"][-1]
			module_collapsible = list(get_widgets_from_layout(module_content_scrollarea.main_widget.layout()))[0]

			collapsible_tree = module_collapsible.tree_to_dict()

		if tree is None:
			tree = self.module_content

		result = {}

		for key, val in tree.items():				
			if isinstance(val, dict) and key in collapsible_tree:
				result[key] = self.get_tree(val, collapsible_tree[key])	
			
				result[key]["collapsed"] = collapsible_tree[key]["collapsed"]
				if "checked" in collapsible_tree[key]:
					result[key]["checked"] = collapsible_tree[key]["checked"]
				continue
				
			result[key] = val
			continue

		return result

	def filter_tree(self, tree: dict=None, collapsible_tree: dict=None, properties_to_ignore: tuple=("collapsed", "checked")):
		"""With using the collapsible_tree and the tree, filter the tree with the checked checkbox on the collapsible_tree
		"""
		if collapsible_tree is None:
			module_content_scrollarea = self.widgets["module_content_scrollarea"][-1]
			module_collapsible = list(get_widgets_from_layout(module_content_scrollarea.main_widget.layout()))[0]

			collapsible_tree = module_collapsible.tree_to_dict()

			# print(PREFS.convert_to_prefs(collapsible_tree))

		if tree is None:
			tree = self.module_content

		result = {}

		for property_name, property_val in tree.items():
			if property_name in properties_to_ignore:
				continue

			# If the property_name is not in the filter means is not a collapsible widget (content, docstring, parameters, etc.) so it's a property (type, docstring, etc)
			# Or if checked is not on the filter means it cannot be disabled
			# Or if checked is in the filter and it's true (so if it's false do not include it)
			if not property_name in collapsible_tree or not "checked" in collapsible_tree[property_name] or ("checked" in collapsible_tree[property_name] and collapsible_tree[property_name]["checked"] == True):
				
				if isinstance(property_val, dict) and property_name in collapsible_tree:
					result[property_name] = self.filter_tree(property_val, collapsible_tree[property_name])	
					continue
					
				result[property_name] = property_val
				continue

			elif "checked" in collapsible_tree[property_name] and collapsible_tree[property_name]["checked"] == False:
				continue

		return result

	def create_filter_dialog(self):
		filter_dialog = FilterDialog(self.prefs, parent=self)
		filter_dialog.setStyleSheet(
			f"""
			QPushButton#CollapseButton {{
				color: {THEME[self.current_theme]['font_color']};
			}}
			""")

		answer = filter_dialog.exec_()
	
		if not answer: # if answer == 0
			return

		self.create_inspect_module_thread(self.prefs.file["current_module_path"])

	def create_tree_tab(self):
		module_content_widget = QWidget()
		module_content_widget.setLayout(QVBoxLayout())
		font = QFont()
		module_content_widget.setStyleSheet(
		f"""
		*{{
			font-family: {THEME['module_collapsible_font_family']};
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
			properties_to_ignore: tuple=("collapsed, checked"), 
			properties_without_checkbox: tuple=("docstring", "inherits"), 
			properties_disabled_by_default: tuple=("self"), 
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
				color = THEME[self.current_theme]["font_color"]

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

					if nested_property_name in properties_to_ignore:
						continue

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
					
					# nested_property_color = self.find_object_type_color(nested_property_name)
					nested_property_label = QLabel(f"{nested_property_name}: {self.convert_to_code_block(nested_property_value)}")
					# nested_property_label.setStyleSheet(f"color: {nested_property_color};")

					property_collapsible.addWidget(nested_property_label)
		
				if "collapsed" in property_value:
					property_collapsible.collapse() if property_value["collapsed"] else property_collapsible.uncollapse()
				if "checked" in property_value:
					property_collapsible.enable_checkbox() if property_value["checked"] else property_collapsible.disable_checkbox()

			elif isinstance(property_value, str):
				property_value = property_value.strip()

				property_label = QLabel(self.convert_to_code_block(property_value))
				property_label.setStyleSheet(f"color {color}")

				property_collapsible.addWidget(property_label)

			return property_collapsible

		def add_object_properties_to_collapsible(object_properties: dict, collapsible: CollapsibleWidget, properties_to_ignore: tuple=("collapsed, checked")):
			"""Given a dictionary with the properties of an object an a collapsible, add widgest to the collapsible representing the properties.
			"""
			for property_name, property_value in object_properties.items():

				if property_name in properties_to_ignore:
					continue

				multiple_line_string = "\n" in property_value if isinstance(property_value, str) else ""

				if isinstance(property_value, (list, tuple, dict)) or multiple_line_string:
					property_content = {property_name: property_value}

					property_collapsible = create_property_collapsible(property_content)
					
					if property_collapsible is None:
						continue

					if "collapsed" in property_value:
						property_collapsible.collapse() if property_value["collapsed"] else property_collapsible.uncollapse()
					if "checked" in property_value:
						property_collapsible.enable_checkbox() if property_value["checked"] else property_collapsible.disable_checkbox()

					collapsible.addWidget(property_collapsible)
					continue

				# property_color = self.find_object_type_color(property_name)
				property_label = QLabel(f"{property_name}: {self.convert_to_code_block(property_value)}")
				# property_label.setStyleSheet(f"color: {property_color};")

				collapsible.addWidget(property_label)
		
		object_name = tuple(object_content)[0]
		object_properties = object_content[object_name]

		color = self.find_object_type_color(object_properties["type"])

		collapsible_object = self.create_collapsible_widget(object_name, color, collapse_button=collapse_button)
		
		if "collapsed" in object_properties:
			if object_properties["collapsed"]: collapsible_object.collapse()
		if "checked" in object_properties:
			collapsible_object.enable_checkbox() if object_properties["checked"] else collapsible_object.disable_checkbox()

		add_object_properties_to_collapsible(object_content[object_name], collapsible_object)

		return collapsible_object

	def find_object_type_color(self, object_type: str, change_types_dict: dict={"class": "type"}) -> str:
		if object_type in change_types_dict:
			object_type = change_types_dict[object_type]

		for _, (type_, type_color) in self.prefs.file["colors"].items():
			if object_type == interpret_type(type_).__name__:
				return type_color
				
		return THEME[self.current_theme]["font_color"]

	def convert_to_code_block(self, string):
		background_color = THEME[self.current_theme]["code_block"]["background_color"]
		font_color = THEME[self.current_theme]["code_block"]["font_color"]

		return convert_to_code_block(string, stylesheet=f"background-color: {background_color}; color: {font_color};")

	def export_module_content(self, export_type: TreeExportTypes) -> None:
		"""Export the object tree as a file"""

		if not self.module_content:
			# If user has not loaded a file, display export error
			error_message = QMessageBox.warning(self, f"Export as {export_type.name}", "Nothing to save.")
			return
		
		default_filename = f"{tuple(self.module_content)[0]}.{export_type.value[1]}"
		path, file_filter = QFileDialog.getSaveFileName(self, f"Export as {export_type.value[0]}", default_filename, f"{export_type.value[0]} Files (*.{export_type.value[1]})")
		
		if path == '':
			return

		with open(path, "w") as file:
			if export_type == TreeExportTypes.PREFS:
				file.write(PREFS.convert_to_prefs(self.module_content))
			
			elif export_type == TreeExportTypes.JSON:
				json.dump(self.module_content, file, indent=4)
			
			elif export_type == TreeExportTypes.YAML:
				yaml.dump(self.module_content, file)
	
	def export_markdown(self, export_type: MarkdownExportTypes):
		if len(self.widgets["markdown_text_edit"]) < 1:
			QMessageBox.critical(self, "Cannot export markdown", "You haven't create any markdown to export.")
			return

		markdown_text = self.widgets["markdown_text_edit"][-1].toPlainText()
	
		default_filename = f"{tuple(self.module_content)[0]}.{export_type.value[1]}"
		path, file_filter = QFileDialog.getSaveFileName(self, f"Export as {export_type.value[0]}", default_filename, f"{export_type.value[0]} Files (*.{export_type.value[1]})")
		
		if path == '':
			return

		with open(path, "w") as file:
			if export_type == MarkdownExportTypes.MARKDOWN:
				file.write(markdown_text)
			
			elif export_type == MarkdownExportTypes.HTML:
				file.write(markdown.markdown(markdown_text))
			
			elif export_type == MarkdownExportTypes.RESTRUCTUREDTEXT:
				file.write(m2r2.convert(markdown_text))
	

def init_app():
	"""Init PyAPIReference application and main window.
	"""
	app = QApplication(sys.argv)
	app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps) # https://github.com/5yutan5/PyQtDarkTheme#usage
	main_window = MainWindow()

	sys.exit(app.exec_())

if __name__ == "__main__":
	init_app()
