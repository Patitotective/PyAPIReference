# Change Log

### v0.1.45 (11/10/2021)
- New markdown previewer with live update.
- When previewing markdown position windows side by side.
- Added option to disable positioning windows side by side when previewing markdown.
- Fixed some bugs.

### v0.1.40 (10/10/2021)
- Now when you disable a collapsible widget's checkbox, it's children's checkboxes don't get unchecked.
- Added `Check all` and `Uncheck all` action to collapsible's context menu.
- Added tooltips to tree members.

### v0.1.39 (10/10/2021)
- Now in settings, dark theme toggle is only applied when you click apply.
- Now it does restore the tree, previously it wasn't.

### v0.1.38 (10/10/2021)
- Now you can add items to the color pattern.
- Each color pattern item require a display name, a (python) type (`types` library available) and a color.
- (Python) type in color pattern and filter is interpreted with `interpret_type` function in `extra.py` module, which is way more safe than using `eval`. Also it doesn't let you to add an invalid type.

### v0.1.37 (08/10/2021)
- Changed filter dialog width (-50).
- Now you can open filter dialog size even if there is no module loaded, but you can't apply those changes, you need to load a module first to do it.
- Now the tab you're selecting is saved and restored.
- Wait 100 milliseconds before restoring module so the app loads properly before it gets stuck (this way you know the app is working) and before inspecting a module because the loading label wasn't displayed properly.
- When inspecting object, if variable is a string save it's value with quotes.

### v0.1.36 (07/10/2021)
- Removed tree scrollbar border.
- Fixed issues with preview markdown thread.

### v0.1.35 (06/10/2021)
- Fixed bug when adding more than one action to `ButtonWithExtraOptions`.
- Added `Inspect` tab in settings where you can change the recursion limit.
- Changed way it gets errors and display them.
- `inspect_object.py`:
	- Fixed some bugs when unknown docstring (`PyQt5`).
	- Added `exclude_types` and `include_imported_members` parameters to `inspect_object` function.
	- Added `recursion_limit` parameter too.
- Remade filter option.
- Added _Preview in Markdown_ option.
- Changed initial window size.
- Now markdown file is stored at `Prefs/temp.md`.
- When file size is large you can cancel the operation in a warning dialog.
- Fixed stretch when retry button.
- Replaced settings screenshot with markdown one.

### v0.1.31 (03/10/2021)
- User can filter objects to remove/show on tree.
- Need to add more options

### v0.1.30 (30/09/2021)
- Now it restores the last tree (checked and collapsed widgets) if you uncomment line `360` and comment the line before. Why? because it takes some time and seems like it weren't working.
- Created a button with extra options.

### v0.1.29 (27/09/2021)
- Added `docs` folder with **PyAPIReference**'s website.
- Now on `inspect_object.py` it doesn't get the members with `inspect.getmembers(object_)`, instead it `tuple(vars(object_).items())` which will keep the members in the order you defined them.
- When converting function to markdown it now includes it's parameters.

### v0.1.28 (25/09/2021)
- Added export as markdown options.
- Added discord link on `README.md`.

### v0.1.27 (25/09/2021)
- Added **Markdown** tab where you can create a markdown file based on the tree (and the checkboxes), update it and edit the markdown.
- When loading file default dir will be the last file dir, if no last file current dir.

### v0.1.26 (22/09/2021)
- If found exception when loading module cancel creation of tree and display the exception onto a label.

### v0.1.25 (20/09/2021)
- Changed code block colors.
- Now `inspect_object` do not inspect imported members (if module).
- `InspectObject` worker now do not have `module_content` as class attribute, just as instance.
- Changed default theme to `dark`.
- Added `inspect_object_worker_finished` and moved all `finished.connect` to it.

### v0.1.24 (20/09/2021)
- Now using [**PyQtDarkTheme**](https://github.com/5yutan5/PyQtDarkTheme) for both, light and dark theme.
- Now `Fold all` action doesn't fold the collapsible widget itself.
- Moved fonts and images to resources.
- Fixed `create_property_collapsible` bug.

### v0.1.23 (20/09/2021)
- `CollapsibleWidget` now has only 10 of margin at the left to representate indentation.
- Added context menu to collapsible widget with `Fold, Unfold, Fold all and Unfold all` actions.
- Now the tree will show class attributes.
- Changed scrollarea step from 2 to 5.
- Removed color pattern from `docstring` and added to `int, str, tuple, list and dict`.

### v0.1.22 (19/09/2021)
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

### v0.1.18 (17/09/2021)A
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