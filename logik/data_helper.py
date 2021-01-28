import math


def digits(error):
    """
    Calculates the number of significant digits
    :param error: Union[float, int, str] = uncertainty of a Data
    :return: int = number of significant digits
    """

    error_str = str(error)
    lenght = len(error_str)

    for index in range(0, len(error_str)):
        if error_str[index] != "0" and error_str[index] != ".":
            break
        elif index == lenght - 1:
            raise ArithmeticError(f"Error '{error_str}' has no digits")

    if error_str[index:].count("."):
        return lenght - (index + 1)
    else:
        return lenght - index


def round_data(data):
    """
    Round a data object to the correct number of significant digits.
    :param data: Data = Data instance to round
    :return: void
    """

    value = data.value / (10 ** data.power)
    error = data.error / (10 ** data.power)

    # determine first (non-zero) digit of error
    error_power = math.floor(math.log10(error))

    # round data to correct length
    error = round(error * 10 ** (- error_power), data.n - 1)
    value = round(value * 10 ** (- error_power), data.n - 1)
    if value == -0:
        value = 0
    data.power += error_power

    # update the value and error in the Data
    data.error = error * 10 ** data.power
    data.value = value * 10 ** data.power
