from PyQt5.QtWidgets import QAction

def create_qaction(menu, text: str, shortcut: str="", callback: callable=lambda: print("No callback"), parent=None) -> QAction:
	"""This function will create a QAction and return it"""
	action = QAction(parent) # Create a qaction in the window (self)

	action.setText(text) # Set the text of the QAction 
	action.setShortcut(shortcut) # Set the shortcut of the QAction

	menu.addAction(action) # Add the action to the menu
	
	action.triggered.connect(callback) # Connect callback to callback argument

	return action # Return QAction
