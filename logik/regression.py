from sympy import Matrix
import sympy

from logik.data import Data, Const
from logik.formula import Formula
from logik.table import Table
from logik.controls import type_check
from abc import ABC, abstractmethod
from logik.chi_2 import Chi2


class Regression(ABC):

    def __init__(self, tab, data_dict):
        self.tab = tab
        self.data_dict = data_dict

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def calc(self, x):
        pass

    def residues(self):
        chi2 = Chi2(self, self.tab)
        chi2.residues_show()


class SimpleRegression(Regression):

    def __init__(self, table, data_dict, n=2):
        Regression.__init__(self, table, data_dict)

        type_check((table, Table))
        type_check((data_dict, dict))
        type_check((n, int))

        self.n = n
        self.a = 0
        self.b = 0
        self.__calc()

    def __str__(self):
        string = "Regression:\n\ty = a + b * x"
        string += "\n\ta: %s" % self.a
        string += "\n\tb: %s" % self.b
        string += "\n" + str(Chi2(self, self.tab))
        return string

    def __calc(self):
        data_points = []
        for row in self.tab.datas:
            if type(row[self.data_dict["x"]]) in [Data, Const]:
                x = row[self.data_dict["x"]].value
            elif type(row[self.data_dict["x"]]) in [int, float]:
                x = row[self.data_dict["x"]]
            else:
                raise TypeError("at least element: '%s' have an incompatible type '%s'" %
                                (row[self.data_dict["x"]], type(row[self.data_dict["x"]])))

            if type(row[self.data_dict["y"]]) in [Data, Const]:
                y = row[self.data_dict["y"]].value
            elif type(row[self.data_dict["y"]]) in [int, float]:
                y = row[self.data_dict["y"]]
            else:
                raise TypeError("at least element: '%s' have an incompatible type '%s'" %
                                (row[self.data_dict["y"]], type(row[self.data_dict["y"]])))

            data_points.append((x, y))

        x_2 = sum(element[0] ** 2 for element in data_points)
        x_y = sum(element[0] * element[1] for element in data_points)
        x = sum(element[0] for element in data_points)
        y = sum(element[1] for element in data_points)
        n = len(data_points)

        delta_2 = n * x_2 - x ** 2

        a = 1 / delta_2 * (x_2 * y - x * x_y)
        b = 1 / delta_2 * (n * x_y - x * y)

        s_2 = 1 / (n - 2) * sum((element[1] - (a + b * element[0])) ** 2 for element in data_points)

        delta_a = (s_2 / delta_2 * x_2) ** 0.5
        delta_b = (n * s_2 / delta_2) ** 0.5

        if delta_a:
            self.a = Data(str(a), str(delta_a), n=self.n)
        else:
            self.a = a
        if delta_b:
            self.b = Data(str(b), str(delta_b), n=self.n)
        else:
            self.b = b

    def calc(self, x):
        if type(x) not in [int, float]:
            raise TypeError("get unexpeced type '%s'. Try int or float instead" % type(x))
        f = Formula("a+b*x")
        data = f.calc({"a": self.a, "b": self.b, "x": x})
        cor_data = Data(str(data.value), str(data.error), n=data.n, sign=self.tab.units[self.data_dict["y"]])
        return cor_data


