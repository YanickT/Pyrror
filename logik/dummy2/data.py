from logik.controlls import type_check, instancemethod
from logik.unit_helper import unit_control
from logik.data_helper import round_data, digits
from logik.unit import Unit
from typing import Union


class Data:

    """
    Main-Class of the project.
    Represents a value with uncertainty
    """

    def __init__(self, value: str, error: str, sign: Union[str, Unit] = "", power: int = 0, n: int = 0):
        """
        Initiate new value with uncertainty
        :param value: str = value
        :param error: str = uncertainty
        :param sign: Union[str, Unit] = unit of the value
        if sign is a string:
         there are different rules for more complex dimensions. They are also described in the Unit class only "/" not:
            #. powered dimensions have the form of  sign = dimension_syombol '^' power. *Attention: power >= 0*!
               Example: Area = m^2
            #. mixed dimensions are separated by ';'.
               Example: torque: = N;m
            #. fractions are created by a '/'. *There can only apper one '/' in each sign*. If a dimension appears left
               to an '/' it is count to the numerator. If it appears to the right its part of the denominator.
               Example: speed: m/s or acceleration: m/s^2

            **sign-EBNF:**
            string = (* normal string *)
            number = (* str of normal float *)
            dimension = string | string, '^', number | string, ';', string
            sign = dimension | dimension, '/', dimension;

        :param power: int = power of the value (for dimensions like mV => power = -3 and unit = 'V')
        :param n: int = significant digits of the error (if 0  (Default): get digits from error: str)
        """

        type_check((value, str), (error, str))

        if n == 0:
            self.n = digits(error)
        else:
            self.n = n

        if isinstance(sign, str):
            sign = sign.split("/")
            if len(sign) > 1:
                self.unit = Unit(sign[0], sign[1])
            else:
                self.unit = Unit(sign[0])
        else:
            self.unit = sign
        self.power = power

        self.error = float(error) * 10 ** self.power
        self.value = float(value) * 10 ** self.power

        round_data(self)

    def __str__(self):
        if self.n > 1:
            element = "(%." + "%s" % (self.n - 1) + "f±%." + "%s" % (self.n - 1) + "f)"
            string = element % (self.value * 10 ** (-self.power), self.error * (10 ** -self.power))
        elif self.n == 1:
            string = "(%i±%i)" % (self.value * 10 ** (-self.power), self.error * (10 ** -self.power))
        else:
            raise ValueError("n could not be smaller than 1")
        if self.power != 0:
            string += "*10^%s" % self.power

        unit_string = str(self.unit)
        if unit_string != "":
            string += " " + unit_string

        return string

    # Rechenoperationen mit Fehler nach vereinfachem Gauß

    """Multiplikation"""

    def __int_mul(self, other):
        return Data(str(self.value * other), str(self.error * other), sign=self.unit, n=self.n)

    def __float_mul(self, other):
        return Data(str(self.value * other), str(self.error * other), sign=self.unit, n=self.n)

    def __const_mul(self, other):
        return Data(str(self.value * other.value), str(self.error * other.value), sign=self.unit * other.unit, n=self.n)

    def __data_mul(self, other):
        result = self.value * other.value
        error = str(result * ((self.error / self.value) ** 2 + (other.error / other.value) ** 2) ** 0.5)
        significant_digits = min(self.n, other.n)
        unit = self.unit * other.unit
        result = str(result)
        return Data(result, error, sign=unit, n=significant_digits)

    @instancemethod
    def __mul__(self, other):  # multiplikation
        type_other = type(other)
        functions = {int: self.__int_mul, float: self.__float_mul, Const: self.__const_mul, Data: self.__data_mul}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '*' for Data and %s" % type_other)

    @instancemethod
    def __rmul__(self, other):
        type_other = type(other)
        functions = {int: self.__int_mul, float: self.__float_mul, Const: self.__const_mul, Data: self.__data_mul}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '*' for Data and %s" % type_other)

    """Multiplikation"""
    """Addition"""

    @unit_control
    def __data_add(self, other):
        result = self.value + other.value
        significant_digits = min(self.n, other.n)
        error = str((self.error ** 2 + other.error ** 2) ** 0.5)
        unit = self.unit
        result = str(result)
        return Data(result, error, n=significant_digits, sign=unit)

    @instancemethod
    def __add__(self, other):  # Addition
        type_other = type(other)
        functions = {Data: self.__data_add}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '+' for Data and %s" % type_other)

    """Addition"""
    """Subtraktion"""

    @unit_control
    def __data_sub(self, other):
        result = self.value - other.value
        significant_digits = min(self.n, other.n)
        error = str((self.error ** 2 + other.error ** 2) ** 0.5)
        unit = self.unit
        result = str(result)
        return Data(result, error, sign=unit, n=significant_digits)

    @instancemethod
    def __sub__(self, other):
        type_other = type(other)
        functions = {Data: self.__data_sub}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '-' for Data and %s" % type_other)

    """Subtraktion"""
    """Division"""

    def __int_div(self, other):
        return Data(str(self.value / other), str(self.error / other), sign=self.unit, n=self.n)

    def __float_div(self, other):
        return Data(str(self.value / other), str(self.error / other), sign=self.unit, n=self.n)

    def __const_div(self, other):
        result = str(self.value / other.value)
        unit = self.unit / other.unit
        error = str(self.error / other.value)
        significant_digits = self.n
        return Data(result, error, sign=unit, n=significant_digits)

    def __data_div(self, other):
        result = self.value / other.value
        significant_digits = min(self.n, other.n)
        error = str(result * ((self.error / self.value) ** 2 + (other.error / other.value) ** 2) ** 0.5)
        result = str(result)
        unit = self.unit / other.unit
        return Data(result, error, sign=unit, n=significant_digits)

    @instancemethod
    def __truediv__(self, other):  # Division
        type_other = type(other)
        functions = {int: self.__int_div, float: self.__float_div, Const: self.__const_div, Data: self.__data_div}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '/' for Data and %s" % type_other)

    @instancemethod
    def __rtruediv__(self, other):
        typ_other = type(other)
        if typ_other == int or typ_other == float:
            result = other / self.value
            unit = self.unit.flip()
            return Data(str(result), str(result * (self.error / self.value)), sign=unit, n=self.n)
        else:
            raise ValueError("Unsupported operation '/' for Data and %s" % typ_other)

    """"Division"""
    """Potenz"""

    def __pow__(self, other):  # Potenz
        typ_other = type(other)
        if typ_other == int or typ_other == float:
            result = self.value ** other
            unit = self.unit ** other
            return Data(str(result), str(result * (self.error / self.value)), sign=unit, n=self.n)
        elif typ_other == Data:
            raise ArithmeticError("Try to use a Formula instead!")
        else:
            raise ValueError("Unsupported operation '**' for Data and %s" % typ_other)

    """Potenz"""
    """Vergleiche"""

    @unit_control
    def __data_lt(self, other):
        return self.value + self.error + other.error < other.value

    @unit_control
    def __const_lt(self, other):
        return self.value + self.error < other.value

    @instancemethod
    def __lt__(self, other):  # <
        type_other = type(other)
        functions = {Const: self.__const_lt, Data: self.__data_lt}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '<' for Data and %s" % type_other)

    """--------"""

    @unit_control
    def __data_eq(self, other):
        return self.value - self.error - other.error <= other.value <= self.value + self.error + other.error

    @unit_control
    def __const_eq(self, other):
        return self.value - self.error <= other.value <= self.value + self.error

    @instancemethod
    def __eq__(self, other):  # ==
        type_other = type(other)
        functions = {Const: self.__const_eq, Data: self.__data_eq}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '==' for Data and %s" % type_other)

    """--------"""

    @unit_control
    def __data_gt(self, other):
        return self.value - self.error - other.error > other.value

    @unit_control
    def __const_gt(self, other):
        return self.value - self.error > other.value

    @instancemethod
    def __gt__(self, other):  # >
        type_other = type(other)
        functions = {Const: self.__const_gt, Data: self.__data_gt}
        try:
            return functions[type_other](other)
        except KeyError:
            raise ValueError("Unsupported operation '==' for Data and %s" % type_other)

    """--------"""

    @instancemethod
    def __ne__(self, other):  # !=
        return not self.__eq__(other)

    """--------"""

    @instancemethod
    def __ge__(self, other):  # >=
        return self.__gt__(other) or self.__eq__(other)

    """--------"""

    @instancemethod
    def __le__(self, other):  # <=
        return self.__lt__(other) or self.__eq__(other)

    """Vergleiche"""


