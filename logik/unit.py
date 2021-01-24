from logik.controlls import type_check, instancemethod
from copy import deepcopy


class Unit:

    """
    Unit class.
    The class can not(!) identify prefactors like km as 1000 m
    """

    def __init__(self, numerator="", denominator=""):  # numerator = "m;N" , denominator = "s^2;N"  => m/s^2
        """
        Initialize a unit. Units are given in the following format:
        S := units | units '/' units
        units := unit | unit ';' unit
        unit := string | string '^' integer
        :param numerator: string = unit constructed as shown in grammar
        :param denominator:string = unit constructed as shown in grammar
        """

        type_check((numerator, str), (denominator, str))

        self.numerator = []  # [[sign,counter],...]  ; m^2*N = [[m,2],[N,1]]
        self.denominator = []

        if numerator != "":
            for element in numerator.split(";"):
                element = element.split("^")
                if len(element) > 1:
                    self.numerator.append([element[0], float(element[1])])
                else:
                    self.numerator.append([element[0], 1])

        if denominator != "":
            for element in denominator.split(";"):
                element = element.split("^")
                if len(element) > 1:
                    self.denominator.append([element[0], float(element[1])])
                else:
                    self.denominator.append([element[0], 1])

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
            unit_strings = ["1"]
        else:
            numerator = [(unit, int(power)) if power == int(power) else (unit, power) for unit, power in self.numerator]
            units = [f"{unit}" if 1 == power else f"{unit}^{power}" for unit, power in numerator]
            unit_strings = ["*".join(units)]

        if self.denominator:
            denominator = [(unit, int(power)) if power == int(power) else (unit, power) for unit, power in self.denominator]
            units= [f"{unit}" if 1 == power else f"{unit}^{power}" for unit, power in denominator]
            unit_strings.append("*".join(units))

        string = "/".join([f"({units})" if units.count("*") else f"{units}" for units in unit_strings])
        return string

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

        other_denominator = deepcopy(other.denominator)
        other_numerator = deepcopy(other.numerator)

        signs = [element[0] for element in self.denominator]

        for element in other_denominator:
            if signs.count(element[0]) > 0:
                for index, sign in enumerate(signs):
                    if sign == element[0]:
                        break
                denominator[index][1] += element[1]
            else:
                denominator.append(element)

        signs = [element[0] for element in self.numerator]
        for element in other_numerator:
            if signs.count(element[0]) > 0:
                for index, sign in enumerate(signs):
                    if sign == element[0]:
                        break
                numerator[index][1] += element[1]
            else:
                numerator.append(element)

        result = Unit()
        result.numerator = numerator
        result.denominator = denominator
        result.__ease()
        return result

    @instancemethod
    def __pow__(self, other):
        """
        Power to an unit.
        :param other: int = power
        :return: Unit = former unit power given int
        """

        denominator = deepcopy(self.denominator)
        numerator = deepcopy(self.numerator)
        signs = [element[0] for element in self.denominator]

        if type(other) != float and type(other) != int:
            raise ValueError("Power with %s is not defined")
        for element in numerator:
            element[1] *= other
        for element in denominator:
            element[1] *= other

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

        denominator = deepcopy(self.denominator)
        numerator = deepcopy(self.numerator)

        other_denominator = deepcopy(other.denominator)
        other_numerator = deepcopy(other.numerator)

        signs = [element[0] for element in self.denominator]

        for element in other_numerator:
            if signs.count(element[0]) > 0:
                for index, sign in enumerate(signs):
                    if sign == element[0]:
                        break
                denominator[index][1] += element[1]
            else:
                denominator.append(deepcopy(element))

        signs = [element[0] for element in self.numerator]
        for element in other_denominator:
            if signs.count(element[0]) > 0:
                for index, sign in enumerate(signs):
                    if sign == element[0]:
                        break
                numerator[index][1] += element[1]
            else:
                numerator.append(deepcopy(element))

        result = Unit()
        result.numerator = numerator
        result.denominator = denominator
        result.__ease()
        return result

    def __ease(self):
        """
        Simplifies the current given units. For example m * s / m -> s
        :return: void
        """
        num_sign = [element[0] for element in self.numerator]
        den_sign = [element[0] for element in self.denominator]

        for num_i, num_element in enumerate(num_sign):

            if den_sign.count(num_element) > 0:
                for den_i, den_element in enumerate(den_sign):
                    if den_element == num_element:
                        break

                while self.denominator[den_i][1] > 0 and self.numerator[num_i][1] > 0:
                    self.numerator[num_i][1] -= 1
                    self.denominator[den_i][1] -= 1

        for element in self.numerator:
            if element[1] < 0:
                self.denominator.append([element[0], -element[1]])
                self.numerator.remove(element)
        self.numerator = [element for element in self.numerator if element[1] != 0]

        for element in self.denominator:
            if element[1] < 0:
                self.numerator.append([element[0], -element[1]])
                self.denominator.remove(element)
        self.denominator = [element for element in self.denominator if element[1] != 0]

        return True

    @instancemethod
    def __eq__(self, other):
        """
        Compares two different Units.
        :param other: Unit = other Unit to compare with
        :return: bool
        """
        if type_check((other, Unit)):
            den1 = deepcopy(self.denominator)
            den1.sort()
            den2 = deepcopy(other.denominator)
            den2.sort()
            nom1 = deepcopy(self.numerator)
            nom1.sort()
            nom2 = deepcopy(other.numerator)
            nom2.sort()

            if den1 == den2 and nom1 == nom2:
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