class GaussRegression(Regression):

    """
    weighted linear regression:
        pos = (x,y)
        ignore x-Error
        need y-Error
    """

    def __init__(self, table, data_dict, n=2):
        Regression.__init__(self, table, data_dict)

        type_check((table, Table))
        type_check((data_dict, dict))
        type_check((n, int))

        self.a = 0
        self.b = 0
        self.n = n
        self.__calc()

    def __calc(self):
        data_points = []
        for row in self.tab.datas:
            if type(row[self.data_dict["x"]]) in [Data, Const]:
                x = row[self.data_dict["x"]].value
            elif type(row[self.data_dict["x"]]) in [int, float]:
                x = row[self.data_dict["x"]]
            else:
                raise TypeError("at least element: '%s' have an incompatible type '%s'" %
                                (row[self.data_dict["x"]], type(row[self.data_dict["x"]])))

            if type(row[self.data_dict["y"]]) != Data:
                raise TypeError("at least element: '%s' is not of type Data\ninstead its of type '%s'" %
                                (row[self.data_dict["y"]], type(row[self.data_dict["y"]])))

            data_points.append((x, row[self.data_dict["y"]]))

        eins_error2 = sum([1 / y.error ** 2 for x, y in data_points])
        x2_error2 = sum([x ** 2 / y.error ** 2 for x, y in data_points])
        x_error2 = sum([x / y.error ** 2 for x, y in data_points])
        xy_error2 = sum([(x * y.value) / y.error ** 2 for x, y in data_points])
        y_error2 = sum([y.value / y.error ** 2 for x, y in data_points])

        a_value = (y_error2 * x2_error2 - x_error2 * xy_error2) / (eins_error2 * x2_error2 - x_error2 ** 2)
        a_error = (x2_error2 / (eins_error2 * x2_error2 - x_error2 ** 2)) ** 0.5
        #unit = self.table.units[self.data_dict["y"]]
        unit = ""
        a = Data(str(a_value), str(a_error), n=2, sign=unit)
        # y-intercept

        b_value = (eins_error2 * xy_error2 - x_error2 * y_error2) / (eins_error2 * x2_error2 - x_error2 ** 2)
        b_error = (eins_error2 / (eins_error2 * x2_error2 - x_error2 ** 2)) ** 0.5
        #unit = self.table.units[self.data_dict["y"]] / self.table.units[self.data_dict["x"]]
        unit = ""
        b = Data(str(b_value), str(b_error), n=2, sign=unit)
        # rise

        self.a = a
        self.b = b

    def __str__(self):
        string = "Regression:\n\ty = a + b * x"
        string += "\n\ta: %s" % self.a
        string += "\n\tb: %s" % self.b
        string += "\n" + str(Chi2(self, self.tab))
        return string

    def calc(self, x):
        if type(x) not in [int, float]:
            raise TypeError("get unexpeced type '%s'. Try int or float instead" % type(x))
        f = Formula("a+b*x")
        data = f.calc({"a": self.a, "b": self.b, "x": x})
        cor_data = Data(str(data.value), str(data.error), n=data.n, sign=self.tab.units[self.data_dict["y"]])
        return cor_data


