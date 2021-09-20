import sys
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

if __name__ == "__main__":
    import collapsible_widget_resources
else:
    import GUI.collapsible_widget_resources

VERTICAL_ARROW_PATH = ":/vertical_arrow_collapsible.png"
HORIZONTAL_ARROW_PATH = ":/horizontal_arrow_collapsible.png"

class CollapsibleWidget(QWidget):
    def __init__(self, 
        THEME, 
        current_theme, 
        title: str=None, 
        color=None,
        parent: QWidget=None
    ):
        super().__init__()
        

        self.THEME = THEME
        self.current_theme = current_theme

        self.is_collapsed = True

        if color is None:
            color = self.THEME[self.current_theme]["font_color"]
        
        self.title_frame = self.CollapseButton(title, color, self.is_collapsed, parent=self)
        self.title_frame.clicked.connect(self.toggle_collapsed)

        self.setParent(parent)

        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(5, 0, 5, 0)    

        self.layout().addWidget(self.title_frame, Qt.AlignTop)
        self.layout().addWidget(self.init_content())

    def init_content(self):
        self.content = QWidget()
        self.content_layout = QVBoxLayout()

        self.content.setLayout(self.content_layout)
        self.content.setVisible(not self.is_collapsed)

        return self.content

    def addWidget(self, widget: QWidget):
        self.content_layout.addWidget(widget)
   
    def toggle_collapsed(self):
        self.content.setVisible(self.is_collapsed)
        self.is_collapsed = not self.is_collapsed
        self.title_frame.update_arrow(self.is_collapsed)

    def collapse(self):
        self.is_collapsed = True

        self.content.setVisible(False)
        self.title_frame.update_arrow(self.is_collapsed)

    def uncollapse(self):
        self.is_collapsed = False

        self.content.setVisible(True)
        self.title_frame.update_arrow(self.is_collapsed)

    class CollapseButton(QPushButton):
        def __init__(self, title: str="", color: str=None, is_collapsed: bool=True, parent: QWidget=None):
            super().__init__()

            self.setParent(parent)
            self.setText(title)
            self.update_arrow()

            self.setStyleSheet(
            f"""
            *{{
                padding: 3px 5px 3px 5px;
                text-align: left;
                color: {color};
                border: none;
                background-color: {parent.THEME[parent.current_theme]["background_color"]};
            }}
            *:hover {{
                background-color: {parent.THEME[parent.current_theme]["collapsible"]["background_color_hover"]};
            }}
            """
            )


        def update_arrow(self, is_collapsed: bool=True):
        	if is_collapsed:
	            self.setIcon(QIcon(HORIZONTAL_ARROW_PATH))
	        elif not is_collapsed:
	            self.setIcon(QIcon(VERTICAL_ARROW_PATH))

