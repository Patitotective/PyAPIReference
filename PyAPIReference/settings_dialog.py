from PyQt5.QtWidgets import QWidget, QLabel, QDialog, QPushButton, QFormLayout, QStyle
from PyQt5.QtCore import Qt
from qtwidgets import AnimatedToggle

def create_settings_dialog(prefs, *, title="Settings dialog", parent=None):
	def apply_changes():
		dark_theme_toggle_state = dark_theme_toggle.checkState()
		
		if dark_theme_toggle_state == 0:
			prefs.write_prefs("theme", "light")
		elif dark_theme_toggle_state == 2:
			prefs.write_prefs("theme", "dark")		

		dialog.done(1)

	dialog = QDialog(parent=parent)
	dialog.setWindowTitle(title)
	dialog.setLayout(QFormLayout())

	dark_theme_toggle = AnimatedToggle()
	if prefs.file["theme"] == "light":
		state = 0
	elif prefs.file["theme"] == "dark":
		state = 1
		
	dark_theme_toggle.setCheckState(state)

	apply_button = QPushButton(icon=dialog.style().standardIcon(QStyle.SP_DialogApplyButton), text="Apply")
	apply_button.clicked.connect(apply_changes)

	# Add widgets to layout
	dialog.layout().addRow("Dark theme: ", dark_theme_toggle)

	dialog.layout().addRow(apply_button)

	return dialog.exec_()
