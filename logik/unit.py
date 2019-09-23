from logik.controlls import type_check, instancemethod
from copy import deepcopy


class Unit(object):

    def __init__(self, numerator="", denominator=""):  # numerator = "m;N" , denominator = "s^2;N"  => m/s^2

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

    def __str__(self):
        string = ""
        if self.numerator == [] and self.denominator == []:
            return ""
        elif self.numerator == [] and self.denominator != []:
            string += "1"
        else:
            for element in self.numerator:
                if element != self.numerator[0]:
                    string += "*"
                string += element[0]
                if element[1] != 1:
                    if element[1] == int(element[1]):
                        upper = int(element[1])
                    else:
                        upper = element[1]
                    string += "^%s" % upper

        if self.denominator != []:
            if len(self.numerator) > 1:
                string = "(" + string + ")"
            string += "/"
            if len(self.denominator) > 1:
                string += "("
            for element in self.denominator:
                if element != self.denominator[0]:
                    string += "*"
                string += element[0]
                if element[1] != 1:
                    if element[1] == int(element[1]):
                        upper = int(element[1])
                    else:
                        upper = element[1]
                    string += "^%s" % upper
            if len(self.denominator) > 1:
                string += ")"
        return string

    @instancemethod
    def __mul__(self, other):
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

    def __eq__(self, other):
        if type_check((other, Unit)):
            self.denominator.sort()
            other.denominator.sort()
            self.numerator.sort()
            other.numerator.sort()

            if self.denominator == other.denominator and self.numerator == other.numerator:
                return True
            else:
                return False

    @instancemethod
    def flip(self):
        result = Unit()
        result.numerator = self.denominator
        result.denominator = self.numerator
        return result