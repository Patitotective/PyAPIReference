import inspect

def inspect_object(object_, include_dunder_methods=False, dunder_methods_to_include=("__init__")):
	"""Find all members of Python object, if class call itself.

	Errors:
		Right now when inspecting module, class in that module will be create a nested dictionary, ignoring class type.
		Not working with nested functions. (Need to implement a way to show member type on nested dictionaries)
	"""
	result = []
	module_members = inspect.getmembers(object_)

	for member_name, member in module_members:
		# If the member name starts with __ (means dunder method) and the member name is not onto the 
		# dunder_methods_to_include check if include_dunder_methods is True, if it is 
		# Add /ignore (backslash ignore) at the end of the member name 
		# (this way we can identify dunder methods to ignore when showing onto the screen) 
		member_base_name = member_name		
		
		if member_name.startswith("__") and member_name not in dunder_methods_to_include:
			if not include_dunder_methods:
				continue

			member_name += r"\ignore"

		# If the member it's a class call itself to get all members in the class
		# (Need to add same with functions, because of nested functions)
		if inspect.isclass(member) or inspect.isfunction(member) or inspect.ismethod(member):
			if member_base_name == "__class__" or member_base_name == "__base__":
				# If not ignore __class__ and __base__ dunder methods will end on
				# RecursionError: maximum recursion depth exceeded while calling a Python object
				continue
			
			result.append((member_name, member, (inspect_object(member))))
			continue

		# If the member is not a class
		# Add it to result with name as key and member as value
		result.append((member_name, member))

	return result

