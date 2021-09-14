# Change Log

## v0.1.04(14/09/2021)
- Fixed bug when window get bigger and removed border on scrollarea.

### v0.1.03 (14/09/2021)
- Added style to the menubar which won't change with the theme.

### v0.1.02 (12/09/2021)
- Addded scrollarea on module collapsible area.
- Added dark theme.
- Changed files and folders from `PyApiReference` to `PyAPIReference`.

#### v0.1.01 (12/09/2021)
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