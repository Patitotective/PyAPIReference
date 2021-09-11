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
from importlib.util import spec_from_file_location, module_from_spec

# Dependencies
#import example


#Get file path (From GUI in future)
file_path = input("File Path: ")
file_name = file_path.split("\\")[-1]

#Get spec from file path and load module from spec
spec = spec_from_file_location(file_name, rf"{file_path}")
module = module_from_spec(spec)
spec.loader.exec_module(module)

#Get non-built in objects 
members = inspect.getmembers(module)
for member in members:
	if not member[0].startswith("__"):
		print(member)
