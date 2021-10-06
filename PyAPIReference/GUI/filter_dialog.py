from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QDialog, QPushButton, QStyle, QWidget, QCheckBox, QHBoxLayout, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

if __name__ == "__main__":
    raise RuntimeError("button_with_extra_options.py requires get_text_size from extra.py which is outside this folder, you can't run this script as main")
else:
	from GUI.collapsible_widget import CollapsibleWidget, CheckBoxCollapseButton
	from GUI.formlayout import FormLayout
	from GUI.scrollarea import ScrollArea
	from extra import get_text_size, remove_key_from_dict

class FilterDialog(QDialog):
	def __init__(self, prefs, title="Filter", parent=None):
		super().__init__(parent=parent)

		self.prefs = prefs

		self.setWindowTitle(title)

		self.setLayout(QVBoxLayout())
		self.create_widgets()

		self.setFixedSize(self.sizeHint().width() + 50, self.sizeHint().height() + 100)

	def create_filter(self, filter_: dict=None):
		def add_filter_item_dialog(edit=False, display_name: str="", type_: str=""):
			dialog = QDialog(self)

			dialog.setWindowTitle("Add filter" if not edit else "Edit filter")
			dialog.setLayout(QVBoxLayout())

			# Inputs
			inputs_widget = QWidget()
			inputs_widget.setLayout(QHBoxLayout())

			display_name_input = QLineEdit(display_name)
			display_name_input.setPlaceholderText("Display name")
			display_name_input.setToolTip("Name to display")
			
			type_input = QLineEdit(type_)
			type_input.setPlaceholderText("Type")
			type_input.setToolTip("Python type (types library available)")

			inputs_widget.layout().addWidget(display_name_input)
			inputs_widget.layout().addWidget(type_input)

			# Buttons
			buttons_widget = QWidget()
			buttons_widget.setLayout(QHBoxLayout())

			add_btn = QPushButton(self.style().standardIcon(QStyle.SP_DialogApplyButton), "Add" if not edit else "Edit")
			add_btn.clicked.connect(lambda: dialog.done(1))

			cancel_bnt = QPushButton(self.style().standardIcon(QStyle.SP_DialogCancelButton), "Cancel")
			cancel_bnt.clicked.connect(lambda: dialog.done(0))

			buttons_widget.layout().addWidget(add_btn)
			buttons_widget.layout().addWidget(cancel_bnt)

			# Add widgets
			dialog.layout().addWidget(inputs_widget)
			dialog.layout().addWidget(buttons_widget)

			dialog.setFixedSize(dialog.sizeHint().width() + 30, dialog.sizeHint().height())

			return dialog.exec_(), display_name_input.text(), type_input.text() 
		
		def create_add_button():
			def add_button_clicked():
				answer, display_name, type_ = add_filter_item_dialog() # if add: 1; else: 0
				if not answer: # if answer == 0
					return

				if display_name.strip() == "":
					QMessageBox.critical(self, "Emtpy display name", "Cannot add a filter with an empty display name")
					return
				if type_.strip() == "":
					QMessageBox.critical(self, "Emtpy type", "Cannot add a filter with an empty type")
					return
					
				self.prefs.write_prefs(f"filter/{display_name}", (type_, True))

				filter_widget.layout().insertWidget(filter_widget.layout().count() - (constant_filter_count + 2), create_filter_item(display_name, type_, True))

			add_btn = QPushButton("+")
			add_btn.clicked.connect(add_button_clicked)

			return add_btn

		def create_filter_item(filter_name: str, filter_type: str, filter_checked: bool):
			def edit_button_clicked():
				nonlocal filter_name, filter_type

				answer, display_name, type_ = add_filter_item_dialog(display_name=filter_name, type_=filter_type, edit=True) # if add: 1; else: 0
				if not answer: # if answer == 0
					return

				if not display_name == filter_name:
					self.prefs.write_prefs(f"filter", remove_key_from_dict(self.prefs.file["filter"], filter_name))

				self.prefs.write_prefs(f"filter/{display_name}", (type_, True))

				filter_checkbox.setText(display_name)

				filter_name = display_name
				filter_type = type_

			def remove_filter():
				self.prefs.write_prefs(f"filter", remove_key_from_dict(self.prefs.file["filter"], filter_name))

				filter_item.setParent(None)

			filter_item = QWidget()
			filter_item.setLayout(QHBoxLayout())

			filter_checkbox = QCheckBox(filter_name)
			filter_checkbox.setChecked(filter_checked)
			filter_checkbox.stateChanged.connect(lambda state, filter_name=filter_name, filter_type=filter_type, filter_checkbox=filter_checkbox: self.prefs.write_prefs(f"filter/{filter_name}", (filter_type, bool(filter_checkbox.checkState()))))

			edit_icon = QIcon(f"Images/edit_icon_{self.prefs.file['theme']}.png")#nutrition_tab.style().standardIcon(QStyle.SP_FileDialogInfoView)
			edit_icon_size = min(edit_icon.availableSizes())

			filter_edit_button = QPushButton(icon=edit_icon)
			filter_edit_button.setFixedWidth(edit_icon_size.width())

			filter_edit_button.clicked.connect(edit_button_clicked)

			remove_filter_btn = QPushButton(icon=self.style().standardIcon(QStyle.SP_DialogNoButton))
			remove_filter_btn.setFixedWidth(edit_icon_size.width())			
			remove_filter_btn.clicked.connect(remove_filter)

			filter_item.layout().addWidget(filter_checkbox)
			filter_item.layout().addWidget(filter_edit_button)
			filter_item.layout().addWidget(remove_filter_btn)

			return filter_item

		def create_constant_filter_item(filter_name: str, filter_type: str, filter_checked: bool):
			filter_item = QWidget()
			filter_item.setLayout(QHBoxLayout())

			filter_checkbox = QCheckBox(filter_name)
			filter_checkbox.setChecked(filter_checked)
			filter_checkbox.stateChanged.connect(lambda state, filter_name=filter_name, filter_checkbox=filter_checkbox: self.prefs.write_prefs(f"filter/{filter_name}", (filter_type, bool(filter_checkbox.checkState()))))
			
			filter_item.layout().addWidget(filter_checkbox)

			return filter_item

		if filter_ is None:
			filter_ = self.prefs.file["filter"]

		filter_widget = QWidget()
		filter_widget.setLayout(QVBoxLayout())
		filter_widget.layout().setSpacing(0)

		constant_filter_count = 0

		for filter_name, (filter_type, filter_checked) in filter_.items():
			
			if filter_type[0] == "#":
				filter_item = create_constant_filter_item(filter_name, filter_type, filter_checked)
				filter_widget.layout().addWidget(filter_item)

				constant_filter_count += 1
				continue

			filter_item = create_filter_item(filter_name, filter_type, filter_checked)
			filter_widget.layout().addWidget(filter_item)

		filter_widget.layout().addWidget(create_add_button())
		filter_widget.layout().addStretch(2)

		return ScrollArea(filter_widget)

	def create_widgets(self):
		filter_widget = self.create_filter()

		apply_button = QPushButton(icon=self.style().standardIcon(QStyle.SP_DialogApplyButton), text="Apply")
		apply_button.clicked.connect(lambda: self.done(1))

		self.layout().addWidget(filter_widget)
		self.layout().addWidget(apply_button)

	@classmethod
	def checkbox_clicked(cls, obj):
		if obj in cls.filters:
			cls.filters.pop(cls.filters.index(obj))
		else:
			cls.filters.append(obj)