class KovRegression(Regression):

    def __init__(self, formula_string, table, data_dict, vars, n=2):

        type_check((formula_string, str))
        type_check((table, Table))
        type_check((data_dict, dict))
        type_check((n, int))

        Regression.__init__(self, table, data_dict)
        # auch nur fuer 2D
        # formula_string muss die Form y = ... und irgendwas von x haben
        # formula darf maximal y = a*f(x) + b*g(x) + ... sein nicht y = a*f(ax)

        if not table.datas:
            raise ValueError("Table need datas for a regression")

        self.formula_string = formula_string.split("=")[1]
        self.vars = vars
        # var kann ggf. extrahiert werden! checken ob wars überhaupt nötig XXXXX
        self.n = n

        self.dummy = {}
        exec("import sympy", self.dummy)
        exec("from sympy.functions import *", self.dummy)

        for var_ in vars:
            exec("%s = sympy.Symbol('%s')" % (var_, var_), self.dummy)

        for key in data_dict.keys():
            exec("%s = sympy.Symbol('%s')" % (key, key), self.dummy)
        exec("formula = " + formula_string, self.dummy)

        if not self.__isvalide():
            raise ArithmeticError("Covariance does only exists for functions like a*f(x) + b*g(x) + ...\nGot:"
                                  + self.formula_string)

        self.__get_matrix()

    def __isvalide(self):
        if self.dummy["formula"].func == sympy.Add:
            exprs = self.dummy["formula"].args
        else:
            exprs = [self.dummy["formula"]]

        for expr in exprs:
            for arg in expr.args:
                if any([True if str(arg).count(var) > 0 else False for var in self.vars]) and \
                        any([True if str(arg).count(key) > 0 else False for key in self.data_dict]):
                    return False
        return True

    def __get_matrix(self):
        # formula = a*x**2 + b*x**3 + c * exp(x)
        if type(self.dummy["formula"]) == sympy.Add:
            parts = self.dummy["formula"].args
        else:
            parts = [self.dummy["formula"]]

        b_list = []
        a_list = []
        alpha_list = []

        for part in parts:
            if type(part) == sympy.Symbol:
                coeff = part
                expr = sympy.numbers.One()
            else:
                coeff, expr = part.args
            a_list.append(coeff)

            self.dummy["__b__"] = 0
            for data in self.tab.datas:

                if type(data[self.data_dict["x"]]) in [Const, Data]:
                    x = data[self.data_dict["x"]].value
                else:
                    x = data[self.data_dict["x"]]

                if type(data[self.data_dict["y"]]) != Data:
                    raise TypeError("y has to be an object of type Data not %s" % type(data[self.data_dict["y"]]))
                sigma = data[self.data_dict["y"]].error
                y = data[self.data_dict["y"]].value

                exec("__b_f__ = (1 / %s)**2 * %s * %s * sympy.numbers.One()" % (sigma, y, expr), self.dummy)
                exec("__b__ += __b_f__.subs(x, %s)" % x, self.dummy)
            b_list.append(self.dummy["__b__"])

            alpha_line = []
            for part_2 in parts:
                if type(part_2) == sympy.Symbol:
                    expr_2 = sympy.numbers.One()
                else:
                    expr_2 = part_2.args[1]

                self.dummy["__alpha__"] = 0
                for data in self.tab.datas:
                    # data is a Data or error would have been raised above
                    if type(data[self.data_dict["x"]]) in [Const, Data]:
                        x = data[self.data_dict["x"]].value
                    else:
                        x = data[self.data_dict["x"]]
                    sigma = data[self.data_dict["y"]].error
                    exec("__alpha_f__ = (1 / %s)**2 * %s * %s * sympy.numbers.One()" % (sigma, expr, expr_2), self.dummy)
                    exec("__alpha__ += __alpha_f__.subs(x, %s)" % x, self.dummy)

                alpha_line.append(self.dummy["__alpha__"])
            alpha_list.append(alpha_line)

        alpha_matrix = Matrix(alpha_list)
        beta_matrix = Matrix(b_list)
        a_matrix = Matrix(a_list)

        alpha_matrix_inv = alpha_matrix.inv()
        coeff_matrix = alpha_matrix_inv * beta_matrix

        self.coeff_matrix_names = a_matrix
        self.coeff_matrix = coeff_matrix
        self.inverse_alphas = alpha_matrix_inv

    def __str__(self):
        string = "Regression:\n\t" + "y =" + self.formula_string
        for index in range(self.coeff_matrix.shape[0]):
            string += "\n\t%s" % self.coeff_matrix_names[index] + ": %s" % (self.coeff_matrix[index])
        string += "\n" + str(Chi2(self, self.tab))
        return string

    def calc(self, x):
        if type(x) in [Const, Data]:
            x = x.value
        exec("__value__ = formula", self.dummy)
        for index in range(self.coeff_matrix_names.shape[0]):
            exec("__value__ = __value__.subs(%s, %s)" % (self.coeff_matrix_names[index, 0],
                                                         self.coeff_matrix[index, 0]), self.dummy)
        exec("__value__ = __value__.subs(x, %s)" % x, self.dummy)
        value = self.dummy["__value__"]

        exec("__error__ = 0", self.dummy)
        for index in range(self.coeff_matrix_names.shape[0]):
            # first all not mixed terms
            exec("__error__ += (sympy.diff(formula, %s))**2 * %s**2" % (self.coeff_matrix_names[index, 0],
                                                                        self.inverse_alphas[index, index]), self.dummy)

        indices = list(range(self.coeff_matrix_names.shape[0]))
        combis = [(first, second) for first in indices for second in indices if first != second]
        for index1, index2 in combis:
            # include not mixed terms
            exec("__error__ += sympy.diff(formula, %s) * sympy.diff(formula, %s) * %s**2" %
                 (self.coeff_matrix_names[index1, 0], self.coeff_matrix_names[index2, 0],
                  self.inverse_alphas[index1, index2]), self.dummy)

        exec("__error__ = __error__.subs(x, %s)" % x, self.dummy)
        error = self.dummy["__error__"]
        unit = self.tab.units[self.data_dict["y"]]
        return Data(str(value), str(error), n=self.n, sign=unit)


if __name__ == "__main__":
    from logik.table import Table
    from random import randint as rand


    def gauss(x_max):
        return sum(rand(-10, 10) for i in range(5)) / 50 * x_max


    data = [
        -0.849, -0.738, -0.537, -0.354, -0.196,
        -0.019,  0.262,  0.413,  0.734,  0.882,
         1.258,  1.305,  1.541,  1.768,  1.935,
         2.147,  2.456,  2.676,  2.994,  3.200,
         3.318]

    datas = [(Const(i, sign="°C"), Data(str(data[i//5]), "0.05", sign="mV")) for i in range(0, 105, 5)]

    tab = Table(columns=2, column_names=["x", "y"], signs=["°C", "mV"])
    for data in datas:
        tab.add(data)
    print(tab)
    a = KovRegression("y = a + b*x + c*x**2", tab, {"x": 0, "y": 1}, ["a", "b", "c"])
    print(a)
    print(a.calc(80))
