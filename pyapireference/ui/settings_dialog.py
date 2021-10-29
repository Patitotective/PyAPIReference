from PyQt5.QtWidgets import (
	QWidget, QLabel, 
	QDialog, QPushButton, 
	QVBoxLayout, QHBoxLayout, 
	QStyle, QComboBox, 
	QTabWidget, QFormLayout, 
	QColorDialog, QGridLayout, 
	QSpinBox, QDoubleSpinBox, 
	QLineEdit, QMessageBox, 
	QCheckBox)

from PyQt5.QtGui import QColor, QIcon

from qtwidgets import AnimatedToggle
import PREFS

if __name__ == "__main__":
    raise RuntimeError("settings_dialog.py requires to_sentence_case from pyapireference.extra.py which is outside this folder, you can't run this script as main")
else:
	from pyapireference.ui.scrollarea import ScrollArea
	from pyapireference.ui.formlayout import FormLayout
	from pyapireference.ui.warning_dialog import WarningDialog
	from pyapireference.extra import to_sentence_case, get_text_size, stylesheet_to_dict, remove_key_from_dict, interpret_type

class SettingsDialog(QDialog):
	def __init__(self, prefs, *args, title="Settings", parent=None, **kwargs):
		super().__init__(parent=parent, *args, **kwargs)

		self.prefs = prefs
		self.widgets = {"dark_theme_toggle": []}

		self.setWindowTitle(title)
		self.setLayout(QFormLayout())

		self.create_widgets()

		width = self.sizeHint().width()
		height = self.sizeHint().height()
		self.setFixedSize(width if not width > 325 else 325, height if not height > 455 else 455)

	def create_widgets(self):
		def apply_cache(cache: dict=None, path: str=""):
			"""Apply the settings in self.prefs.file["cache"]
			"""
			if cache is None:
				cache = self.prefs.file["cache"]

			for pref, pref_val in cache.items():
				if isinstance(pref_val, dict):
					apply_cache(cache=pref_val, path=f"{path}/{pref}" if path != "" else pref)
					continue

				self.prefs.write_prefs(pref if path == "" else f"{path}/{pref}", pref_val)

		def apply_changes():
			apply_cache()

			self.done(1)

		def cancel_changes():
			if self.prefs.file["cache"] != {}:
				warning = WarningDialog(
					"Discard Changes", 
					"Do you want to discard your changes?", 
					no_btn_text="Cancel", 
					parent=self).exec_()

				if not warning:
					return

			self.prefs.write_prefs("cache", {})

			self.done(0)

		tabs = QTabWidget()

		tabs.addTab(self.create_general_tab(), "General")
		tabs.addTab(self.create_theme_tab(), "Theme")

		buttons_widget = QWidget()
		buttons_widget.setLayout(QHBoxLayout())

		apply_button = QPushButton(icon=self.style().standardIcon(QStyle.SP_DialogApplyButton), text="Apply")
		apply_button.clicked.connect(apply_changes)

		cancel_button = QPushButton(icon=self.style().standardIcon(QStyle.SP_DialogCancelButton), text="Cancel")
		cancel_button.clicked.connect(cancel_changes)

		buttons_widget.layout().addWidget(apply_button)
		buttons_widget.layout().addWidget(cancel_button)

		self.layout().addRow(tabs)
		self.layout().addRow(buttons_widget)

	def create_general_tab(self):
		def create_widgets(settings: dict, parent=None):
			for pref, pref_props in settings.items():
				if not "value" in pref_props:  # Means is a section that contains other settings
					section_label = QLabel(f"{to_sentence_case(pref)}<hr>")
					section_label.setStyleSheet("font-size: 16px; margin-top: 10px; margin-bottom: 0px; padding-bottom: 0px;")
					general_tab.layout().addRow(section_label)

					create_widgets(settings[pref], parent=pref)
					continue

				val = pref_props["value"]
				tooltip = pref_props["tooltip"]
				path = f"cache/settings/{parent}/{pref}/value" if parent is not None else f"cache/settings/{pref}/value"

				if type(val) in (int, float):
					min_val, max_val = 0, 2147483647
					if "min_val" in pref_props:
						min_val = pref_props["min_val"]
					if "max_val" in pref_props:
						max_val = pref_props["max_val"]

					if isinstance(val, int):
						spinbox = QSpinBox()
					elif isinstance(val, float):
						spinbox = QDoubleSpinBox(val)
						spinbox.setDecimals(2)

					spinbox.setRange(min_val, max_val)
					spinbox.setValue(val)	
					spinbox.valueChanged.connect(lambda spinbox_val, path=path: self.prefs.write_prefs(path, spinbox_val))
					spinbox.setToolTip(tooltip)

					general_tab.layout().addRow(f"{to_sentence_case(pref)}: ", spinbox)

				elif type(val) == bool:
					checkbox = QCheckBox(to_sentence_case(pref))
					checkbox.setChecked(val)
					checkbox.stateChanged.connect(lambda checked, path=path: self.prefs.write_prefs(path, bool(checked)))				
					checkbox.setToolTip(tooltip)

					general_tab.layout().addRow(checkbox)

		general_tab = QWidget()
		general_tab.setLayout(FormLayout())

		create_widgets(self.prefs.file["settings"])

		return ScrollArea(general_tab)

	def get_color_dialog(self, default_color: str=None, title: str="Pick a color"):
		"""Open a color picker dialog and return it's hex, if no selected color return an empty string.
		"""
		if default_color is None:
			if self.prefs.file["theme"] == "light":
				default_color = "#000000"
			else:
				default_color = "#ffffff"

		color = QColorDialog.getColor(QColor(default_color), title=title, parent=self)

		if not QColor.isValid(color):
			return ""

		return color.name()

	def create_theme_tab(self):
		def get_type_color(button, display_name: str="", default_type: str="",  default_color: str=None, write_in_prefs: bool=True):
			if default_color is None:
				if self.prefs.file["theme"] == "light":
					default_color = "#000000"
				else:
					default_color = "#ffffff"

			color = self.get_color_dialog(default_color=default_color)

			if color == "":
				return

			button.setText(color)
			button.setStyleSheet(f"color: {color};")

			if write_in_prefs:
				self.prefs.write_prefs(f"colors/{display_name}", (default_type, color))
		
		def add_color_pattern_item(edit=False, default_display_name: str="", default_type: str="", default_type_color: str=None):
			def add_btn_clicked():
				if display_name_input.text().strip() == "":
					QMessageBox.critical(self, "Empty Display Name", "You cannot have an item with an emtpy display name.")
					return

				if type_input.text().strip() == "":
					QMessageBox.critical(self, "Empty Type", "You cannot have an item with an emtpy type.")
					return
					
				try:
					interpret_type(type_input.text())
				except AttributeError:
					QMessageBox.critical(
						self, 
						"Invalid Type", 
						"Given type is invalid, make sure there are no typos and the type exists."
					)
					return

				dialog.done(1)
			
			if default_type_color is None:
				if self.prefs.file["theme"] == "light":
					default_type_color = "#000000"
				else:
					default_type_color = "#ffffff"

			dialog = QDialog(self)

			dialog.setWindowTitle("Add item" if not edit else "Edit item")
			dialog.setLayout(QVBoxLayout())

			# Inputs
			inputs_widget = QWidget()
			inputs_widget.setLayout(QHBoxLayout())

			display_name_input = QLineEdit(default_display_name)
			display_name_input.setPlaceholderText("Display Name")
			display_name_input.setToolTip("Name to Display")
			
			type_input = QLineEdit(default_type)
			type_input.setPlaceholderText("Type")
			type_input.setToolTip("Python Type (types library available)")
				
			color_button = QPushButton(default_type_color)
			color_button.setStyleSheet(f"color: {default_type_color};")
			color_button.clicked.connect(lambda: get_type_color(color_button, default_color=stylesheet_to_dict(color_button.styleSheet())["color"], write_in_prefs=False))

			inputs_widget.layout().addWidget(display_name_input)
			inputs_widget.layout().addWidget(type_input)			
			inputs_widget.layout().addWidget(color_button)

			# Buttons
			buttons_widget = QWidget()
			buttons_widget.setLayout(QHBoxLayout())

			add_btn = QPushButton(self.style().standardIcon(QStyle.SP_DialogApplyButton), "Add" if not edit else "Edit")
			add_btn.clicked.connect(add_btn_clicked)

			cancel_bnt = QPushButton(self.style().standardIcon(QStyle.SP_DialogCancelButton), "Cancel")
			cancel_bnt.clicked.connect(lambda: dialog.done(0))

			buttons_widget.layout().addWidget(add_btn)
			buttons_widget.layout().addWidget(cancel_bnt)

			# Add widgets
			dialog.layout().addWidget(inputs_widget)
			dialog.layout().addWidget(buttons_widget)

			dialog.setFixedSize(dialog.sizeHint().width() + 30, dialog.sizeHint().height())

			return dialog.exec_(), display_name_input.text(), type_input.text(), color_button.text() 

		def create_color_pattern_item(display_name: str, type_: str, type_color: str):
			def edit_button_clicked():
				nonlocal display_name, type_, type_color

				answer, new_display_name, new_type, new_type_color = add_color_pattern_item(default_display_name=display_name, default_type=type_, default_type_color=self.prefs.file["colors"][display_name][1], edit=True) # if add: 1; else: 0
				if not answer: # if answer == 0
					return

				if not new_display_name == display_name: # Remove the old key if it is not equal to the new one
					self.prefs.write_prefs(f"colors", remove_key_from_dict(self.prefs.file["colors"], display_name))

				self.prefs.write_prefs(f"colors/{new_display_name}", (new_type, new_type_color))

				color_pattern_label.setText(new_display_name)
				color_button.setText(new_type_color)
				color_button.setStyleSheet(f"color: {new_type_color};")

				display_name = new_display_name
				type_ = new_type

			def remove_color_pattern_item():
				self.prefs.write_prefs(f"colors", remove_key_from_dict(self.prefs.file["colors"], display_name))

				color_pattern_item.setParent(None)

			color_pattern_item = QWidget()
			color_pattern_item.setLayout(QHBoxLayout())
			color_pattern_item.layout().setSpacing(5)

			color_pattern_label = QLabel(display_name)
			color_pattern_label.setStyleSheet("margin-right: 0px;")

			color_button = QPushButton(type_color)
			color_button.setStyleSheet(f"color: {type_color};")

			color_button.clicked.connect(lambda ignore: get_type_color(color_button, display_name, self.prefs.file["colors"][display_name][0], self.prefs.file["colors"][display_name][1]))

			edit_icon = QIcon(f":/img/edit_icon_{self.prefs.file['theme']}.png")
			edit_icon_size = min(edit_icon.availableSizes())

			edit_button = QPushButton(icon=edit_icon)
			edit_button.setFixedWidth(edit_icon_size.width())

			edit_button.clicked.connect(edit_button_clicked)

			remove_button = QPushButton(icon=self.style().standardIcon(QStyle.SP_DialogNoButton))
			remove_button.setFixedWidth(edit_icon_size.width())			
			remove_button.clicked.connect(remove_color_pattern_item)

			color_pattern_item.layout().addWidget(color_pattern_label)
			color_pattern_item.layout().addWidget(color_button)
			color_pattern_item.layout().addWidget(edit_button)			
			color_pattern_item.layout().addWidget(remove_button)

			return color_pattern_item

		def create_add_button():
			def add_button_clicked():
				answer, display_name, type_, type_color = add_color_pattern_item() # if add: 1; else: 0
				if not answer: # if answer == 0
					return

				self.prefs.write_prefs(f"colors/{display_name}", (type_, type_color))

				color_pattern_widget.layout().insertWidget(color_pattern_widget.layout().count() - 2, create_color_pattern_item(display_name, type_, type_color))

			add_btn = QPushButton("+")
			add_btn.clicked.connect(add_button_clicked)

			return add_btn

		def dark_theme_toggled(state):
			self.prefs.write_prefs("cache/theme", 'dark' if bool(state) else 'light')

		theme_tab = QWidget()
		theme_tab.setLayout(FormLayout(stretch=False))

		dark_theme_toggle = AnimatedToggle()
		
		if self.prefs.file["theme"] == "light":
			state = 0
		elif self.prefs.file["theme"] == "dark":
			state = 1
			
		dark_theme_toggle.stateChanged.connect(dark_theme_toggled)
		dark_theme_toggle.setCheckState(state)
		self.widgets["dark_theme_toggle"].append(dark_theme_toggle)

		color_pattern_widget = QWidget()
		color_pattern_widget.setLayout(QVBoxLayout())
		color_pattern_widget.layout().setSpacing(0)

		color_pattern_title = QLabel("Color Pattern<hr>")
		color_pattern_title.setToolTip("Set the color of each type")
		color_pattern_title.setStyleSheet("margin-bottom: 0px;")

		for display_name, (type_, type_color) in self.prefs.file["colors"].items():
			"""
			colors=>
				Classes=("type", "#a6e22e")

			So display_name will be "Classes". type_ "type" and type_color will be "#a6e22e" (str).
			"""
			color_pattern_widget.layout().addWidget(create_color_pattern_item(display_name, type_, type_color))

		color_pattern_widget.layout().addWidget(create_add_button())
		color_pattern_widget.layout().addStretch(2)

		theme_tab.layout().addRow("Dark Theme: ", dark_theme_toggle)
		theme_tab.layout().addRow(color_pattern_title)
		theme_tab.layout().addRow(ScrollArea(color_pattern_widget))

		return theme_tab
