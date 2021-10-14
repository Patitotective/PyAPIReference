import sys
from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
	def __init__(self, version, link_color: str=None, parent=None):
		super().__init__(parent=parent)

		self.setWindowTitle("About PyAPIReference")
		about_layout = QGridLayout()
		self.setLayout(about_layout)

		icon_label = QLabel()
		icon = QPixmap(":/Images/about_icon.png")
		icon_label.setAlignment(Qt.AlignLeft)
		icon_label.setPixmap(icon)

		message_label = QLabel()
		message_label2 = QLabel()
		message_label3 = QLabel()

		message_label.setOpenExternalLinks(True)
		message_label3.setOpenExternalLinks(True)

		if link_color is None:
			link_color = ""

		message = f'''
			<p>
				PyAPIReference is a GUI application<br>to generate API References for Python modules.
			</p>
			<p>
				Learn more at our <a href="https://patitotective.github.io/PyAPIReference/" style="color:{link_color}">website</a>.
				<br>
				Join our <a href="https://discord.com/invite/as85Q4GnR6" style="color:{link_color}">Discord</a> server to stay updated.
			</p>
		'''

		message2 = f"<p style='font-size: 13px;'>{version}</p>"
		message3 = f"<p style='font-size: 13px;text-align: right'><a href='https://patitotective.github.io/PyAPIReference/' style='color:{link_color}'>Source Code</a></p>"

		message_label.setText(message)
		message_label2.setText(message2)
		message_label3.setText(message3)

		message_label.setAlignment(Qt.AlignLeft)
		message_label2.setAlignment(Qt.AlignLeft)
		message_label3.setAlignment(Qt.AlignRight)

		about_layout.addWidget(icon_label, 0, 0)
		about_layout.addWidget(message_label, 0, 1)

		about_layout.addWidget(message_label2, 1, 0)
		about_layout.addWidget(message_label3, 1, 1)

		self.setMaximumSize(self.sizeHint())

if __name__ == "__main__":
	app = QApplication(sys.argv)
	about_dialog = AboutDialog()
	about_dialog.exec_()

	sys.exit(app.exec_())
