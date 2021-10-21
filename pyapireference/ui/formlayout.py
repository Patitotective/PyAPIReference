from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from multipledispatch import dispatch

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

	@dispatch(str, str)
	def addRow(self, string1: str, string2: str):
		self.addWidget(QLabel(string1), self.row, 0)
		self.addWidget(QLabel(string2), self.row, 1)

		self.addRowEvent()

	@dispatch(QWidget)
	def addRow(self, widget: QWidget):
		self.addWidget(widget, self.row, 0, 1, 0)
		
		self.addRowEvent()

	@dispatch(str)
	def addRow(self, string: str):
		self.addWidget(QLabel(string), self.row, 0, 1, 0)
		
		self.addRowEvent()
