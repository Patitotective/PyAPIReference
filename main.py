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
import json
import yaml
from enum import Enum, auto

import PREFS
import markdown # Markdown to HTML converter
import m2r2 # Markdown to ReStructuredText converter
import platform

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
	QShortcut, QMenuBar, 
	QSplitter
)

from PyQt5.QtGui import QIcon, QPixmap, QFontDatabase, QFont, QKeySequence, QGuiApplication, QHoverEvent
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QTimer, QEvent

# Dependencies
from pyapireference.ui.collapsible_widget import CollapsibleWidget, CheckBoxCollapseButton, CollapseButton
from pyapireference.ui.scrollarea import ScrollArea
from pyapireference.ui.settings_dialog import SettingsDialog
from pyapireference.ui.markdownhighlighter import MarkdownHighlighter
from pyapireference.ui.warning_dialog import WarningDialog
from pyapireference.ui.button_with_extra_options import ButtonWithExtraOptions
from pyapireference.ui.filter_dialog import FilterDialog
from pyapireference.ui.markdown_previewer import MarkdownPreviewer
from pyapireference.ui.about_dialog import AboutDialog
from pyapireference.ui.markdown_text_edit import MarkdownTextEdit
from pyapireference.ui import resources # Qt resources GUI/resources.qrc

from pyapireference.inspect_object import inspect_object, check_file
from pyapireference.extra import (
	create_menu, convert_to_code_block, 
	get_module_from_path, change_widget_stylesheet, 
	add_text_to_text_edit, get_widgets_from_layout, 
	HTML_TAB, interpret_type, 
	HTML_SPACE
)

from pyapireference.tree_to_markdown import convert_tree_to_markdown


THEME = PREFS.read_prefs_file(f"pyapireference{os.sep}ui{os.sep}theme.prefs")
VERSION = "v0.1.50"


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

	def generate_error_text(self, error: Exception):
		result = ""
		error = traceback.format_exc().replace('\n', '<br>').replace('\t', HTML_TAB).replace("    ", HTML_TAB).replace("  ", HTML_SPACE * 2).replace("   ", HTML_SPACE * 3)

		result = f"""An unexpected error ocurred: <br>
		{self.convert_to_code_block(error)}<br>
		"""

		if isinstance(error, RecursionError): result += "Try changing the <b>Recursion limit</b> on settings.<br>"
		result += f"If you think it is and issue, please report it at <a style='color: {THEME[self.prefs.file['theme']]['link_color']};' href='https://github.com/Patitotective/PyAPIReference/issues'>GitHub issues</a>."		

	def run(self):
		self.running = True
		try:
			module, error = get_module_from_path(self.path)
		except Exception as error:
			self.exception_message = self.generate_error_text(error)

			self.expection_found.emit()
			self.running = False
			
		if module is None: # Means exception
			error = error.replace('\n', '<br>').replace('    ', HTML_TAB)		

			self.exception_message = f"Couldn't load file. Exception found: <br>{self.convert_to_code_block(error)}" 
			self.expection_found.emit()
			self.running = False
		else:
			try:
				exclude_types, kwargs = self.get_filter()

				kwargs["recursion_limit"] = self.prefs.file["settings"]["inspect_module"]["recursion_limit"]["value"]

				self.module_content = inspect_object(module, exclude_types=exclude_types, **kwargs)
			except Exception as error:
				self.exception_message = self.generate_error_text(error)

				self.expection_found.emit()
				self.running = False
			else:
				self.finished.emit()
				self.running = False

	def convert_to_code_block(self, string):
		background_color = THEME[self.prefs.file['theme']]["code_block"]["background_color"]
		font_color = THEME[self.prefs.file['theme']]["code_block"]["font_color"]

		return convert_to_code_block(string, stylesheet=f"background-color: {background_color}; color: {font_color};")


