def has_unit(variable):
    return hasattr(variable, 'unit')


def unit_control(f):
    def wrapper(first_data, sec_data):
        # first_data is Const or Data
        if not has_unit(sec_data):
            raise TypeError(f"Comparison between {type(first_data)} and {type(sec_data)} is not defined")
        if first_data.unit == sec_data.unit:
            return f(first_data, sec_data)
        else:
            raise ValueError(f"Comparison of vars with dimension {first_data.unit} and {sec_data.unit} is not defined")
    return wrapper

