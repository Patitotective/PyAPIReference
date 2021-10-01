"""Example file with classes, iheritance, functions, imported members and constants to test PyAPIReference.
This is the docstring for example.py.
"""
from time import sleep
from PyQt5 import *

BLACK = "#000000"
WHITE = "#ffffff"

class Person:
	"""Class person that requires name, last name and age.
	Allows you to display some info about it.
	"""
	human = True
	def __init__(self, name: str, last_name: str, age: str):
		self.name = name
		self.last_name = last_name
		self.age = age

	def display_info(self):
		print(f"Hello, my name is {self.name} {self.last_name} I have {self.age} years old.\n")

class Student(Person):
	"""Class Student that inherits from Person and requires grade and institution (besides the Person ones).
	Allows you to display some info about it.
	"""	
	studying = True
	
	def __init__(self, grade: int, institution: str, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.grade = grade
		self.institution = institution

	def display_info(self):
		print(f"Hello, my name is {self.name} {self.last_name} I have {self.age} years old.\nI'm a student of grade {self.grade} in {self.institution}\n")


class Teacher(Person):
	"""Class Teacher that inherits from Person and requires instituiton and classes (besides Person ones).
	Alloes you to display some info about it.
	"""
	def __init__(self, institution: str, classes: tuple, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.institution = institution
		self.classes = classes

	def display_info(self):
		print(f"Hello, my name is {self.name} {self.last_name} I have {self.age} years old.\nI'm a teacher of {''.join(self.classes)} in {self.institution}\n")


class SchoolTeacher(Teacher):
	"""Class SchoolTeacher that inherits from Teacher and requires grades.
	Allows you to display some info about it."""

	def __init__(self, grades: tuple, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.grades = grades

	def display_info(self):
		print(f"Hello, my name is {self.name} {self.last_name} I have {self.age} years old.\nI'm a teacher of {''.join(self.classes)} in {''.join(self.grades)} at {self.institution}\n")


class CollegeStudent(Student):
	"""Class CollegeStudent that inherits from Student and requires career and semester (besides the Student ones).
	Allows you to display some info about it.
	"""		
	def __init__(self, career: str, semester: int, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.career = career
		self.semester = semester

	def display_info(self):
		print(f"Hello, my name is {self.name} {self.last_name} I have {self.age} years old.\nI'm a college student of {self.career}, I'm on {self.semester} semester\n")



class Me(Teacher, CollegeStudent):
	"""I'm a teacher on a school but a student in a college."""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


def caesar_cipher(text: str, shift: int=5) -> str:
	"""Simple caesar cipher function that encrypts a string with using caesar cipher.
	"""
	result = ""
	for char in text:	      
		if (char.isupper()):
			result += chr((ord(char) + shift - 65) % 26 + 65)
			continue
		
		result += chr((ord(char) + shift - 97) % 26 + 97)
	
	return result

def foo(param1, param2=None, param3: str="Hello world"):
	"""foo function docstring"""
	pass

def emtpy():
	pass

if __name__ == "__main__":
	person = Person("William", "Polo", 15)
	student = Student(6, "Harward", "Jack", "Sparrow", 45)
	college_student = CollegeStudent("Computer science", 4, 0, "Harvard", "Will", "Miles", 23)

	person.display_info()
	student.display_info()
	college_student.display_info()

	print(caesar_cipher(person.name))
