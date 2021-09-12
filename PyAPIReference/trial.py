import PREFS
from inspect_object import inspect_object

def say_hi(name, last_name, age, greeting="hi"):
  print(f"{greeting}, {name} {last_name} you are {age} years old")

#print(PREFS.convert_to_prefs(inspect_object(say_hi)))
