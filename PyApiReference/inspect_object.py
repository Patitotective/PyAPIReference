from collections import OrderedDict
import inspect
import PREFS
import example

def prefs(func):
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

@prefs
def inspect_object(object_):
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
		Right now the example is not really true, it also includes an __init__ dunder method which it wouldn't, 
		we need to implement a way to only include __init__ dunder method when class (when class the type is <type>).
	"""
	object_name = object_.__name__
	result = {object_name: get_object_attributes(object_)}	
	object_members = get_object_members(object_)

	for member_name, member in object_members:
		result[object_name][member_name] = get_object_attributes(member)

	return result

def get_object_members(object_: object, dunder_methods_to_include: tuple=("__init__")):
	def filter_member(member_name):
		if member_name.startswith("__") and member_name.endswith("__") and member_name not in dunder_methods_to_include:
			return False

		return True

	result = inspect.getmembers(object_)
	# x[0] means member_name
	result = filter(lambda x: filter_member(x[0]), result)

	return result

def get_object_content(object_: object):
	"""
	"""
	result = {}
	
	for member_name, member in get_object_members(object_):
		result[member_name] = get_object_attributes(member)

	return result

def get_object_attributes(object_: object):
	result = {"type": type(object_)}

	if inspect.isfunction(object_) or inspect.ismethod(object_):
			result["parameters"] = get_callable_parameters(object_)	
			
			if "return" in object_.__annotations__:
				result["return_annotation"] = object_.__annotations__["return"]	
		
	elif inspect.isclass(object_):
		result["content"] = get_object_content(object_)

	return result

def get_callable_parameters(callable_: callable):
	result = {}

	for parameter in inspect.signature(callable_).parameters.values():
		result[parameter.name] = {
		"annotation": parameter.annotation if not parameter.annotation == inspect._empty else None, 
		"default": parameter.default if not parameter.default == inspect._empty else None, 
		"kind": parameter.kind
	}

	return result	