class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent=parent)

		print("PyAPIReference started")

		self.EXPORT_TREE_MENU = {
			"Export as PREFS": {
				"callback": lambda: self.main_widget.export_tree(TreeExportTypes.PREFS), 
			}, 
			"Export as JSON": {
				"callback": lambda: self.main_widget.export_tree(TreeExportTypes.JSON), 
			}, 
			"Export as YAML": {
				"callback": lambda: self.main_widget.export_tree(TreeExportTypes.YAML), 
			}, 
		}

		self.EXPORT_API_MENU = {
			"Export as Markdown": {
				"callback": lambda: self.main_widget.export_markdown(MarkdownExportTypes.MARKDOWN), 
			}, 
			"Export as HTML": {
				"callback": lambda: self.main_widget.export_markdown(MarkdownExportTypes.HTML), 
			}, 
			"Export as ReStructuredText": {
				"callback": lambda: self.main_widget.export_markdown(MarkdownExportTypes.RESTRUCTUREDTEXT), 
			}, 	
		}

		self.FILE_MENU = {
			"Load Module": {
				"callback": lambda: self.main_widget.load_module_file() if self.main_widget.widgets["load_file_button"][-1].isEnabled() else QMessageBox.critical(self, "Cannot load file", "There is a file already loading, wait for it to load another."), 
				"shortcut": "Ctrl+O", 
			}, 
			"Export Tree>": self.EXPORT_TREE_MENU, 
			"Export API Reference>": self.EXPORT_API_MENU, 
			"Close": {
				"callback": self.close, 
				"shortcut": "Ctrl+W", 
			}
		}

		self.EDIT_MENU = {
			"&Filter Tree": {
				"callback": lambda: self.main_widget.create_filter_dialog(), 
				"shortcut": "Ctrl+F", 
			}, 
			"&Settings": {
				"callback": self.open_settings_dialog, 
				"shortcut": "Ctrl+S",  
			}
		}

		self.ABOUT_MENU = {
			"About &Qt": {
				"callback": lambda: QMessageBox.aboutQt(self), 
			}, 
			"About &PyAPIReference": {
				"callback": lambda: AboutDialog(VERSION, THEME[self.main_widget.current_theme]["link_color"], self).exec_()
			}
		}

		self.create_menubar()
		self.init_window()

		self.show()
		self.restore_geometry()

	def init_window(self):
		self.setWindowTitle("PyAPIReference")
		self.setWindowIcon(QIcon(':/img/icon.png'))

		self.main_widget = MainWidget(parent=self)
		
		self.setStyleSheet(qdarktheme.load_stylesheet(self.main_widget.current_theme))

		self.setCentralWidget(self.main_widget)

	def create_menubar(self):
		"""Create menu bar."""
		menubar = self.menuBar()

		menubar.addMenu(create_menu(self.FILE_MENU, '&File', parent=self))
		menubar.addMenu(create_menu(self.EDIT_MENU, '&Edit', parent=self))
		menubar.addMenu(create_menu(self.ABOUT_MENU, '&About', parent=self))
		
	def open_settings_dialog(self):
		settings_dialog = SettingsDialog(self.main_widget.prefs, parent=self)
		preivous_theme = self.main_widget.current_theme
		previous_colors = self.main_widget.prefs.file["colors"]

		answer = settings_dialog.exec_()
		
		if not answer:
			return
			
		if self.main_widget.prefs.file["colors"] != previous_colors:
			if self.main_widget.prefs.file["current_module_path"]:	
				self.main_widget.load_last_module(warning=True)

		if self.main_widget.current_theme != preivous_theme:
			self.reset_app()

	def reset_app(self):
		self.close() # Close
		self.__init__() # Init again

	def restore_geometry(self):
		print("Restoring MainWindow geometry")

		self.showNormal()

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
		print("Saving MainWindow geometry")
		geometry = self.geometry()

		pos = geometry.x(), geometry.y()
		size = geometry.width(), geometry.height()

		self.main_widget.prefs.write_prefs("state/pos", pos)
		self.main_widget.prefs.write_prefs("state/size", size)
		self.main_widget.prefs.write_prefs("state/is_maximized", self.isMaximized())

	def close_app(self):
		if self.main_widget.save_geometry_at_end:
			self.save_geometry()
	
		if self.main_widget.save_tree_at_end:
			self.main_widget.prefs.write_prefs("current_module", self.main_widget.get_tree())

	def closeEvent(self, event) -> None:
		"""This will be called when the windows is closed."""		
		self.close_app()
		event.accept()

		print("Closed PyAPIReference")


class MainWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__()

		self.parent = parent
		self.mouse_hover = False

		self.FONTS = ("UbuntuMono-B.ttf", "UbuntuMono-BI.ttf", "UbuntuMono-R.ttf", "UbuntuMono-RI.ttf")

		self.widgets = {
			"module_tabs": [], 
			"load_file_button": [], 
			"retry_button": [], 
			"loading_label": [], 
			"markdown_text_edit": [], 
			"markdown_previewer": [], 
		}

		self.module_content = None

		self.save_tree_at_end = True
		self.save_geometry_at_end = True

		self.setAttribute(Qt.WA_Hover, True)

		self.load_fonts()
		self.init_prefs()
		self.init_window()

	@property	
	def current_theme(self):
		return self.prefs.file["theme"]

	def load_fonts(self):
		for font in self.FONTS:
			QFontDatabase.addApplicationFont(f':/fonts/{font}')

	def init_window(self):
		self.setLayout(QGridLayout())

		self.main_frame()

	def init_prefs(self):
		default_prefs = {
			"current_module_path": "", # The path when you open a file to restore it 
			"current_module": {}, 
			"current_markdown": "", 
			"current_tab": 0, 
			"theme": "dark", 
			"state": {
				"pos": (-100, -100), 
				"size": (0, 0), 
				"is_maximized": False,
				"preview_saved": False, 
			}, 
			"settings": {
				"inspect_module": {
					"recursion_limit": {
						"tooltip": "Recursion limit when inspecting module (when large modules it should be bigger).", 
						"value": 10 ** 6, 
						"min_val": 1500, 
					}, 
				}, 
				"preview_markdown": {
					"synchronize_scrollbars": {
						"tooltip": "When previewing markdown synchronize editor's and preview's scrollbar.", 
						"value": True, 
					}, 
					"maximize_window": {
						"tooltip": "Maximize window when previewing markdown", 
						"value": True,
					}
				}, 
			}, 
			"cache": {}, 			
			"colors": {
				"Modules": ("types.ModuleType", "#4e9a06"),			
				"Classes": ("type", "#b140bf"),
				"Functions": ("types.FunctionType", "#ce5c00"),
				"Strings": ("str", "#5B82D7"), 
			}, 
			"filter": {
				"Include Imported Members": ("#include_imported_members", False),
				"Modules": ('types.ModuleType', False), 
				"Classes": ('type', True), 
				"Functions": ('types.FunctionType', True), 
			}
		}

		self.prefs = PREFS.Prefs(default_prefs, filename=f"Prefs{os.sep}settings.prefs")

	def main_frame(self):
		logo = QLabel()

		pixmap = QPixmap(":/img/logo_without_background.png")
		logo.setPixmap(pixmap)

		logo.setStyleSheet("margin-bottom: 10px;")
		logo.setAlignment(Qt.AlignCenter)

		load_file_button = ButtonWithExtraOptions("Load Module", parent=self, 
			actions=[
				("Reload Module", self.load_last_module), 
				("Unload Module", self.unload_file), 
				("Filter", self.create_filter_dialog)
			]
		)
		
		load_file_button.main_button.clicked.connect(self.load_module_file)

		self.widgets["load_file_button"].append(load_file_button)

		self.layout().addWidget(logo, 0, 0, 1, 0, Qt.AlignTop)
		self.layout().addWidget(load_file_button, 1, 0, Qt.AlignTop)
		self.layout().setRowStretch(1, 1)

		self.restore_module()

	def create_loading_label(self):
		loading_label = QLabel("Loading...")
		loading_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		loading_label.setStyleSheet(f"font-size: 20px; font-family: {THEME['tree_font_family']};")

		if len(self.widgets["loading_label"]) > 0:
			self.widgets["loading_label"][-1].setParent(None)
			self.widgets["loading_label"].pop()

		self.widgets["loading_label"].append(loading_label)

		return loading_label

	def restore_module(self):
		"""Restore tree if tree available else load last module.
		"""
		self.timer = QTimer()
		if not self.prefs.file["current_module"] == {}: # Means it's not empty
			self.timer.timeout.connect(self.restore_tree)		
		elif os.path.isfile(self.prefs.file["current_module_path"]): # Means the path really exist
			self.timer.timeout.connect(lambda: self.load_last_module(warning=False))
		else:
			return
		
		# Disable Load File button
		self.widgets["load_file_button"][-1].setEnabled(False)

		loading_label = self.create_loading_label()

		self.layout().addWidget(loading_label, 2, 0)
		self.layout().setRowStretch(2, 100)
		
		self.timer.timeout.connect(lambda: self.widgets["load_file_button"][-1].setEnabled(True))
		self.timer.timeout.connect(lambda: loading_label.setParent(None))
		self.timer.timeout.connect(self.timer.stop)		
		self.timer.start(500)

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
			QMessageBox.warning(self, "No Module to Unload", "You must load a module first to unload it.")
			return

		if self.prefs.file['current_markdown'] != "":
			warning = WarningDialog(
				"Lose Markdown", 
				"If you unload this module, this module's Markdown will be lost.\nExport it to preserve.", 
				no_btn_text="Cancel", 
				yes_btn_text="Continue", 
				parent=self).exec_()
			
			if not warning:
				return

		self.clear_widgets(to_clear=["module_tabs", "markdown_text_edit", "markdown_previewer"])

		self.prefs.write_prefs("current_markdown", "")
		self.prefs.write_prefs("current_module_path", "")
		self.prefs.write_prefs("current_module", {})

	def clear_widgets(self, to_clear: list=None):
		for widget_name, widget_list in self.widgets.items():
			# print(f"{widget_name}: {len(widget_list) > 1=} and ({to_clear is None=} or {widget_name in to_clear=})")
			if len(widget_list) > 0 and (to_clear is None or widget_name in to_clear):
				widget_list[-1].setParent(None)
				self.widgets[widget_name].pop()

	def load_module_file(self):
		if len(self.widgets["markdown_previewer"]) > 0:
			self.widgets["markdown_previewer"].pop()

		markdown_warning = True

		if self.prefs.file['current_markdown'] != "": # If the markdown is not emtpy
			markdown_warning = WarningDialog(
				"Lose Markdown", 
				"If you load another module this module's Markdown will be lost.\nExport it to preserve.", 
				no_btn_text="Cancel", 
				yes_btn_text="Continue", 
				parent=self).exec_()

			if not markdown_warning:
				return

		path = self.load_file("Python files (*.py)")
		
		if path == '':
			return

		if markdown_warning:
			self.prefs.write_prefs("current_markdown", "")

		self.prefs.write_prefs("current_module_path", path)

		self.create_inspect_module_thread(path)

	def load_last_module(self, warning: bool=True):
		if self.prefs.file["current_module_path"] == "" and warning:
			QMessageBox.warning(self, "No Module to Reload", "You must load a module first to reload it.")
			return

		if not self.prefs.file["current_module_path"] == "":
			if not os.path.isfile(self.prefs.file["current_module_path"]):
				return # Ignore it because is not a valid path

			self.create_inspect_module_thread(self.prefs.file["current_module_path"])		

	def create_inspect_module_thread(self, module):
		# Check if file is safe 
		not_safe_lines, name_main = check_file(module)
		lines = ""

		# If name main is present, file is safe. Otherwise enter here.
		if not name_main:
			if len(not_safe_lines) > 0:
				for index, line in not_safe_lines:
					lines += f"Line: {index}, {line}\n"
				
				message = "This module contains global calls which can be unsafe when inspecting.\n\n" + f"\nUnsafe Lines: \n{lines}\n\n" + "Consider moving these inside a if __name__ == '__main__' condition."
				warning = WarningDialog(
						"File Not Safe", 
						message, 
						no_btn_text="Cancel", 
						yes_btn_text="Continue", 
						parent=self,
						safe_dialog=(True, THEME[self.current_theme]["link_color"])).exec_()
				
				if not warning:
					return
				
		self.widgets["load_file_button"][-1].setEnabled(False)

		self.save_tree_at_end = False

		loading_label = self.create_loading_label()

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
		self.worker.finished.connect(lambda: loading_label.setParent(None))
		self.worker.expection_found.connect(lambda: loading_label.setParent(None))		
		self.worker.expection_found.connect(self.inspect_object_worker_exception)

		self.timer = QTimer()
		self.timer.timeout.connect(self.thread.start)
		self.timer.timeout.connect(self.timer.stop)
		self.timer.start(100)

	def inspect_object_worker_exception(self):
		self.stop_inspect_object_worker()

		self.widgets["load_file_button"][-1].setEnabled(True)

		self.save_tree_at_end = False
		self.prefs.write_prefs("current_module", {})

		exception_label = QLabel(self.worker.exception_message)
		exception_label.setOpenExternalLinks(True)
		exception_label.setTextFormat(Qt.TextFormat.RichText)		
		exception_label.setStyleSheet(f"font-size: 15px; font-family: {THEME['tree_font_family']};")

		retry_button = QPushButton("Retry")
		retry_button.clicked.connect(lambda: self.widgets["loading_label"][-1].setParent(None) if len(self.widgets["loading_label"]) > 0 else None)
		retry_button.clicked.connect(lambda: self.create_inspect_module_thread(self.prefs.file["current_module_path"]))

		if len(self.widgets["loading_label"]) > 0:
			self.widgets["loading_label"][-1].setParent(None)
			self.widgets["loading_label"].pop()

		self.widgets["loading_label"].append(exception_label)

		self.widgets["retry_button"].append(retry_button)
	
		self.layout().addWidget(exception_label, 2, 0)		
		self.layout().addWidget(retry_button, 3, 0)
		
		self.layout().setRowStretch(1, 0)
		self.layout().setRowStretch(2, 0)
		self.layout().setRowStretch(3, 0)
		self.layout().setRowStretch(4, 100)

	def stop_inspect_object_worker(self):
		self.thread.quit()
		self.worker.deleteLater()
		self.thread.deleteLater()		

	def inspect_object_worker_finished(self):
		self.stop_inspect_object_worker()

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
		
		first_time = True

		module_tabs = QTabWidget()
		module_tabs.currentChanged.connect(tab_changed)

		module_tabs_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), module_tabs)
		module_tabs_shortcut.activated.connect(lambda: module_tabs.setCurrentIndex((module_tabs.currentIndex() + 1) % module_tabs.count()))

		self.layout().addWidget(module_tabs, 2, 0, 1, 0)
		self.layout().setRowStretch(2, 1)		
		self.layout().setRowStretch(1, 0)

		module_tabs.addTab(self.create_tree_tab(), "Tree")		
		module_tabs.addTab(self.create_markdown_tab(), "API Reference")		

		module_tabs.setCurrentIndex(self.prefs.file["current_tab"])

		self.widgets["module_tabs"].append(module_tabs)

	def create_markdown_tab(self):
		def create_markdown_text_edit(text: str=None):
			def text_edit_updated():
				self.prefs.write_prefs("current_markdown", text_edit.toPlainText())
				
				if self.text_timer.isActive():
					self.text_timer.setInterval(UPDATE_TIME)
					return

				self.text_timer.start(UPDATE_TIME)

			def text_timeout():
				if len(self.widgets["markdown_previewer"]) > 0:
					self.widgets["markdown_previewer"][-1].update_markdown(text_edit.toPlainText())

				self.text_timer.stop()
			nonlocal markdown_edit_section

			if text is None:
				markdown_text = convert_tree_to_markdown(tree=self.filter_tree())
			else:
				markdown_text = text

			if len(self.widgets["markdown_text_edit"]) > 0:
				# If markdown_text_edit was already created just update it.
				self.widgets["markdown_text_edit"][-1].setText(markdown_text)
				return

			UPDATE_TIME = 200 # msec
			self.text_timer = QTimer()
			self.text_timer.timeout.connect(text_timeout)

			text_edit = MarkdownTextEdit()
			text_edit.textChanged.connect(text_edit_updated)

			text_edit.setPlainText(markdown_text)
			text_edit.setStyleSheet(f"background-color: {THEME[self.current_theme]['markdown_highlighter']['background-color']};")

			highlighter = MarkdownHighlighter(text_edit, THEME=THEME, current_theme=self.current_theme)

			self.widgets["markdown_text_edit"].append(text_edit)

			markdown_edit_section.addWidget(text_edit)

			if len(self.widgets["markdown_previewer"]) > 0:
				self.widgets["markdown_previewer"].pop()
				preview_markdown()

			markdown_tab.layout().addWidget(markdown_edit_section, 1, 0)
			markdown_tab.layout().setRowStretch(0, 0)

			return text_edit

		def convert_to_markdown_button_clicked(ignore=None, text: str=None, load_clicked=True):
			nonlocal convert_to_markdown_clicked

			if not convert_to_markdown_clicked:
				convert_to_markdown_clicked = True
				convert_to_markdown_button.main_button.setText("Update API Reference")				
				create_markdown_text_edit(text)
				return

			warning = WarningDialog("Overwrite Markdown", "Do you want to overwrite current Markdown text?", parent=self).exec_() # Return 1 if yes, 0 if no

			if not warning:
				return

			if load_clicked:
				create_markdown_text_edit(text)
			else:
				create_markdown_text_edit()

		def load_markdown_file():
			path = self.load_file("Markdown files (*.md)", directory="") # If directory not empty, filter doesn't work
			
			if path == "":
				return

			with open(path, "r") as file:
				content = file.read()

			convert_to_markdown_button_clicked(text=content, load_clicked=True)

		def preview_markdown():
			def stop_previewing():
				self.prefs.write_prefs("state/preview_saved", False)
				
				if self.parent.isMaximized():
					if self.prefs.file["settings"]["preview_markdown"]["maximize_window"]["value"]:
						self.save_geometry_at_end = True	
						self.parent.restore_geometry()
	
				self.clear_widgets(to_clear=["markdown_previewer"])

			def preview_already_live():
				answer = WarningDialog(
					"Markdown Preview Live", 
					"You are already previewing the Markdown.", 
					yes_btn_text="OK", 
					yes_btn_callback=2, 
					no_btn_text="Stop previewing", 
					no_btn_callback=1, 
					parent=self
				).exec_()
				
				if answer == 1: # Means stop
					stop_previewing()

			def markdown_previewer_scrollbar_changed(point):
				if markdown_previewer.mouse_hover and self.prefs.file["settings"]["preview_markdown"]["synchronize_scrollbars"]["value"]:
					y = int(point.y())
					self.widgets["markdown_text_edit"][-1].verticalScrollBar().setValue(y)
			
			nonlocal markdown_edit_section

			if self.prefs.file['current_markdown'] == "":
				QMessageBox.critical(self, "No Markdown to preview", "You must generate the API Reference first to preview it.")
				return

			if len(self.widgets["markdown_previewer"]) > 0:
				preview_already_live()
				return

			self.save_geometry_at_end = False

			markdown_previewer = MarkdownPreviewer(self.prefs, self.prefs.file['current_markdown'], scroll_link=(self.widgets["markdown_text_edit"][-1].horizontalScrollBar(), self.widgets["markdown_text_edit"][-1].verticalScrollBar()), parent=self)			
			markdown_previewer.page().scrollPositionChanged.connect(markdown_previewer_scrollbar_changed)
			markdown_previewer.stop.connect(stop_previewing)

			markdown_edit_section.addWidget(markdown_previewer)
			
			equal_width = max(self.widgets["markdown_text_edit"][-1].minimumSizeHint().width(), markdown_previewer.minimumSizeHint().width())
			extra_width = 15 # An extra value to subtract from left widget's width and add to right widget's width

			markdown_edit_section.setSizes([equal_width - extra_width, equal_width + extra_width])

			if self.prefs.file["settings"]["preview_markdown"]["maximize_window"]["value"]:
				if not self.prefs.file["state"]["preview_saved"]:
					self.parent.save_geometry()
					self.prefs.write_prefs("state/preview_saved", True)
			
				self.parent.showMaximized()

			self.widgets["markdown_previewer"].append(markdown_previewer)

		if len(self.widgets["markdown_text_edit"]) > 0:
			self.widgets["markdown_text_edit"][-1].setParent(None)
			self.widgets["markdown_text_edit"].pop()

		convert_to_markdown_clicked = False

		markdown_tab = QWidget()
		markdown_tab.setLayout(QGridLayout())

		markdown_edit_section = QSplitter(Qt.Horizontal)
		markdown_edit_section.setStyleSheet(
		"""
		QSplitter::handle {
		    image: none;
			width: 0px;
			height: 0px;
		}
		"""
		)

		convert_to_markdown_button = ButtonWithExtraOptions("Generate API Reference", parent=self, 
			actions=[
				("Preview Markdown", preview_markdown), 			
				("Export", self.parent.EXPORT_API_MENU), 
				("Load Markdown file", load_markdown_file), 
			]
		)
		
		convert_to_markdown_button.main_button.clicked.connect(convert_to_markdown_button_clicked)

		markdown_tab.layout().addWidget(convert_to_markdown_button, 0, 0)
		markdown_tab.layout().setRowStretch(1, 1)

		if self.prefs.file['current_markdown'] != "":
			convert_to_markdown_button_clicked(text=self.prefs.file['current_markdown'])

		return markdown_tab
	
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
			if len(self.widgets["module_tabs"]) < 1:
				return {}

			tree_scrollarea = self.widgets["module_tabs"][-1].widget(0) # Get the first tab from module_tabs
			tree_widget_layout = tree_scrollarea.widget().layout() # Get the layout of the main widget in the tree scrollare
			widgets_in_tree_widget = list(get_widgets_from_layout(tree_widget_layout)) # Get the widgets in the tree widget layout

			if len(widgets_in_tree_widget) < 1:
				return {}

			tree_collapsible = widgets_in_tree_widget[0]
			collapsible_tree = tree_collapsible.tree_to_dict()

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
			tree_scrollarea = self.widgets["module_tabs"][-1].widget(0) # Get the first tab from module_tabs
			tree_widget_layout = tree_scrollarea.widget().layout() # Get the layout of the main widget in the tree scrollare
			widgets_in_tree_widget = list(get_widgets_from_layout(tree_widget_layout)) # Get the widgets in the tree widget layout

			tree_collapsible = widgets_in_tree_widget[0]

			collapsible_tree = tree_collapsible.tree_to_dict()

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

		if self.prefs.file["current_module_path"] == "":
			return
			
		self.create_inspect_module_thread(self.prefs.file["current_module_path"])

	def create_tree_tab(self):
		module_content_widget = QWidget()
		module_content_widget.setLayout(QVBoxLayout())
		
		font = QFont()
		module_content_widget.setStyleSheet(
		f"""
		*{{
			font-family: {THEME['tree_font_family']};
		}}
		QToolTip {{
			font-family: {font.defaultFamily()};
		}}
		""")

		tree_collapsible = self.create_module_tree(self.module_content, collapse_button=CollapseButton)
		
		tree_collapsible.uncollapse()

		module_content_widget.layout().addWidget(tree_collapsible)
		module_content_widget.layout().addStretch(1)

		module_content_scrollarea = ScrollArea(module_content_widget)

		return module_content_scrollarea

	def create_module_tree(self, object_content: dict, collapse_button=CheckBoxCollapseButton):
		"""Generates a collapsible widget for a given object_content generated by inspect_object
		"""

		def create_property_collapsible(
			property_name: str,
			property_value: any,  
			properties_to_ignore: tuple=("collapsed, checked"), 
			properties_without_checkbox: tuple=("docstring", "inherits"), 
			properties_disabled_by_default: tuple=("self"), 
			parent: str=None
			):
			
			"""Given a dicionary with {property_name: property_value}, where property_value could be a dictionary or a list
			return a collapsible widget.
			"""
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
				add_object_properties_to_collapsible(property_value, property_collapsible, parent=property_name)

			elif isinstance(property_value, str):
				property_value = property_value.strip()

				property_label = QLabel(self.convert_to_code_block(property_value))
				property_label.setStyleSheet(f"color {color}")

				property_collapsible.addWidget(property_label)

			# Add tooltips
			if "type" in property_value and isinstance(property_value, dict): # Means is a variable (classes, strings, etc)
				property_collapsible.title_frame.setToolTip(f"{property_name} {property_value['type']}")
			elif "annotation" in property_value and isinstance(property_value, dict): # Means is a parameter
				parameter_tooltip = property_name

				if property_value["annotation"] is not None and property_value["default"] is not None:
					parameter_tooltip += f" ({property_value['annotation']}={property_value['default']})"
				elif property_value["annotation"] is not None and property_value["default"] is None:
					parameter_tooltip += f" ({property_value['annotation']})"
				elif property_value["default"] is not None:
					parameter_tooltip += f"={property_value['default']}"

				property_collapsible.title_frame.setToolTip(parameter_tooltip)
			else:
				if property_name == "inherits":
					property_name = "inheritance"

				property_collapsible.title_frame.setToolTip(f"{parent}'s {property_name}")
			
			return property_collapsible

		def add_object_properties_to_collapsible(object_properties: dict, collapsible: CollapsibleWidget, properties_to_ignore: tuple=("collapsed, checked"), parent: str=None):
			"""Given a dictionary with the properties of an object an a collapsible, add widgest to the collapsible representing the properties.
			"""
			for property_name, property_value in object_properties.items():
				if property_name in properties_to_ignore:
					continue

				multiple_line_string = "\n" in property_value if isinstance(property_value, str) else ""
				if isinstance(property_value, (list, tuple, dict)) or multiple_line_string:
					
					property_collapsible = create_property_collapsible(property_name, property_value, parent=parent)

					if property_collapsible is None:
						continue
					
					if isinstance(property_value, dict):
						if "collapsed" in property_value:
							property_collapsible.collapse() if property_value["collapsed"] else property_collapsible.uncollapse()
						if "checked" in property_value:
							property_collapsible.enable_checkbox() if property_value["checked"] else property_collapsible.disable_checkbox()

					collapsible.addWidget(property_collapsible)
					continue
				
				property_label = QLabel(f"{property_name}: {self.convert_to_code_block(property_value)}")

				collapsible.addWidget(property_label)
		
		object_name = tuple(object_content)[0]
		object_properties = object_content[object_name]

		# print(PREFS.convert_to_prefs(object_properties))

		color = self.find_object_type_color(object_properties["type"])

		collapsible_object = self.create_collapsible_widget(object_name, color, collapse_button=collapse_button)
		collapsible_object.title_frame.setToolTip(f"{object_name} module at {self.prefs.file['current_module_path']}")

		if "collapsed" in object_properties:
			if object_properties["collapsed"]: collapsible_object.collapse()
		if "checked" in object_properties:
			collapsible_object.enable_checkbox() if object_properties["checked"] else collapsible_object.disable_checkbox()

		add_object_properties_to_collapsible(object_content[object_name], collapsible_object, parent=object_name)

		return collapsible_object

	def create_collapsible_widget(self, title: str, color=None, collapse_button=CheckBoxCollapseButton, parent=None) -> QWidget:
		if parent is None:
			parent = self
			
		collapsible_widget = CollapsibleWidget(
			title, 
			color, 
			collapse_button, 
			parent)

		return collapsible_widget

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

	def export_tree(self, export_type: TreeExportTypes) -> None:
		"""Export the object tree as a file"""

		module_content = self.prefs.file["current_module_path"]

		if module_content == "":
			# If user has not loaded a file, display export error
			error_message = QMessageBox.warning(self, f"Export as {export_type.name}", "Nothing to export, load a module first.")
			return
		
		default_filename = f"{tuple(self.module_content)[0]}.{export_type.value[1]}"
		path, file_filter = QFileDialog.getSaveFileName(self, f"Export as {export_type.value[0]}", default_filename, f"{export_type.value[0]} Files (*.{export_type.value[1]})")
		
		if path == '':
			return

		with open(path, "w") as file:
			if export_type == TreeExportTypes.PREFS:
				file.write(PREFS.convert_to_prefs(self.filter_tree()))
			
			elif export_type == TreeExportTypes.JSON:
				json.dump(self.filter_tree(), file, indent=4)
			
			elif export_type == TreeExportTypes.YAML:
				yaml.dump(self.filter_tree(), file)
	
	def export_markdown(self, export_type: MarkdownExportTypes):
		if len(self.widgets["markdown_text_edit"]) < 1:
			QMessageBox.critical(self, "Cannot Export Markdown", "No Markdown to export.")
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
