import os
import PREFS

from PyQt5.QtWidgets import QDialog, QPushButton, QWidget, QTextEdit, QGridLayout, QLineEdit
from PyQt5.QtCore import Qt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from cryptography.fernet import Fernet

class BugDialog(QDialog):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.setLayout(QGridLayout())

		self.setWindowTitle("Report a Bug")

		self.title_input = QLineEdit()
		self.title_input.setPlaceholderText("Title")

		self.description_input = QTextEdit()
		self.description_input.setPlaceholderText("Description")

		send_btn = QPushButton("Send")
		send_btn.clicked.connect(self.send)

		cancel_btn = QPushButton("Cancel")
		cancel_btn.clicked.connect(lambda: self.done(0))

		self.layout().addWidget(self.title_input, 0, 0, 1, 0)
		self.layout().addWidget(self.description_input, 1, 0, 1, 2)
		self.layout().addWidget(send_btn, 2, 0)
		self.layout().addWidget(cancel_btn, 2, 1)

	def send(self):
		info = PREFS.read_prefs_file(f"Prefs{os.sep}info.prefs")
		f = Fernet(info["key"].decode())
		API = f.decrypt(info["api"]).decode()
		EMAIL = info["email"]

		message = Mail(
			from_email=EMAIL,
			to_emails=EMAIL,
			subject="Bug Report",
			html_content=f'''
						<strong> New Bug Report </strong><br>
						<span>
						Title: {self.title_input.text()}<br>
						Description: {self.description_input.toPlainText()}
						</span>
						'''
		)				

		try:
			sg = SendGridAPIClient(API)
			response = sg.send(message)
			print(response.status_code)
			print(response.body)
			print(response.headers)
		except Exception as e:
			print(e.message)

		self.done(1)

