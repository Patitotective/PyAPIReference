from PyQt5.QtWidgets import QWidget, QLabel, QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QStyle, QComboBox, QTabWidget, QFormLayout, QColorDialog, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from qtwidgets import AnimatedToggle
from multipledispatch import dispatch
import PREFS

if __name__ == "__main__":
	from scrollarea import ScrollArea
else:
	from GUI.scrollarea import ScrollArea

class FormLayout(QGridLayout):
	"""This layout will work as QFormLayout but this will center the two columns vertically.
	QFormLayout:
		--- ___
	This:
		--- ---
	"""
	def __init__(self, stretch=True, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.stretch = stretch
		self.row = 0

	def addRowEvent(self):
		"""This function is called whenever a row is added.
		"""
		if self.stretch: self.setRowStretch(self.row, 0)
		self.row += 1
		if self.stretch: self.setRowStretch(self.row, 1)

	@dispatch(QWidget, QWidget)
	def addRow(self, widget1: QWidget, widget2: QWidget):		
		self.addWidget(widget1, self.row, 0)
		self.addWidget(widget2, self.row, 1)

		self.addRowEvent()

	@dispatch(str, QWidget)
	def addRow(self, string: str, widget: QWidget):
		self.addWidget(QLabel(string), self.row, 0)
		self.addWidget(widget, self.row, 1)

		self.addRowEvent()
	
	@dispatch(QWidget, str)
	def addRow(self, string: str, widget: QWidget):
		self.addWidget(widget, self.row, 0)
		self.addWidget(QLabel(string), self.row, 1)

		self.addRowEvent()

	@dispatch(QWidget)
	def addRow(self, widget: QWidget):
		self.addWidget(widget, self.row, 0, 1, 0)
		
		self.addRowEvent()

	@dispatch(str)
	def addRow(self, string: str):
		self.addWidget(QLabel(string), self.row, 0, 1, 0)
		
		self.addRowEvent()

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

		tabs.addTab(self.create_theme_tab(), "Theme")

		apply_button = QPushButton(icon=self.style().standardIcon(QStyle.SP_DialogApplyButton), text="Apply")
		apply_button.clicked.connect(lambda: self.done(1))

		self.layout().addRow(tabs)
		self.layout().addRow(apply_button)
	
	def create_theme_tab(self):
		def dark_theme_toggle_changed(state: int):
			if state == 0:
				self.prefs.write_prefs("theme", "light")
			elif state == 2:
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
