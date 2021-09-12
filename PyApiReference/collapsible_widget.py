import sys
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import collapsible_widget_resources

VERTICAL_ARROW_PATH = ":/vertical_arrow_collapsible.png"
HORIZONTAL_ARROW_PATH = ":/horizontal_arrow_collapsible.png"

class CollapsibleWidget(QWidget):
    def __init__(self, title=None, parent=None):
        super().__init__()
        
        self.is_collasped = True

        self.title_frame = self.CollapseButton(title, self.is_collasped)        
        self.title_frame.clicked.connect(self.toggle_collapsed)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.title_frame)
        self.layout().addWidget(self.init_content())

    def init_content(self):
        self.content = QWidget()
        self.content_layout = QVBoxLayout()

        self.content.setLayout(self.content_layout)
        self.content.setVisible(not self.is_collasped)

        return self.content

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)
   
    def toggle_collapsed(self):
        self.content.setVisible(self.is_collasped)
        self.is_collasped = not self.is_collasped
        self.title_frame.update_arrow(self.is_collasped)


    class CollapseButton(QPushButton):
        def __init__(self, title="", is_collasped=True, parent=None):
            super().__init__()

            self.setText(title)
            self.update_arrow()

            self.setStyleSheet(
            """
            *{
            	padding: 3px 5px 3px 5px;
            	text-align: left;
            	border: none;
            	background-color: #dcdee0;
            }
            *:hover {
            	background-color: #c7cccf;
            }
            """
            )


        def update_arrow(self, is_collasped=True):
        	if is_collasped:
	            self.setIcon(QIcon(HORIZONTAL_ARROW_PATH))
	        elif not is_collasped:
	            self.setIcon(QIcon(VERTICAL_ARROW_PATH))

