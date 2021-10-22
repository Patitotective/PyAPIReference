from PyQt5.QtWidgets import QWidget, QDialog, QLabel, QPushButton, QGridLayout, QStyle
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt

if __name__ == "__main__":
	from scrollarea import ScrollArea
else:
	from pyapireference.ui.scrollarea import ScrollArea

class WarningDialog(QDialog):
	def __init__(self, title: str, text: str, yes_btn_callback: callable=1, yes_btn_text: str="Yes", no_btn_callback: callable=0, no_btn_text: str="No", icon_size: (tuple, list)=(60, 60), parent=None, safe_dialog=(False, None)):
		super().__init__(parent=parent)

		self.setWindowTitle(title)
		self.setLayout(QGridLayout())

		icon = self.style().standardIcon(QStyle.SP_MessageBoxWarning)
		icon_label = QLabel()

		pixmap = QPixmap(icon.pixmap(QSize(*icon_size)))
		icon_label.setPixmap(pixmap)
		
		yes_btn = QPushButton(self.style().standardIcon(QStyle.SP_DialogApplyButton), yes_btn_text)
		yes_btn.clicked.connect(lambda: self.done(yes_btn_callback))

		no_btn = QPushButton(self.style().standardIcon(QStyle.SP_DialogCancelButton), no_btn_text)
		no_btn.clicked.connect(lambda: self.done(no_btn_callback))

		text_label = QLabel(text)
		text_label.setAlignment(Qt.AlignTop)
		text_scrollarea = ScrollArea(text_label)

		if safe_dialog[0]:
			more_info_label = QLabel(f'''
				<p>
					<a href="https://stackoverflow.com/questions/419163/what-does-if-name-main-do/419185#419185" style="color:{safe_dialog[1]}">More Info</a>
				</p>'''
				)

			more_info_label.setOpenExternalLinks(True)
			continue_label = QLabel("Would you still like to continue?")

			self.layout().addWidget(icon_label, 0, 0)
			self.layout().addWidget(text_label, 0, 1, len(text.split("\n")), 2)
			self.layout().addWidget(more_info_label, len(text.split("\n")) + 1, 1)
			self.layout().addWidget(QLabel(""), len(text.split("\n")) + 2, 1)
			self.layout().addWidget(continue_label, len(text.split("\n")) + 3, 1)

			self.layout().addWidget(yes_btn, len(text.split("\n")) + 4, 1)
			self.layout().addWidget(no_btn, len(text.split("\n")) + 4, 2)

		else:
			self.layout().addWidget(icon_label, 0, 0)
			self.layout().addWidget(text_scrollarea, 0, 1, 0, 2)

			self.layout().addWidget(yes_btn, 1, 1)
			self.layout().addWidget(no_btn, 1, 2)

		self.setMaximumSize(self.sizeHint())