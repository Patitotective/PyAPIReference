import inspect
import PREFS
import example
from types import ModuleType

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

def inspect_object(object_: object):
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
	Errors:
		Tatkes too much time, need to add some optimization.
	"""
	object_name = object_.__name__
	result = {object_name: get_object_properties(object_)}	

	return result

def get_object_members(object_: object, exclude_types: tuple=(ModuleType)):
	def filter_member(member_name: str, member: object):
		if isinstance(member, exclude_types):
			return False


		dunder_methods = PREFS.read_prefs_file("dunder_methods")
		if type(object_).__name__ in dunder_methods:
			dunder_methods_to_include = dunder_methods[type(object_).__name__]
		else:
			dunder_methods_to_include = ()

		if member_name.startswith("__") and member_name.endswith("__") and member_name not in dunder_methods_to_include:
			return False

		return True

	result = inspect.getmembers(object_)
	# filter_member(*x) means filter_member(x[0], x[1])
	result = filter(lambda x: filter_member(*x), result)

	return result

def get_object_content(object_: object):
	"""Given an object get attributes of all of it's members.
	"""
	result = {}
	
	for member_name, member in get_object_members(object_):
		result[member_name] = get_object_properties(member)

	return result

def get_object_properties(object_: object):
	"""Given an object return it's attributes.
	class, module -> type, content
	callable (function, lambda, methods) -> parameters (see get_callable_parameters), return_annotation 
	"""
	result = {"type": type(object_)}
		
	if inspect.isclass(object_) or inspect.ismodule(object_):
		if inspect.isclass(object_):
			result["inherits"] = list(inspect.getmro(object_)[1:-1])
		
		result["content"] = get_object_content(object_)
	
	elif inspect.isfunction(object_) or inspect.ismethod(object_):
		result["parameters"] = get_callable_parameters(object_)	
			
		if "return" in object_.__annotations__:
			result["return_annotation"] = object_.__annotations__["return"]	
	
	else:
		result["value"] = object_
	
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
		result[parameter.name] = {
		"annotation": parameter.annotation if not parameter.annotation == inspect._empty else None, 
		"default": parameter.default if not parameter.default == inspect._empty else None, 
		"kind": parameter.kind
	}

	return result