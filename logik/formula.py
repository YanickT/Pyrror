from logik.data import Data, Const
from logik.unit import Unit
from logik.controlls import instancemethod

from sympy import Symbol, pretty, latex
import sympy

"""
Hier kann später mit sympy latex code für die Formel erzeugt werden. Dieser kann auch im Tkinter angezeigt werden :)
IN GUI dringend sympy interactive einbauen!!!
Berechnung mit relativfehler moeglich machen
"""


class Formula:

    def __init__(self, formula_string):

        self.formula_string = formula_string

    @staticmethod
    def __get_units(sympy_exp):
        if type(sympy_exp) == sympy.add.Add:
            return False

        units = []
        if type(sympy_exp) == Symbol:
            units.append([str(sympy_exp), 1])
            return units
        exps = list(sympy_exp.args)
        for exp in exps:
            if type(exp) == sympy.power.Pow:
                units.append([str(exp.args[0]), float(exp.args[1])])
            elif type(exp) == Symbol:
                units.append([str(exp), 1])
            elif type(exp) in [sympy.numbers.Integer, sympy.numbers.Float]:
                pass
            else:
                print("Einheit in nicht linearer Funktion:\n\t%s\n\t=> Einheit wird ignoriert" % exp)
                return False
        return units

    @instancemethod
    def __create_formula(self, type_dict):
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
        dummy = {"unit": self.__create_formula(type_dict), "cur_unit": 1, "Symbol": Symbol, "sympy": sympy}
        exec("from sympy.functions import *", dummy)

        for key in value_dict:
            if not (type_dict[key] in [int, float]):
                for sign, number in value_dict[key].unit.numerator:
                    exec("%s = Symbol('%s')" % (sign, sign), dummy)
                    exec("cur_unit = %s ** %s" % (sign, number), dummy)

                for sign, number in value_dict[key].unit.denominator:
                    exec("%s = Symbol('%s')" % (sign, sign), dummy)
                    exec("cur_unit = cur_unit / (%s ** %s)" % (sign, number), dummy)

            exec("%s = Symbol('%s')" % (key, key), dummy)
            exec("unit = unit.subs(%s,cur_unit)" % key, dummy)

        units = self.__get_units(sympy.nsimplify(dummy["unit"]))

        if not units:
            return Unit("")

        numerator = []
        denominator = []
        for unit, power in units:
            if power > 0:
                numerator.append([unit, power])
            else:
                denominator.append([unit, -1 * power])
        unit = Unit()
        unit.denominator = denominator
        unit.numerator = numerator

        return unit

    @instancemethod
    def latex(self, type_dict):
        formula = self.__create_formula(type_dict)
        error_f = self.__create_error_f(type_dict)
        return latex(formula), latex(error_f)

    @instancemethod
    def __str__(self):
        return self.formula_string

    @instancemethod
    def show_error(self, type_dict):
        error_f = self.__create_error_f(type_dict)
        formula = self.__create_formula(type_dict)

        string = ""
        string += "Formel:\n"
        string += pretty(formula)#, use_unicdoe=False)
        string += "\nFehlerformel nach Gauß:\n"
        string += pretty(error_f)#, use_unicode=False)
        return string

    @instancemethod
    def calc(self, value_dict):

        type_dict = {}

        for key, value in value_dict.items():
            type_dict[key] = type(value)

        result = float(self.__calc_result(value_dict, type_dict))
        unit = self.calc_unit(value_dict, type_dict)

        if Data in type_dict.values():
            error = float(self.__calc_error(value_dict, type_dict))

            significant_digits = min([value_dict[key].n for key in type_dict if type_dict[key] == Data])
            return Data(str(result), str(error), n=significant_digits, sign=unit)

        elif Const in type_dict:
            return Const(result, unit)

        return result
