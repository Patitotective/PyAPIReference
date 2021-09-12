# Change Log

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