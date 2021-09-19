import copy


def type_check(*args):
    """
    Checks if all types in args are correct
    :param args: List[Tuple[object, type]] = list of objects and their estimated types
    :return: bool = True or raises an error
    """
    for arg in args:
        if type(arg[0]) != arg[1]:
            raise TypeError(f"Type of '{type(arg[0])}' is false! Try {arg[1]} instead")
    return True


def list_type_check(lst, data_type):
    """
    Checks if each element of lst has a given type.
    :param lst: List = list of objects
    :param data_type: type = estimated type for the objects
    :return: bool = true if all objects in list have the type data_type
    """
    return all([type(e) == data_type for e in lst])


def instancemethod(f):
    """
    Checks if an instance of a class changes while executing f. If so raise an error.
    USE AS DECORATOR
    :param f: function = method to overload
    :return: obj = return of the function
    """

    def wrapper(self, *args, **kwargs):
        atts = copy.deepcopy(self.__dict__)
        result = f(self, *args, **kwargs)
        if atts != self.__dict__:
            raise AttributeError("Instance was chanced during the method")
        return result
    return wrapper
