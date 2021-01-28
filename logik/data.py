from logik.controls import type_check, instancemethod
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
            **sign-EBNF:**
            S := '"' units '"' | '"' units '/' units '"'
            units := unit | unit ';' units
            unit := string | string '^' integer
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
                sign = ["" if s == "1" else s for s in sign]
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
        """
        Return a string representation of the Data.
        :return: str = string representation of the Data
        """

        # insert values
        if self.n > 1:
            string = f"({self.value * 10 ** (-self.power):.{(self.n - 1)}f}±{self.error * (10 ** -self.power):.{(self.n - 1)}f})"
        elif self.n == 1:
            string = f"({self.value * 10 ** (-self.power):.0f}±{self.error * (10 ** -self.power):.0f})"
        else:
            raise ValueError("n could not be smaller than 1")

        # add power
        if self.power != 0:
            string += f"*10^{self.power}"

        # add unit
        unit = str(self.unit)
        if unit != "":
            string += f" {unit}"

        return string

    @instancemethod
    def __repr__(self):
        return self.__str__()
    # Calculations using simplified gauss

    def __number_mul(self, other):
        """
        Helper function of multiplication of Data with float.
        :param other: Union[int, float] = value to multiplicative Data with
        :return: Data = result of the multiplication
        """

        return Data(str(self.value * other), str(self.error * other), sign=self.unit, n=self.n)

    def __const_mul(self, other):
        """
        Helper function of multiplication of Data with Const.
        :param other: Const = Const to multiplicative Data with
        :return: Data = result of the multiplication
        """

        return Data(str(self.value * other.value), str(self.error * other.value), sign=self.unit * other.unit, n=self.n)

    def __data_mul(self, other):
        """
        Helper function of multiplication of two Data.
        :param other: Data = The other Data to multiplicative Data with
        :return: Data = result of the multiplication
        """

        result = self.value * other.value
        error = str(result * ((self.error / self.value) ** 2 + (other.error / other.value) ** 2) ** 0.5)
        significant_digits = min(self.n, other.n)
        unit = self.unit * other.unit
        result = str(result)
        return Data(result, error, sign=unit, n=significant_digits)

    @instancemethod
    def __mul__(self, other):
        """
        Multiplication of Data object with other. Which will happen depend on the type of other.
        :param other: Union[Data, Const, int, float] = Object to multiply with
        :return: Data = result of the multiplication
        """

        type_other = type(other)
        functions = {int: self.__number_mul, float: self.__number_mul, Const: self.__const_mul, Data: self.__data_mul}

        if type_other not in functions:
            raise ValueError(f"Unsupported operation '*' for Data and {type(other)}")

        return functions[type_other](other)

    @instancemethod
    def __rmul__(self, other):
        """
        Multiplication of Data object with other. Which will happen depend on the type of other.
        :param other: Union[Data, Const, int, float] = Object to multiply with
        :return: Data = result of the multiplication
        """
        return self.__mul__(other)

    @unit_control
    def __data_add(self, other):
        """
        Helper function for addition of two Data.
        :param other: Data = other Data to add with Data
        :return: Data = result of the addition
        """

        result = self.value + other.value
        significant_digits = min(self.n, other.n)
        error = str((self.error ** 2 + other.error ** 2) ** 0.5)
        unit = self.unit
        result = str(result)
        return Data(result, error, n=significant_digits, sign=unit)

    def __number_add(self, other):
        """
        Helper function for addition of a Data and an Union[int, float].
        :param other: Union[int, float] = value to add
        :return: Data = result of the addition
        """

        if self.unit == Unit(""):
            return Data(str(self.value + other), str(self.error), n=self.n, power=self.power)

    @unit_control
    def __const_add(self, other):
        """
        Helper function for addition of a Data and an Const.
        :param other: Const = value to add
        :return: Data = result of the addition
        """

        result = self.value + other.value
        significant_digits = min(self.n, other.n)
        unit = self.unit
        result = str(result)
        return Data(result, self.error, n=self.n, sign=unit)

    @instancemethod
    def __add__(self, other):
        """
        Addition of a Data and other.
        :param other: Union[Data, Const, int, float] = Object to add with
        :return: Data = result of the addition
        """

        type_other = type(other)
        functions = {int: self.__number_add, float: self.__number_add, Const: self.__const_add, Data: self.__data_add}

        if type_other not in functions:
            raise ValueError("Unsupported operation '+' for Data and {type(other)}")

        return functions[type_other](other)

    @instancemethod
    def __radd__(self, other):
        """
        Addition of a Data and other.
        :param other: Union[Data, Const, int, float] = Object to add with
        :return: Data = result of the addition
        """

        return self.__number_add(other)

    @unit_control
    def __data_sub(self, other):
        """
        Helper function for subtraction of two Data.
        :param other: Data = other Data to subtract with Data
        :return: Data = result of the subtraction
        """

        result = self.value - other.value
        significant_digits = min(self.n, other.n)
        error = str((self.error ** 2 + other.error ** 2) ** 0.5)
        unit = self.unit
        result = str(result)
        return Data(result, error, sign=unit, n=significant_digits)

    def __number_sub(self, other):
        """
        Helper function for subtraction of a Data and an Union[int, float].
        :param other: Union[int, float] = value to subtract
        :return: Data = result of the subtraction
        """

        if self.unit == Unit(""):
            return Data(str(self.value - other), str(self.error), n=self.n, power=self.power)

    @unit_control
    def __const_sub(self, other):
        """
        Helper function for subtraction of a Data and an Const.
        :param other: Const = value to subtract
        :return: Data = result of the subtraction
        """

        return Data(str(self.value - other.value), str(self.error), n=self.n, sign=self.unit)

    @instancemethod
    def __sub__(self, other):
        """
        Subtraction of two Data objects.
        :param other: Data = other Data to subtract with Data
        :return: Data = result of the subtraction
        """

        type_other = type(other)
        functions = {int: self.__number_sub, float: self.__number_sub, Const: self.__const_sub, Data: self.__data_sub}

        if type_other not in functions:
            raise ValueError("Unsupported operation '-' for Data and {type(other)}")

        return functions[type_other](other)

    @instancemethod
    def __rsub__(self, other):
        """
        Subtraction of a Data and other.
        :param other: Union[Data, Const, int, float] = Object to subtract with
        :return: Data = result of the substraction
        """

        return self.__number_sub(other)

    def __number_div(self, other):
        """
        Helper function of division of Data with float.
        :param other: Union[int, float] = value to divide Data with
        :return: Data = result of division
        """

        return Data(str(self.value / other), str(self.error / other), sign=self.unit, n=self.n)

    def __const_div(self, other):
        """
        Helper function of division of Data with Const.
        :param other: Const = Const to divide Data with
        :return: Data = result of division
        """

        result = str(self.value / other.value)
        unit = self.unit / other.unit
        error = str(self.error / other.value)
        significant_digits = self.n
        return Data(result, error, sign=unit, n=significant_digits)

    def __data_div(self, other):
        """
        Helper function of division of Data with Data.
        :param other: Data = Data to divide Data with
        :return: Data = result of division
        """

        result = self.value / other.value
        significant_digits = min(self.n, other.n)
        error = str(result * ((self.error / self.value) ** 2 + (other.error / other.value) ** 2) ** 0.5)
        result = str(result)
        unit = self.unit / other.unit
        return Data(result, error, sign=unit, n=significant_digits)

    @instancemethod
    def __truediv__(self, other):
        """
        Division of a Data object with other.
        :param other: Union[Data, Const, int, float] = object to divide with
        :return: Data = result of the division
        """

        type_other = type(other)
        functions = {int: self.__number_div, float: self.__number_div, Const: self.__const_div, Data: self.__data_div}
        if type_other not in functions:
            raise ValueError(f"Unsupported operation '/' for Data and {type_other}")

        return functions[type_other](other)

    @instancemethod
    def __rtruediv__(self, other):
        """
        Division of a Data object with other.
        :param other: Union[int, float] = object to divide with
        :return: Data = result of the division
        """
        typ_other = type(other)
        if typ_other == int or typ_other == float:
            result = other / self.value
            unit = self.unit.flip()
            return Data(str(result), str(result * (self.error / self.value)), sign=unit, n=self.n)
        else:
            raise ValueError(f"Unsupported operation '/' for Data and {typ_other}")

    def __pow__(self, other):
        """
        Power of a Data object with other.
        :param other: Union[int, float] = object to power with
        :return: Data = result of the calculation
        """

        typ_other = type(other)
        if typ_other == int or typ_other == float:
            result = self.value ** other
            unit = self.unit ** other
            return Data(str(result), str(result * (self.error / self.value)), sign=unit, n=self.n)
        elif typ_other == Data:
            raise ArithmeticError("Try to use a Formula instead!")
        else:
            raise TypeError(f"Unsupported operation '**' for Data and {typ_other}")

    # Data comparisons

    @unit_control
    def __data_lt(self, other):
        """
        Helper function of lt comparison of Data with Data.
        :param other: Data = Data to compare with
        :return: bool = result of comparison
        """

        return self.value + self.error + other.error < other.value

    @unit_control
    def __const_lt(self, other):
        """
        Helper function of lt comparison of Data with Const.
        :param other: Const = Const to compare with
        :return: bool = result of comparison
        """

        return self.value + self.error < other.value

    @instancemethod
    def __lt__(self, other):
        """
        Compare Data with other objects.
        :param other: Union[Data, Const] = object to compare with
        :return: bool = result of comparison
        """

        type_other = type(other)
        functions = {Const: self.__const_lt, Data: self.__data_lt}

        if type_other not in functions:
            raise ValueError(f"Unsupported operation '<' for Data and {type_other}")

        return functions[type_other](other)

    @unit_control
    def __data_eq(self, other):
        """
        Helper function of eq comparison of Data with Data.
        :param other: Data = Data to compare with
        :return: bool = result of comparison
        """

        return self.value - self.error - other.error <= other.value <= self.value + self.error + other.error

    @unit_control
    def __const_eq(self, other):
        """
        Helper function of eq comparison of Data with Const.
        :param other: Const = Const to compare with
        :return: bool = result of comparison
        """

        return self.value - self.error <= other.value <= self.value + self.error

    @instancemethod
    def __eq__(self, other):
        """
        Compare Data with other objects.
        :param other: Union[Data, Const] = object to compare with
        :return: bool = result of comparison
        """

        type_other = type(other)
        functions = {Const: self.__const_eq, Data: self.__data_eq}
        if type_other not in functions:
            raise ValueError(f"Unsupported operation '==' for Data and {type_other}")

        return functions[type_other](other)

    @unit_control
    def __data_gt(self, other):
        """
        Helper function of gt comparison of Data with Data.
        :param other: Data = Data to compare with
        :return: bool = result of comparison
        """

        return self.value - self.error - other.error > other.value

    @unit_control
    def __const_gt(self, other):
        """
        Helper function of eq comparison of Data with Const.
        :param other: Const = Const to compare with
        :return: bool = result of comparison
        """

        return self.value - self.error > other.value

    @instancemethod
    def __gt__(self, other):
        """
        Compare Data with other objects.
        :param other: Union[Data, Const] = object to compare with
        :return: bool = result of comparison
        """

        type_other = type(other)
        functions = {Const: self.__const_gt, Data: self.__data_gt}
        if type_other not in functions:
            raise ValueError(f"Unsupported operation '==' for Data and {type_other}")

        return functions[type_other](other)

    @instancemethod
    def __ne__(self, other):
        """
        Compare Data with other objects.
        :param other: Union[Data, Const] = object to compare with
        :return: bool = result of comparison
        """

        return not self.__eq__(other)

    @instancemethod
    def __ge__(self, other):
        """
        Compare Data with other objects.
        :param other: Union[Data, Const] = object to compare with
        :return: bool = result of comparison
        """

        return self.__gt__(other) or self.__eq__(other)

    @instancemethod
    def __le__(self, other):
        """
        Compare Data with other objects.
        :param other: Union[Data, Const] = object to compare with
        :return: bool = result of comparison
        """

        return self.__lt__(other) or self.__eq__(other)