# -------------------------------------------------------------------------------------------- #


class Const:
    """
    Für die Konstanten z.B. die Lichtgeschwindigkeit oder für ausreichend genaue Datas -> kein Fehler
    """

    def __init__(self, value, sign):  # sign = "m;N/s"; "/s;n"; "N;m"

        if type(sign) == str:
            sign = sign.split("/")
            if len(sign) > 1:
                self.unit = Unit(sign[0], sign[1])
            else:
                self.unit = Unit(sign[0])
        else:
            self.unit = sign

        self.value = float(value)

    @instancemethod
    def __str__(self):
        string = "%s" % self.value
        unit_string = str(self.unit)
        if unit_string != "":
            string += " " + unit_string
        return string

    @instancemethod
    def __mul__(self, other):  # multiplikation
        type_other = type(other)
        if type_other == int or type_other == float:
            value = self.value * other
            unit = self.unit
            return Const(value, sign=unit)
        elif type_other == Const:
            value = self.value * other.value
            unit = self.unit * other.unit
            return Const(value, sign=unit)
        elif type_other == Data:
            value = self.value * other.value
            unit = self.unit * other.unit
            n = other.n
            error = self.value * other.error
            return Data(str(value), str(error), n=n, sign=unit)

    @instancemethod
    def __rmul__(self, other):
        return self.__mul__(other)

    @instancemethod
    def __add__(self, other):  # Addition
        if type(other) == Const:
            if self.unit == other.unit:
                return Const(self.value + other.value, sign=self.unit)
        else:
            raise TypeError("unsupported operand '+' for Const and %s" % type(other))

    @instancemethod
    def __sub__(self, other):
        self.add(self, -1 * other)

    @instancemethod
    def __truediv__(self, other):  # Division
        type_other = type(other)
        if type_other == int or type_other == float:
            value = self.value / other
            unit = self.unit
            return Const(value, sign=unit)
        elif type_other == Const:
            value = self.value / other.value
            unit = self.unit / other.unit
            return Const(value, sign=unit)
        elif type_other == Data:
            value = self.value / other.value
            unit = self.unit / other.unit
            n = other.n
            error = self.value / other.error
            return Data(str(value), str(error), n=n, sign=unit)

    @instancemethod
    def __rtruediv__(self, other):
        typ_other = type(other)
        if typ_other == int or typ_other == float:
            result = other / self.value
            unit = self.unit.flip()
            return Const(result, unit)
        else:
            raise ValueError("Unsupported operation '/' for Const and %s" % typ_other)

    @instancemethod
    def __pow__(self, other):  # Potenz
        typ_other = type(other)
        if typ_other == int or typ_other == float:
            result = self.value ** other
            unit = self.unit ** other
            return Const(result, unit)
        elif typ_other == Data:
            raise ArithmeticError("Try to use a Formula instead!")
        else:
            raise ValueError("Unsupported operation '/' for Const and %s" % typ_other)

    @unit_control
    def __lt__(self, other):  # <
        return self.value < other.value

    @unit_control
    def __le__(self, other):  # <=
        return self.value <= other.value

    @unit_control
    def __eq__(self, other):  # ==
        return self.value == other.value

    @unit_control
    def __ne__(self, other):  # !=
        return self.value != other.value

    @unit_control
    def __ge__(self, other):  # >=
        return self.value >= other.value

    @unit_control
    def __gt__(self, other):  # >
        return self.value > other.value
