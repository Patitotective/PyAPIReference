import sys
from PyQt5.QtWidgets import QFrame, QWidget, QLayout, QVBoxLayout, QLabel, QPushButton, QApplication, QMainWindow, QMenu, QAction, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor

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
        super().__init__(parent=parent)
        
        self.parent = parent

        self.THEME = THEME
        self.current_theme = current_theme

        self.is_collapsed = True

        if color is None:
            color = self.THEME[self.current_theme]["font_color"]
        
        self.title_frame = CollapseButton(title, color, self.is_collapsed, parent=self)
        self.title_frame.button.clicked.connect(self.toggle_collapsed)

        self.title_frame.setContextMenuPolicy(Qt.CustomContextMenu)
        self.title_frame.customContextMenuRequested.connect(self.context_menu)
    
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)    

        self.layout().addWidget(self.title_frame, Qt.AlignTop)
        self.layout().addWidget(self.init_content())

    def context_menu(self):
        menu = QMenu(self.parent)
        fold_action = QAction("Fold")
        fold_action.triggered.connect(self.collapse)
        
        unfold_action = QAction("Unfold")
        unfold_action.triggered.connect(self.uncollapse)

        fold_all_action = QAction("Fold all")
        fold_all_action.triggered.connect(lambda ignore: self.fold_all())
        
        unfold_all_action = QAction("Unfold all")
        unfold_all_action.triggered.connect(lambda ignore: self.unfold_all())
           
        menu.addAction(fold_action)
        menu.addAction(unfold_action)
           
        menu.addAction(fold_all_action)
        menu.addAction(unfold_all_action)

        menu.exec_(QCursor.pos())

    def fold_all(self):
        for widget in get_widgets_from_layout(self.content_layout):
            if isinstance(widget, CollapsibleWidget):
                widget.collapse()

    def unfold_all(self):
        for widget in get_widgets_from_layout(self.content_layout):
            if isinstance(widget, CollapsibleWidget):
                widget.uncollapse()

        self.uncollapse()

    def init_content(self):
        self.content = QWidget()
        self.content_layout = QVBoxLayout()

        self.content.setLayout(self.content_layout)
        self.content.setVisible(not self.is_collapsed)

        return self.content

    def addWidget(self, widget: QWidget):
        widget.setContentsMargins(10, 0, 0, 0) # To representate indentation
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

class CollapseButton(QWidget):
    def __init__(self, title: str="", color: str=None, is_collapsed: bool=True, parent: QWidget=None):
        super().__init__(parent=parent)

        self.setLayout(QHBoxLayout())

        self.button = QPushButton(title)
        self.layout().addWidget(self.button)
        self.update_arrow()

        self.setStyleSheet(f"text-align: left; padding: 3px 5px 3px 5px; color: {color};")
        # self.setStyleSheet(
        # f"""
        # *{{
        #     color: {color};
        #     border: none;
        #     background-color: {parent.THEME[parent.current_theme]["background_color"]};
        # }}
        # *:hover {{
        #     background-color: {parent.THEME[parent.current_theme]["collapsible"]["background_color_hover"]};
        # }}
        # """
        # )


    def update_arrow(self, is_collapsed: bool=True):
        if is_collapsed:
            self.button.setIcon(QIcon(HORIZONTAL_ARROW_PATH))
        elif not is_collapsed:
            self.button.setIcon(QIcon(VERTICAL_ARROW_PATH))

class CheckBoxCollapseButton(CollapseButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.checkbox = QCheckBox(self.button)
        #self.checkbox.setFixedWidth(self.checkbox.sizeHint().width() * 2)        
        #self.layout().addWidget(self.checkbox)
        #self.layout().addStretch()

def get_widgets_from_layout(layout: QLayout, widget_type: QWidget=QWidget, exact_type: bool=False) -> iter:
    for indx in range(layout.count()):
        widget = layout.itemAt(indx).widget()
        
        if not isinstance(widget, widget_type) and not exact_type:
            continue
        elif not type(widget) is widget_type and exact_type:
            continue

        yield widget
