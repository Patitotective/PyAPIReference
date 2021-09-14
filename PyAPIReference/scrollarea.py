from PyQt5.QtWidgets import QWidget,  QScrollBar, QScrollArea
from PyQt5.QtCore import Qt, QCoreApplication, QEvent

from enum import Enum, auto

class AutoScrollTypes(Enum):
	VERTICAL = auto()
	HORIZONTAL = auto()
	AUTOMATIC = auto()

class ScrollArea(QScrollArea):
	def __init__(self, main_widget: QWidget, parent: QWidget=None, auto_scroll: AutoScrollTypes=AutoScrollTypes.AUTOMATIC):
		super().__init__()
		
		self.auto_scroll = auto_scroll
		self.main_widget = main_widget

		self.horizontalScrollBar().setSingleStep(2)
		self.verticalScrollBar().setSingleStep(2)

		self.setWidget(main_widget)
		self.setWidgetResizable(True)
		self.set_stylesheet()

		main_widget.installEventFilter(self)

	def set_stylesheet(self):
		stylesheet = """
			QScrollArea {
				border: none;
			}
			/* --------------------------------------- QScrollBar  -----------------------------------*/
			QScrollBar:horizontal
			{
			    height: 15px;
			    margin: 3px 15px 3px 15px;
			    border: 1px transparent #2A2929;
			    border-radius: 4px;
			    background-color: #C4C4C4;    /* #2A2929; */
			}

			QScrollBar::handle:horizontal
			{
			    background-color: #807E7E;      /* #605F5F; */
			    min-width: 5px;
			    border-radius: 4px;
			}

			QScrollBar::handle:horizontal:hover
			{
				background-color: #605F5F;
			}

			QScrollBar::add-line:horizontal
			{
			    margin: 0px 3px 0px 3px;
			    border-image: url(:/qss_icons/rc/right_arrow_disabled.png);
			    width: 10px;
			    height: 10px;
			    subcontrol-position: right;
			    subcontrol-origin: margin;
			}

			QScrollBar::sub-line:horizontal
			{
			    margin: 0px 3px 0px 3px;
			    border-image: url(:/qss_icons/rc/left_arrow_disabled.png);
			    height: 10px;
			    width: 10px;
			    subcontrol-position: left;
			    subcontrol-origin: margin;
			}

			QScrollBar::add-line:horizontal:hover, QScrollBar::add-line:horizontal:on
			{
			    border-image: url(:/qss_icons/rc/right_arrow.png);
			    height: 10px;
			    width: 10px;
			    subcontrol-position: right;
			    subcontrol-origin: margin;
			}

			QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on
			{
			    border-image: url(:/qss_icons/rc/left_arrow.png);
			    height: 10px;
			    width: 10px;
			    subcontrol-position: left;
			    subcontrol-origin: margin;
			}

			QScrollBar:vertical
			{
			    background-color: #C4C4C4;
			    width: 15px;
			    margin: 15px 3px 15px 3px;
			    border: 1px transparent #2A2929;
			    border-radius: 4px;
			}

			QScrollBar::handle:vertical
			{
			    background-color: #807E7E;
			    min-width: 5px;
			    border-radius: 4px;
			}

			QScrollBar::handle:vertical:hover
			{
				background-color: #605F5F;
			}

			QScrollBar::sub-line:vertical
			{
			    margin: 3px 0px 3px 0px;
			    border-image: url(:/qss_icons/rc/up_arrow_disabled.png);
			    height: 10px;
			    width: 10px;
			    subcontrol-position: top;
			    subcontrol-origin: margin;
			}

			QScrollBar::add-line:vertical
			{
			    margin: 3px 0px 3px 0px;
			    border-image: url(:/qss_icons/rc/down_arrow_disabled.png);
			    height: 10px;
			    width: 10px;
			    subcontrol-position: bottom;
			    subcontrol-origin: margin;
			}

			QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on
			{
			    border-image: url(:/qss_icons/rc/up_arrow.png);
			    height: 10px;
			    width: 10px;
			    subcontrol-position: top;
			    subcontrol-origin: margin;
			}


			QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on
			{
			    border-image: url(:/qss_icons/rc/down_arrow.png);
			    height: 10px;
			    width: 10px;
			    subcontrol-position: bottom;
			    subcontrol-origin: margin;
			}

			QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical, QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal, QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal
			{
			    background: none;
			}
		"""

		self.setStyleSheet(stylesheet)
		"""
		 /* --------------------------------------- QScrollBar  -----------------------------------*/
		 QScrollBar
		 {
		     height: 15px;
		     margin: 3px 15px 3px 15px;
		     border: 1px transparent #2A2929;
		     border-radius: 4px;
		     background-color: #C4C4C4;    /* #2A2929; */
		 }

		 QScrollBar::handle
		 {
		     background-color: #807E7E;      /* #605F5F; */
		     min-width: 5px;
		     border-radius: 4px;
		 }

		QScrollBar::handle:hover
		{
			background-color: #605F5F;
		}

		QScrollBar::add-line
		{
			margin: 0px 3px 0px 3px;
			border-image: url(:/qss_icons/rc/right_arrow_disabled.png);
			width: 10px;
			height: 10px;
			subcontrol-position: right;
			subcontrol-origin: margin;
		}

		QScrollBar::sub-line
		{
			margin: 0px 3px 0px 3px;
			border-image: url(:/qss_icons/rc/left_arrow_disabled.png);
			height: 10px;
			width: 10px;
			subcontrol-position: left;
			subcontrol-origin: margin;
		}

		QScrollBar::add-line:hover,QScrollBar::add-line:on
		{
			border-image: url(:/qss_icons/rc/right_arrow.png);
			height: 10px;
			width: 10px;
			subcontrol-position: right;
			subcontrol-origin: margin;
		}


		QScrollBar::sub-line:hover, QScrollBar::sub-line:on
		{
			border-image: url(:/qss_icons/rc/left_arrow.png);
			height: 10px;
			width: 10px;
			subcontrol-position: left;
			subcontrol-origin: margin;
		}

		QScrollBar::up-arrow, QScrollBar::down-arrow
		{
			background: none;
		}


		QScrollBar::add-page, QScrollBar::sub-page
		{
			background: none;
		}
		"""

	def eventFilter(self, obj, event):
		try: # Without try and except raises three errors when begin run code
			if self.main_widget is obj and event.type() == QEvent.Wheel:
			
				if self.auto_scroll == AutoScrollTypes.AUTOMATIC:
					if self.verticalScrollBar().isVisible():
						scrollbar = self.verticalScrollBar()

					elif self.horizontalScrollBar().isVisible():
						scrollbar = self.horizontalScrollBar()

				elif self.auto_scroll == AutoScrollTypes.HORIZONTAL:
					scrollbar = self.horizontalScrollBar()

				elif self.auto_scroll == AutoScrollTypes.VERTICAL:
					scrollbar = self.verticalScrollBar()

				QCoreApplication.sendEvent(scrollbar, event)
			
			return super().eventFilter(obj, event)
		except:
			return True

