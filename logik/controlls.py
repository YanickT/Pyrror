import copy


def type_check(*args):
    for arg in args:
        #Bsp.: arg = (3, int)
        if type(arg[0]) != arg[1]:
            raise TypeError("Type of '%s' is false! Try %s instead" % (arg[0], arg[1]))
    return True


def list_type_check(liste, data_type):
    for element in liste:
        if type(element) != data_type:
            return False
    return True


# Decorator
def instancemethod(f):
    def wrapper(self, *args):
        atts = copy.deepcopy(self.__dict__)
        result = f(self, *args)
        if atts != self.__dict__:
            raise AttributeError("Instance has been chanced in during method")
        return result
    return wrapper
