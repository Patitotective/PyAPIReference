import inspect
import PREFS
import types
import sys

def prefs(func: callable):
    """This decorator will pass the result of the given func to PREFS.convert_to_prefs, 
    to print a dictionary using PREFS format.
    Example:
    	# Without prefs decorator
    	def dictionary():
    		return {'keybindings': {'Ctrl+C': 'Copy', 'Ctrl+V': 'Paste'}} 
    	
    	print(dictionary())
		>>> {'keybindings': {'Ctrl+C': 'Copy', 'Ctrl+V': 'Paste'}}
    	# With prefs decorator
    	@prefs # This is called a decorator
    	def dictionary():
    		return {'keybindings': {"Ctrl+C": "Copy", "Ctrl+V": "Paste"}} 
    	
    	print(dictionary())
    	>>> keybindings=>
    			Ctrl+C='Copy'
    			Ctrl+C='Paste'
    Notes:
    	Only works with dictionaries.
    """
    def wrapper_function(*args, **kwargs):
        result = PREFS.convert_to_prefs(func(*args,  **kwargs)) # Call given func and pass it's result to PREFS.convert_to_prefs

        return result

    return wrapper_function # Return function to call

def inspect_object(object_: object, exclude_types: tuple=(types.ModuleType), include_imported_members: bool=False, recursion_limit: int=10 ** 6):
	"""Find all members of Python object.
	Example:
		def say_hi(name: str) -> str:
			print(f"hi {name}")
		print(inspect_object(say_hi))
		>>> say_hi=>
			type=<class 'function'>
			parameters=>
				name=>
				annotation=<class 'str'>
				default=None
				kind=POSITIONAL_OR_KEYWORD
			return_annotation=<class 'str'>
	"""
	previous_recursion_limit = sys.getrecursionlimit()
	sys.setrecursionlimit(recursion_limit)

	object_name = object_.__name__
	result = {object_name: get_object_properties(object_, exclude_types=exclude_types, include_imported_members=include_imported_members)}	
	
	sys.setrecursionlimit(previous_recursion_limit)

	return result

def get_object_members(object_: object, exclude_types: tuple=(types.ModuleType), include_imported_members: bool=False):
	def filter_member(member_name: str, member: object):
		if isinstance(member, exclude_types):
			return False
 
 		# If the object it's a module
		if inspect.ismodule(object_) and not include_imported_members:
			# Get the module of the member (where it was defined or it belongs to)
			# And check if the object name is the same as the member one.
			# This will exclude all members that do not belong to the given module.
			member_module = inspect.getmodule(member)
			if member_module is not None:
				return member_module.__name__ == object_.__name__

		dunder_methods = PREFS.read_prefs_file("dunder_methods.prefs")
		if type(object_).__name__ in dunder_methods:
			dunder_methods_to_include = dunder_methods[type(object_).__name__]
		else:
			dunder_methods_to_include = ()

		if (member_name.startswith("__") and member_name.endswith("__") 
			and member_name not in dunder_methods_to_include):
			
			return False

		return True

	# Instead of using inspect.getmembers to keep the members in the order they were defined
	# We are going to use vars(object_)
	# result = inspect.getmembers(object_)
	result = tuple(vars(object_).items())

	# filter_member(*x) is equivalent to filter_member(x[0], x[1])
	result = filter(lambda x: filter_member(*x), result)

	return result

def get_object_content(object_: object, exclude_types: tuple=(types.ModuleType), include_imported_members: bool=False):
	"""Given an object get attributes of all of it's members.
	"""
	result = {}

	for member_name, member in get_object_members(object_, exclude_types=exclude_types, include_imported_members=include_imported_members):
		result[member_name] = get_object_properties(member, exclude_types=exclude_types, include_imported_members=include_imported_members)

	return result

def get_object_properties(object_: object, exclude_types: tuple=(types.ModuleType), include_imported_members: bool=False):
	"""Given an object return it's type and content.
	Example:
		class Test2(Test1):
			def __init__(self):
				pass

			def test_fun(self):
				pass
		
		>>>
		type=class
		inherits=>
			Test1
		content=>
			__init__=>
				type=function 
				parameters ...
			test_func=>
				type=function
				parameters ...

	callable (function, lambda, methods) -> parameters (see get_callable_parameters), return_annotation 
	"""

	object_type = type(object_).__name__

	if object_type == "type":
		object_type = "class"

	result = {"type": object_type, "docstring": str(object_.__doc__) if object_.__doc__ is not None else object_.__doc__}
		
	if inspect.isclass(object_) or inspect.ismodule(object_):
		
		if inspect.isclass(object_):
			result["inherits"] = [i.__name__ for i in inspect.getmro(object_)[1:-1]]
		
		result["content"] = get_object_content(object_, exclude_types=exclude_types, include_imported_members=include_imported_members)
	
	elif inspect.isfunction(object_) or inspect.ismethod(object_):
		
		result["parameters"] = get_callable_parameters(object_)	
			
		if "return" in object_.__annotations__:
			result["return_annotation"] = []
	
			if isinstance(object_.__annotations__["return"], (tuple, list)):
				for annotation in object_.__annotations__["return"]:
					result["return_annotation"].append(str(annotation.__name__) if not annotation == inspect._empty else None)
			else:
				result["return_annotation"] = str(object_.__annotations__["return"].__name__) if object_.__annotations__["return"] is not None else None 

	else:
		result["value"] = str(object_)
	
	return result

def get_callable_parameters(callable_: callable):
	"""Given a callable object (functions, lambda or methods) get all it's parameters, 
	each parameter annotation (a: str, b: int), default value (a=1, b=2) and kind (positional, keyword, etc).
	If no annotation or default value None.
	Example:
		def say_hi(name: str, last_name: str, age: int=20):
			print(f"hi {name} {last_name}, you are {age} years old.")
		print(get_callable_parameters(say_hi))
		
		>>> 
		name=>
			annotation=<class 'str'>
			default=None
			kind=POSITIONAL_OR_KEYWORD
		last_name=>
			annotation=<class 'str'>
			default=None
			kind=POSITIONAL_OR_KEYWORD
		age=>
			annotation=<class 'int'>
			default=20
			kind=POSITIONAL_OR_KEYWORD
	"""
	result = {}

	for parameter in inspect.signature(callable_).parameters.values():
		
		if parameter.default == inspect._empty:
			default_parameter = None
		else:
			try:
				default_parameter = parameter.default.__name__
			except AttributeError:
				default_parameter = str(parameter.default)

		
		result[parameter.name] = {
			"annotation": [], 
			"default": default_parameter, 
			"kind": parameter.kind.description
		}

		if isinstance(parameter.annotation, (tuple, list)):
			for annotation in parameter.annotation:
				result[parameter.name]["annotation"].append(str(annotation.__name__) if not annotation == inspect._empty else None)
			continue

		result[parameter.name]["annotation"] = str(parameter.annotation.__name__) if not parameter.annotation == inspect._empty else None

	return result
