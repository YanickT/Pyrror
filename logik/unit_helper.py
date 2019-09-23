def has_unit(variable):
    try:
        variable.unit
        return True
    except AttributeError:
        return False


def unit_control(f):
    def wrapper(first_data, sec_data):
        # first_data is Const or Data
        if not has_unit(sec_data):
            raise TypeError("Comparison between %s and %s is not defined" % (type(first_data), type(sec_data)))
        if first_data.unit == sec_data.unit:
            return f(first_data, sec_data)
        else:
            raise ValueError(
                "Comparison of vars with dimension %s and %s is not defined" % (first_data.unit, sec_data.unit))
    return wrapper

