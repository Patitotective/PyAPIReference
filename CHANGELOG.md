# Change Log

### v0.1.22
- Color pattern
	- Now the `default` value will be a color instead of `"default"`.
	- Created `find_object_type_color`, which will, given a string representing the type of the object, look up trough `colors` onto the prefs file for a color for the object type, if no color for the type, default font color.
- Settings dialog
	- Converted the settings dialog into a class.
	- Settings now in tabs (`QTabWidget`).
- When inspecting object if found `type` type return `class` instead.
- `theme` to `THEME` (because it's a constant)
- Added `logo_without_background.png` image to display on the top of the application.

### v0.1.21 (19/09/2021)
- User can pick color pattern for (``classes, functions, parameters``) in Settings tab
- Prefs/settings.prefs
  - Added default color pattern (white for dark mode, black for light mode) 
- Adding more colors soon

### v0.1.20 (17/09/2021)
- When docstring (or other string) has more than one line, create a collapsible for it.
- Set `UbuntuMono` as font for the whole app (needed to fix, because menu bar is included).
- Added `UbuntuMono` font to assets.

### v0.1.19 (17/09/2021)
- `GUI/theme.prefs`
	- Added disabled color to buttons.
	- Added custom font.
- Added loading label when inspecting module.
- Moved all export actions to `Export tree...` menu inside `File` menu.
- Removed all export actions shortcuts.
- Added **PyAPIReference** logo at the top of the window
- Renamed some thread stuff.

### v0.1.18 (17/09/2021)
- Changed `inspect_object` to run on seperate thread. Prevents GUI freezing.    
Visual suggestion: Need to gray out button when disabled

### v0.1.17 (17/09/2021)
- Added breakline after logo on `README.md`.

### v0.1.16 (17/09/2021)
- Resized `logo.png` (now `500x263`).

### v0.1.15 (17/09/2021)
- Added `logo.png`, `icon.png` and `icon.ico`.
- Added icon to window.

### v0.1.14 (17/09/2021)
- Fixed export option.

### v0.1.13 (16/09/2021)
- Added `restore_geometry` and `save_geometry` methods on `MainWindow` class.

### v0.1.12 (16/09/2021)
- Fixed **PREFS** export function.
- Updated all to new **PREFS** version.

### v0.1.11 (16/09/2021)
- Moved GUI stuff to `GUI` folder.

### v0.1.10 (16/09/2021)
- Now annotation support collapsible widget.
- Settings no more resizable.
- `inspect_object.py`
	- Changed way object type was obtained.
	- Get docstring from every object.
	- Now supports multiple function return annotation or parameter annotations.
	- Other `str` and `__name__` stuff.

### v0.1.09 (16/09/2021)
- Changed way `collapsible_widget` theme works.
- Restore opened file when closing application (also when applying on settings dialog).
- If no inherits or no parameters ignore collapsible (instead of displaying and empty one).
- Created `FormLayout` on `settings_dialog.py` that centers the widgets (not like `QFormLayout`).
	- Added `multipledispatch` on `requirements.txt`

### v0.1.08 (16/09/2021)
- Added export as PREFS and YAML options

### v0.1.07 (15/09/2021)
- Added docstrings of objects to tree 
- Fixed bug if default parameter was class or function (`get_callable_parameters` in `inspect_object.py`)

### v0.1.06 (15/09/2021)
- Changed widgets margin on `collapsible_widget.py`.
- Added `get_module_from_path` on `extra.py` (used on `main.py`).
- Fixed bug when no annotation on parameters (`get_object_properties` on `inspect_object.py`).
- Made `export_as_json` more pythonic.
- Added default filename when `Export as JSON` which is the module name plus `.json`.
- Added recursion when `create_object_properties_widgets`.
- `inherits` property now it's an collapsible object.
- Added row span to `module_content_widget` so it fills the screen.

### v0.1.05 (14/09/2021)
- Added option to export object tree as a JSON file   
- Bugs
  - Object tree doesnt display some attributes. Example: Not displaying *a = 1* from class Test3 (from example.py)
### v0.1.04 (14/09/2021)
- Fixed bug when window get bigger and removed border on scrollarea.

#### v0.1.03 (14/09/2021)
- Added style to the menubar which won't change with the theme.

#### v0.1.02 (12/09/2021)
- Addded scrollarea on module collapsible area.
- Added dark theme.
- Changed files and folders from `PyApiReference` to `PyAPIReference`.

###### v0.1.01 (12/09/2021)
- Optimized `inspect_object` by excluding modules from inspecting.
	- How:  
		On `get_object_members` added `exclude_types` parameter which it's default value is `tuple: (ModuleType)` (`types.ModuleType`), means exclude modules while getting object members.

	- Example:
		```py
		import PREFS

		def say_hi(name: str):
			print(f"Hi {name}")
		```
		Will only inspect `say_hi` and not `PREFS`.

	- Notes:
		You need to know that when importing classes or functions from libraries it does inspect them.
		```py
		from PREFS import read_prefs_file

		def say_hi(name: str):
			print(f"Hi {name}")
		```
		Will inspect `say_hi` **and** `read_prefs_file`.