from pyrror.controls import type_check, instancemethod
from copy import deepcopy


class Unit:
    """
    Unit class.
    The class can not(!) identify pre-factors like km as 1000 m
    """

    def __init__(self, numerator="", denominator=""):  # numerator = "m;N" , denominator = "s^2;N"  => m/s^2
        """
        Initialize a unit. Units are given in the following format:
            **sign-EBNF:**
            S := '"' units '"'
            units := unit | unit ';' units
            unit := string | string '^' integer
        :param numerator: string = unit constructed as shown in grammar
        :param denominator:string = unit constructed as shown in grammar
        """

        type_check((numerator, str), (denominator, str))

        self.numerator = {}  # [[sign,counter],...]  ; m^2*N = [[m,2],[N,1]]
        self.denominator = {}

        if numerator != "":
            num = [element.split("^") if "^" in element else [element, 1] for element in numerator.split(";")]
            self.numerator = {element[0]: float(element[1]) for element in num}

        if denominator != "":
            den = [element.split("^") if "^" in element else [element, 1] for element in denominator.split(";")]
            self.denominator = {element[0]: float(element[1]) for element in den}

        self.__ease()

    @instancemethod
    def __str__(self):
        """
        Creates pretty string for the units.
        :return: str = representation of the units
        """

        if not self.numerator and not self.denominator:
            return ""
        elif not self.numerator and self.denominator:
            num = "1"
        else:
            numerator = [(unit, int(power)) if power == int(power) else (unit, power) for unit, power in
                         self.numerator.items()]
            units = [f"{unit}" if 1 == power else f"{unit}^{power}" for unit, power in numerator]
            num = '*'.join(units)

        if self.denominator:
            denominator = [(unit, int(power)) if power == int(power) else (unit, power) for unit, power in
                           self.denominator.items()]
            units = [f"{unit}" if 1 == power else f"{unit}^{power}" for unit, power in denominator]
            if len(units) == 1:
                den = units[0]
            else:
                den = f"({'*'.join(units)})"

        if self.numerator and not self.denominator:
            return num
        elif not self.numerator and self.denominator:
            return f"1/{den}"
        elif num.count("*") > 0:
            return f"({num})/{den}"
        else:
            return f"{num}/{den}"

    @instancemethod
    def __repr__(self):
        return self.__str__()

    @instancemethod
    def __mul__(self, other):
        """
        Multiplication with other unit.
        :param other: Unit = another unit to multiply with
        :return: Unit = Result of the multiplication
        """

        type_check((other, Unit))

        denominator = deepcopy(self.denominator)
        numerator = deepcopy(self.numerator)

        for unit in other.denominator.keys():
            if unit in denominator:
                denominator[unit] += other.denominator[unit]
            else:
                denominator[unit] = other.denominator[unit]

        for unit in other.numerator.keys():
            if unit in numerator:
                numerator[unit] += other.numerator[unit]
            else:
                numerator[unit] = other.numerator[unit]

        result = Unit()
        result.numerator = numerator
        result.denominator = denominator
        result.__ease()
        return result

    @instancemethod
    def __pow__(self, other):
        """
        Power to an unit.
        :param other: Union[int, float] = power
        :return: Unit = former unit power given int
        """

        if not isinstance(other, (float, int)):
            raise ValueError("Power with %s is not defined")

        denominator = deepcopy(self.denominator)
        numerator = deepcopy(self.numerator)

        for unit in denominator.keys():
            denominator[unit] *= other
        for unit in numerator.keys():
            numerator[unit] *= other

        result = Unit()
        result.numerator = numerator
        result.denominator = denominator
        result.__ease()
        return result

    @instancemethod
    def __truediv__(self, other):
        """
        Division with other unit.
        :param other: Unit = another unit to divide with
        :return: Unit = Result of the division
        """

        type_check((other, Unit))
        inv_other = other.flip()
        return self * inv_other

    def __ease(self):
        """
        Simplifies the current given units. For example m * s / m -> s
        :return: void
        """

        num_keys = tuple(self.numerator.keys())
        den_keys = tuple(self.denominator.keys())

        # shorten fracture
        for unit in num_keys:
            if unit in self.denominator:
                min_power = min(self.denominator[unit], self.numerator[unit])
                self.denominator[unit] -= min_power
                self.numerator[unit] -= min_power

        # eliminate zeros
        for unit in num_keys:
            if self.numerator[unit] == 0:
                del self.numerator[unit]
            elif self.numerator[unit] < 0:
                self.denominator[unit] = -1 * self.numerator[unit]
                del self.numerator[unit]

        for unit in den_keys:
            if self.denominator[unit] == 0:
                del self.denominator[unit]
            elif self.denominator[unit] < 0:
                self.numerator[unit] = -1 * self.denominator[unit]
                del self.denominator[unit]

        return True

    @instancemethod
    def __eq__(self, other):
        """
        Compares two different Units.
        :param other: Unit = other Unit to compare with
        :return: bool
        """
        if type_check((other, Unit)):
            if self.denominator == other.denominator and self.numerator == other.numerator:
                return True
            else:
                return False

    @instancemethod
    def flip(self):
        """
        Flips the Unit. E.g. m/s -> s/m.
        :return: Unit = flipped unit
        """
        result = Unit()
        result.numerator = self.denominator
        result.denominator = self.numerator
        return result
