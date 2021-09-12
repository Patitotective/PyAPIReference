#Inheritance Example
class Test3:
	pass


class Test2(Test3):
	def __init__(self):
		self.age = 100

	def say_age(self):
		print(f"hi {self.age}")


class Test(Test2):
	def __init__(self):
		self.name = "carlitos"
		super().__init__()

	def say_hi(self):
		print(f"hi {self.name}")


def say_hi(name: str) -> str:
    print(f"hi {name}")


