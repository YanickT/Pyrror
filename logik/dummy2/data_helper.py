def digits(error):
    error_str = str(error)
    lenght = len(error_str)

    for index in range(0, len(error_str)):
        if error_str[index] != "0" and error_str[index] != ".":
            break
        elif index == lenght - 1:
            raise ArithmeticError("Error '%s' has no digits" % (error_str))

    if error_str[index:].count("."):
        return lenght - (index + 1)
    else:
        return lenght - index


def round_data(data):
    n = data.n

    value = data.value / (10 ** data.power)
    error = data.error / (10 ** data.power)

    e_int = int(error)
    if e_int == 0:
        e_length = 0
    else:
        e_length = len(str(e_int))

    while e_length != 1:

        if e_length == 0:
            data.power -= 1
            value *= 10
            error *= 10

        elif e_length > 1:
            data.power += 1
            value /= 10
            error /= 10

        e_int = int(error)
        if e_int == 0:
            e_length = 0
        else:
            e_length = len(str(e_int))

    if n - 1 > 0:
        if value >= 0:
            data.value = round(value, n - 1) * 10 ** data.power
        else:
            data.value = -1 * round(-1 * value, n - 1) * 10 ** data.power
        data.error = round(error, n - 1) * 10 ** data.power
    else:
        if value >= 0:
            data.value = int(value + 0.5) * 10 ** data.power
        else:
            data.value = int(value - 0.5) * 10 ** data.power
        data.error = int(error + 0.5) * 10 ** data.power
    return True