class Const:

    """
    Class for constants and values with units if they carry no uncertainty (or a neglected one).
    """

    def __init__(self, value, sign):
        """
        Initalize a constant with a unit.
        :param value: Union[int, float] = constant value
        :param sign: Union[str, Unit] = String carrying the unit.
        **sign-EBNF:**
            S := '"' units '"' | '"' units '/' units '"'
            units := unit | unit ';' units
            unit := string | string '^' integer
        """

        if isinstance(sign, str):
            sign = sign.split("/")
            if len(sign) > 1:
                sign = ["" if s == "1" else s for s in sign]
                self.unit = Unit(sign[0], sign[1])
            else:
                self.unit = Unit(sign[0])
        else:
            self.unit = sign

        self.value = float(value)

    @instancemethod
    def __str__(self):
        """
        Creates a string representation of the Const.
        :return: str = representation of the Const
        """

        string = str(self.value)
        unit_string = str(self.unit)
        if unit_string != "":
            string += " " + unit_string
        return string

    @instancemethod
    def __repr__(self):
        return self.__str__()

    @instancemethod
    def __mul__(self, other):
        """
        Multiplication with other.
        :param other: Union[Data, Const, int, float] = other object to multiply with
        :return: Union[Data, Const] = Result type depends on the other object
        """

        if isinstance(other, (int, float)):
            value = self.value * other
            unit = self.unit
            return Const(value, sign=unit)

        elif isinstance(other, Const):
            value = self.value * other.value
            unit = self.unit * other.unit
            return Const(value, sign=unit)

        elif isinstance(other, Data):
            value = self.value * other.value
            unit = self.unit * other.unit
            n = other.n
            error = self.value * other.error
            return Data(str(value), str(error), n=n, sign=unit)

        else:
            raise TypeError(f"unsupported operand '*' for Const and {type(other)}")

    @instancemethod
    def __rmul__(self, other):
        """
        Multiplication with other.
        :param other: Union[Data, Const, int, float] = other object to multiply with
        :return: Union[Data, Const] = result type depends on the other object
        """

        return self.__mul__(other)

    @instancemethod
    def __add__(self, other):
        """
        Addition with other Const.
        :param other: Union[Const, Data, int, float] = other object to add with
        :return: Union[Const, Data, int, float] = result of the subtraction
        """

        if isinstance(other, Const):
            if self.unit == other.unit:
                return Const(self.value + other.value, sign=self.unit)
            else:
                raise ArithmeticError("Addition of Data with different units is not possible")

        elif isinstance(other, Data):
            if self.unit == other.unit:
                return Data(str(self.value + other.value), str(other.error), n=other.n, sign=self.unit)
            else:
                raise ArithmeticError("Addition of Data and Const with different units is not possible")

        elif isinstance(other, (int, float)):
            if self.unit == Unit():
                return self.value + other
            else:
                raise ArithmeticError("Addition of values with different units is not possible")

        else:
            raise TypeError(f"unsupported operand '+' for Const and {type(other)}")

    @instancemethod
    def __radd__(self, other):
        return self.__add__(other)

    @instancemethod
    def __sub__(self, other):
        """
        Subtraction with other Const.
        :param other: Union[Const, Data, int, float] = other object to add with
        :return: Union[Const, Data] = result of the subtraction
        """

        return self.__add__(-1 * other)

    @instancemethod
    def __rsub__(self, other):
        neg_self = -1 * self
        return neg_self.__add__(other)

    @instancemethod
    def __truediv__(self, other):
        """
        Division with other object.
        :param other: Union[Data, Const, int, float] = other object to add with
        :return: Union[Data, Const] = Result type depends on the other object
        """

        if isinstance(other, (int, float)):
            value = self.value / other
            unit = self.unit
            return Const(value, sign=unit)

        elif isinstance(other, Const):
            value = self.value / other.value
            unit = self.unit / other.unit
            return Const(value, sign=unit)

        elif isinstance(other, Data):
            value = self.value / other.value
            unit = self.unit / other.unit
            n = other.n
            error = self.value / other.error
            return Data(str(value), str(error), n=n, sign=unit)

        else:
            raise TypeError(f"unsupported operand '/' for Const and {type(other)}")

    @instancemethod
    def __rtruediv__(self, other):
        """
        Division with other object.
        :param other: Union[int, float] = other object to add with
        :return: Union[Data, Const] = Result type depends on the other object
        """

        if isinstance(other, (int, float)):
            result = other / self.value
            unit = self.unit.flip()
            return Const(result, unit)
        else:
            raise ValueError(f"Unsupported operation '/' for Const and {type(other)}")

    @instancemethod
    def __pow__(self, other):
        """
        Power a Const object
        :param other: Union[int, float] = object to power with
        :return: Const = result of the calculation
        """

        typ_other = type(other)
        if typ_other == int or typ_other == float:
            result = self.value ** other
            unit = self.unit ** other
            return Const(result, unit)
        elif typ_other == Data:
            raise ArithmeticError("Try to use a Formula instead!")
        else:
            raise TypeError(f"Unsupported operation '/' for Const and {typ_other}")

    @unit_control
    def __lt__(self, other):
        """
        Compare Const with other objects.
        :param other: Const = object to compare with
        :return: bool = result of comparison
        """

        if isinstance(other, Const):
            return self.value < other.value
        raise TypeError(f"unsupported operation '<' for Data and {type(other)}")

    @unit_control
    def __le__(self, other):
        """
        Compare Const with other objects.
        :param other: Const = object to compare with
        :return: bool = result of comparison
        """

        if isinstance(other, Const):
            return self.value <= other.value
        raise TypeError(f"unsupported operation '<=' for Data and {type(other)}")

    @unit_control
    def __eq__(self, other):
        """
        Compare Const with other objects.
        :param other: Const = object to compare with
        :return: bool = result of comparison
        """

        if isinstance(other, Const):
            return self.value == other.value
        raise TypeError(f"unsupported operation '==' for Data and {type(other)}")

    @unit_control
    def __ne__(self, other):
        """
        Compare Const with other objects.
        :param other: Const = object to compare with
        :return: bool = result of comparison
        """

        if isinstance(other, Const):
            return self.value != other.value
        raise TypeError(f"unsupported operation '!=' for Data and {type(other)}")

    @unit_control
    def __ge__(self, other):
        """
        Compare Const with other objects.
        :param other: Const = object to compare with
        :return: bool = result of comparison
        """

        if isinstance(other, Const):
            return self.value >= other.value
        raise TypeError(f"unsupported operation '>=' for Data and {type(other)}")

    @unit_control
    def __gt__(self, other):
        """
        Compare Const with other objects.
        :param other: Const = object to compare with
        :return: bool = result of comparison
        """

        if isinstance(other, Const):
            return self.value > other.value
        raise TypeError(f"unsupported operation '>' for Data and {type(other)}")
