"""PyApiReference is a GUI application to generate Python Api References.

About:
	Patitotective:
		Discord: patitotective#0127
		GitHub: https://github.com/Patitotective
	Sharkface:
		Discord: Sharkface#9495
		GitHub: https://github.com/devp4

"""

# Libraries
import inspect
import PREFS

# Dependencies
import example

members = inspect.getmembers(example)
for member in members:
	if not member[0].startswith("__"):
		print(member)
