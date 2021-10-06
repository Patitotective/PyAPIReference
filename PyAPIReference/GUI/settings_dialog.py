from PyQt5.QtWidgets import (
	QWidget, QLabel, 
	QDialog, QPushButton, 
	QVBoxLayout, QHBoxLayout, 
	QStyle, QComboBox, 
	QTabWidget, QFormLayout, 
	QColorDialog, QGridLayout, 
	QSpinBox, QDoubleSpinBox)

from PyQt5.QtGui import QColor

from qtwidgets import AnimatedToggle
import PREFS

if __name__ == "__main__":
    raise RuntimeError("settings_dialog.py requires to_sentence_case from extra.py which is outside this folder, you can't run this script as main")
else:
	from GUI.scrollarea import ScrollArea
	from GUI.formlayout import FormLayout
	from extra import to_sentence_case

class SettingsDialog(QDialog):
	def __init__(self, prefs, *args, title="Settings", parent=None, **kwargs):
		super().__init__(parent=parent, *args, **kwargs)

		self.prefs = prefs

		self.setWindowTitle(title)
		self.setLayout(QFormLayout())

		self.create_widgets()

		self.setFixedSize(300, 450)

	def create_widgets(self):
		tabs = QTabWidget()

		tabs.addTab(self.create_inspect_module_tab(), "Inspect module")
		tabs.addTab(self.create_theme_tab(), "Theme")

		apply_button = QPushButton(icon=self.style().standardIcon(QStyle.SP_DialogApplyButton), text="Apply")
		apply_button.clicked.connect(lambda: self.done(1))

		self.layout().addRow(tabs)
		self.layout().addRow(apply_button)
	
	def create_inspect_module_tab(self):
		inspect_module_tab = QWidget()
		inspect_module_tab.setLayout(FormLayout())

		for pref, pref_props in self.prefs.file["inspect"].items():
			val = pref_props["value"]
			tooltip = pref_props["tooltip"]

			if isinstance(val, (int, float)):
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
				spinbox.valueChanged.connect(lambda spinbox_val: self.prefs.write_prefs(f"inspect/{pref}/value", spinbox_val))
				spinbox.setToolTip(tooltip)

				inspect_module_tab.layout().addRow(f"{to_sentence_case(pref)}: ", spinbox)

		return inspect_module_tab

	def create_theme_tab(self):
		def dark_theme_toggle_changed(state: int):
			state = bool(state)
			if not state:
				self.prefs.write_prefs("theme", "light")
			elif state:
				self.prefs.write_prefs("theme", "dark")		

		def get_type_color(button, object_type, default_color, title="Pick a color", parent=None):
			color = QColorDialog.getColor(QColor(default_color), title=title, parent=parent)

			if not QColor.isValid(color):
				return

			button.setText(color.name())
			button.setStyleSheet(f"color: {color.name()};")

			self.prefs.write_prefs(f"colors/{object_type}", color.name())

		theme_tab = QWidget()
		theme_tab.setLayout(FormLayout(stretch=False))
	
		dark_theme_toggle = AnimatedToggle()
		if self.prefs.file["theme"] == "light":
			state = 0
		elif self.prefs.file["theme"] == "dark":
			state = 1
			
		dark_theme_toggle.setCheckState(state)
		dark_theme_toggle.stateChanged.connect(dark_theme_toggle_changed)

		color_pattern_widget = QWidget()
		color_pattern_widget.setLayout(FormLayout())

		for object_type, type_color in self.prefs.file["colors"].items():
			"""
			colors=>
				class="#a6e22e"

			So object_type will be class (str) and type_color will be "#a6e22e" (str).
			"""

			color_label = QLabel(object_type)
			color_button = QPushButton(type_color)
			color_button.setStyleSheet(f"color: {type_color};")

			color_button.clicked.connect(
				lambda ignore, 
				button=color_button, 
				object_type=object_type: 
				get_type_color(button, object_type, self.prefs.file["colors"][object_type], parent=self)
			)

			color_pattern_widget.layout().addRow(f"{object_type.capitalize()} color: ", color_button)

		theme_tab.layout().addRow("Dark theme: ", dark_theme_toggle)
		theme_tab.layout().addRow(ScrollArea(color_pattern_widget))

		return theme_tab
