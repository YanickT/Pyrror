from logik.data import Data, Const
from logik.unit import Unit
from logik.controlls import instancemethod

from sympy import Symbol, pretty, latex
import sympy
import warnings


class Formula:

    """
    Main class for calculations.
    """

    def __init__(self, formula_string):

        """
        Initialize new formula.
        :param formula_string: str = Formula to use
        """

        self.formula_string = formula_string

    @staticmethod
    def __get_units(sympy_exp):
        """
        Calculate the unit by eliminating possible units.
        :param sympy_exp: sympy exp = expression in sympy classes
        :return: the unit of the calculation
        """

        if type(sympy_exp) == sympy.core.add.Add:
            return False

        if type(sympy_exp) == Symbol:
            return [[str(sympy_exp), 1]]

        units = []
        exps = list(sympy_exp.args)
        for exp in exps:
            if type(exp) == sympy.core.power.Pow:
                units.append([str(exp.args[0]), float(exp.args[1])])
            elif type(exp) == Symbol:
                units.append([str(exp), 1])
            elif type(exp) in [sympy.core.numbers.Integer, sympy.core.numbers.Float]:
                pass
            else:
                warnings.warn(f"Unit in non linear function encountered:\n {exp} \n => Ignoring the unit")
                return False

        return units

    @instancemethod
    def __create_formula(self, type_dict):
        """
        Creates formula as sympy expression using exec
        :param type_dict: Dict[type] = Dictionary containing the types of each parameter/variable
        :return: sympy expression of the formula
        """
        dummy = {"Symbol": Symbol, "sympy": sympy}
        exec("from sympy.functions import *", dummy)
        for key in type_dict:
            exec("%s = Symbol('%s')" % (key, key), dummy)
        exec("formula = %s" % self.formula_string, dummy)
        return dummy["formula"]

    @instancemethod
    def __create_error_f(self, type_dict):
        dummy = {"error_f": 0, "formula": self.__create_formula(type_dict), "Symbol": Symbol, "sympy": sympy}
        exec("from sympy.functions import *", dummy)

        for key in type_dict:
            exec("%s = Symbol('%s')" % (key, key), dummy)

        for key, var_type in type_dict.items():
            if var_type == Data:
                d_key = "__delta__" + key
                exec("%s = Symbol('%s')" % (d_key, d_key), dummy)
                exec("error_f += (%s)**2 * (formula.diff(%s))**2" % (d_key, key), dummy)

        return sympy.sqrt(dummy["error_f"])

    @instancemethod
    def __calc_result(self, value_dict, type_dict):
        dummy = {"result": self.__create_formula(type_dict), "Symbol": Symbol, "sympy": sympy}
        exec("from sympy.functions import *", dummy)

        for key in value_dict:
            if type_dict[key] in [int, float]:
                value = value_dict[key]
            else:
                value = value_dict[key].value

            exec("%s = Symbol('%s')" % (key, key), dummy)
            exec("result = result.subs('%s',%s)" % (key, value), dummy)

        return dummy["result"]

    @instancemethod
    def __calc_error(self, value_dict, type_dict):
        dummy = {"error": self.__create_error_f(type_dict), "Symbol": Symbol, "sympy": sympy}
        exec("from sympy.functions import *", dummy)

        for key in value_dict:
            if type_dict[key] in [int, float]:
                value = value_dict[key]

            else:
                value = value_dict[key].value

                if type_dict[key] == Data:
                    error_value = value_dict[key].error
                    d_key = "__delta__" + key
                    exec("%s = Symbol('%s')" % (d_key, d_key), dummy)
                    exec("error = error.subs(%s, %s)" % (d_key, error_value), dummy)
            exec("%s = Symbol('%s')" % (key, key), dummy)
            exec("error = error.subs(%s, %s)" % (key, value), dummy)

        return dummy["error"]

    @instancemethod
    def calc_unit(self, value_dict, type_dict):
        """
        Determine the unit of the result will have.
        :param value_dict: Dict[str: Union[int, float, Data, Const]] = Dict of the variables for the formula
        :param type_dict: Dict[type] = Dictionary containing the types of each parameter/variable
        :return: Unit = Unit of the result of the formula
        """

        dummy = {"unit": self.__create_formula(type_dict), "cur_unit": 1, "Symbol": Symbol, "sympy": sympy}
        exec("from sympy.functions import *", dummy)

        for key in value_dict:
            if not (type_dict[key] in [int, float]):
                numerator = value_dict[key].unit.numerator
                denominator = value_dict[key].unit.denominator

                for unit in numerator.keys():
                    exec("%s = Symbol('%s')" % (unit, unit), dummy)
                    exec("cur_unit *= %s ** %s" % (unit, numerator[unit]), dummy)

                for unit in denominator.keys():
                    exec("%s = Symbol('%s')" % (unit, unit), dummy)
                    exec("cur_unit /= (%s ** %s)" % (unit, denominator[unit]), dummy)

            exec("%s = Symbol('%s')" % (key, key), dummy)
            exec("unit = unit.subs(%s,cur_unit)" % key, dummy)
            dummy["cur_unit"] = 1

        units = self.__get_units(sympy.nsimplify(dummy["unit"]))

        if not units:
            return Unit("")

        numerator = {}
        denominator = {}
        for unit, power in units:
            if power > 0:
                numerator[unit] = power
            else:
                denominator[unit] = -1 * power

        unit = Unit()
        unit.denominator = denominator
        unit.numerator = numerator
        return unit

    @instancemethod
    def latex(self, type_dict):
        """
        Returns formula for error and main value in latex code.
        :param type_dict: Dict[type] = Dictionary containing the types of each parameter/variable
        :return: Tuple[str, str] = (formula, error formula)
        """
        formula = self.__create_formula(type_dict)
        error_f = self.__create_error_f(type_dict)
        return latex(formula), latex(error_f)

    @instancemethod
    def __str__(self):
        """
        Give a string representation of the formula.
        :return: str = representation of the formula
        """
        return self.formula_string

    @instancemethod
    def show_error(self, type_dict):
        """
        Show the formula for the error.
        :param type_dict: Dict[type] = Dictionary containing the types of each parameter/variable.
        :return: str = pretty version of the formula for the error
        """
        error_f = self.__create_error_f(type_dict)
        formula = self.__create_formula(type_dict)

        string = ""
        string += "Formel:\n"
        string += pretty(formula)#, use_unicdoe=False)
        string += "\nFehlerformel nach Gauss:\n"
        string += pretty(error_f)
        return string

    @instancemethod
    def calc(self, value_dict):
        """
        Calculate a value using the formula. Through the types of the value_dict the uncertain variables are determined
        and the propagation of the uncertainty is calculated.
        :param value_dict: Dict[str: Union[int, float, Data, Const]] = Dict of the variables for the formula
        :return: Union[Data, Const, int, float] = Result of the formula. Type depends on the input
        """

        type_dict = {key: type(value) for key, value in value_dict.items()}

        result = float(self.__calc_result(value_dict, type_dict))
        unit = self.calc_unit(value_dict, type_dict)

        if Data in type_dict.values():
            error = float(self.__calc_error(value_dict, type_dict))

            significant_digits = min([value_dict[key].n for key in type_dict if type_dict[key] == Data])
            return Data(str(result), str(error), n=significant_digits, sign=unit)

        elif Const in type_dict:
            return Const(result, unit)

        return result
