import sys
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QMainWindow, QMenu, QAction, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor

if __name__ == "__main__":
    raise RuntimeError("This module requires extra.py module which is outside this folder, you can't run this script as main")
else:
    import pyapireference.ui.collapsible_widget_resources
    from pyapireference.extra import get_widgets_from_layout, create_menu

VERTICAL_ARROW_PATH = ":/vertical_arrow_collapsible.png"
HORIZONTAL_ARROW_PATH = ":/horizontal_arrow_collapsible.png"


class CollapseButton(QWidget):
    def __init__(self, title: str="", color: str=None, is_collapsed: bool=True, parent: QWidget=None):
        super().__init__(parent=parent)

        self.parent = parent

        self.setLayout(QHBoxLayout())
        self.setObjectName("CollapseButton")

        self.button = QPushButton(title)
        self.layout().addWidget(self.button)
        self.update_arrow()

        self.setStyleSheet(
        f"""  
        QPushButton {{
            text-align: left; 
            padding: 3px 5px 3px 5px; 
            color: {color if color is not None else ''};
        }}
        """)

    def update_arrow(self, is_collapsed: bool=True):
        if is_collapsed:
            self.button.setIcon(QIcon(HORIZONTAL_ARROW_PATH))
        elif not is_collapsed:
            self.button.setIcon(QIcon(VERTICAL_ARROW_PATH))


class CheckBoxCollapseButton(CollapseButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(30, 30)
        self.checkbox.setChecked(True)
        self.checkbox.setToolTip(f"Include {self.parent.title} in Markdown?")

        self.layout().addWidget(self.checkbox)


class CollapsibleWidget(QWidget):
    def __init__(self, 
        title: str=None, 
        color=None, 
        collapse_button: QWidget=CollapseButton, 
        parent: QWidget=None
    ):
        super().__init__(parent=parent)
        
        self.parent = parent

        self.title = title

        self.is_collapsed = True

        self.title_frame = collapse_button(title, color, self.is_collapsed, parent=self)
        self.title_frame.button.clicked.connect(self.toggle_collapsed)

        self.title_frame.setContextMenuPolicy(Qt.CustomContextMenu)
        self.title_frame.customContextMenuRequested.connect(self.context_menu)
    
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)    

        self.layout().addWidget(self.title_frame, Qt.AlignTop)
        self.layout().addWidget(self.init_content())

    def context_menu(self):
        menu = create_menu(
            {
                "Fold": {
                    "callback": self.collapse, 
                }, 
                "Unfold": {
                    "callback": self.uncollapse, 
                }, 
                "Fold all": {
                    "callback": self.fold_all, 
                }, 
                "Unfold all": {
                    "callback": self.unfold_all, 
                }, 
                "Check all": {
                    "callback": self.enable_all_checkboxes, 
                }, 
                "Uncheck all": {
                    "callback": self.disable_all_checkboxes, 
                }, 
            }, 
            parent=self.parent
        )

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

    def disable_all_checkboxes(self):
        """This function will disable all child collapsible objects checkboxes if CollapseButton == CheckBoxCollapseButton
        """
        if isinstance(self.title_frame, CheckBoxCollapseButton):
            self.disable_checkbox()

        for widget in get_widgets_from_layout(self.content_layout):
            if isinstance(widget, CollapsibleWidget):
                if isinstance(widget.title_frame, CheckBoxCollapseButton):
                    widget.disable_all_checkboxes()
    
    def enable_all_checkboxes(self):
        """This function will enable all child collapsible objects checkboxes if CollapseButton == CheckBoxCollapseButton
        """
        if isinstance(self.title_frame, CheckBoxCollapseButton):
            self.enable_checkbox()

        for widget in get_widgets_from_layout(self.content_layout):
            if isinstance(widget, CollapsibleWidget):
                if isinstance(widget.title_frame, CheckBoxCollapseButton):
                    widget.enable_all_checkboxes()

    def disable_checkbox(self):
        self.title_frame.checkbox.setChecked(False)

    def enable_checkbox(self):
        self.title_frame.checkbox.setChecked(True)

    def tree_to_dict(self, collapsible_widget=None, include_title: bool=True):
        """This will convert the tree of collapsible widgets into a dictionary.
        """
        if collapsible_widget is None:
            collapsible_widget = self
        
        if not isinstance(collapsible_widget, CollapsibleWidget):
            return

        layout = collapsible_widget.content_layout

        content = {"collapsed": collapsible_widget.is_collapsed}
        if isinstance(collapsible_widget.title_frame, CheckBoxCollapseButton):
            content["checked"] = bool(collapsible_widget.title_frame.checkbox.checkState())

        collapsible_widgets_with_checkbox_counter = 0
        widgets = get_widgets_from_layout(layout) # widgets on collapsible widgets layout

        for widget in widgets:
            if isinstance(widget, CollapsibleWidget):
                content[widget.title] = self.tree_to_dict(widget, include_title=False)

        return {self.title: content} if include_title else content
