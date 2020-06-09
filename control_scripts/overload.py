CLASSES = {}


class Overload:

	def __init__(self, *types):
		self.types = types

	def __call__(self, f):
		# get name of method an corresponding class
		name = f.__qualname__.split(".")
		class_name, method_name = name[-2], name[-1]

		if class_name not in CLASSES:
			CLASSES[class_name] = {}
		func_dict = CLASSES[class_name]
		
		# get type tuple
		types = tuple(self.types[:])

		# add types to dictionary d[types] -> function
		func_dict[types] = f

		# create wrapper to return
		def wrapper(*args):
			# dump first since it is self (methods only)
			args_ = args[1:]
			types = (None, ) if not args else tuple([type(e) for e in args_])
			try:
				return func_dict[types](*args)
			except KeyError:
				raise TypeError("Overloaded method for args:\n'" + "".join(*map(str, types)) + "'\ndoes not exist")

		return wrapper


if __name__ == "__main__":
	class Dummy:

		a = "hallo"

		@Overload(int)
		def dummy(self, x):
			print(x, "is an int")

		@Overload(str)
		def dummy(self, x):
			print(x, "is a str")

	a = Dummy()
	a.dummy(2)
	a.dummy("2")
	a.dummy(3.0)



