from sympy import Matrix
import sympy

from logik.data import Data, Const
from logik.formula import Formula
from logik.controls import type_check, list_type_check
from abc import ABC, abstractmethod
from logik.chi_2 import Chi2


class Regression(ABC):
    """
    Abstract class defines what methods and attributes a Regression should have.
    """

    def __init__(self, tab, data_dict, n_o_f_p):
        """
        Initalize a Regression
        :param tab: Table = Table of given Data
        :param data_dict: Dict[str, int] = Dictionary of column usage eg. {'x': 0, 'y': 1}
        :param n_o_f_p: int = Number of fit parameters
        """
        self.tab = tab
        self.data_dict = data_dict

        # number of fit parameters (has to be set for each regression)
        self.n_o_f_p = n_o_f_p

    @abstractmethod
    def __str__(self):
        """
        Creates a string representing the results of the Regression.
        :return: str = representation of the Regression
        """
        pass

    @abstractmethod
    def calc(self, x):
        """
        Calculate the result for a given x. Regression result can be seen as function f(x).
        :param x: Union[float, int] = value to determine f(x) for
        :return: Union[float, int] = f(x)
        """
        pass

    @abstractmethod
    def residues(self):
        """
        Calculate the residues for the Regression.
        :return: void
        """
        pass


class SimpleRegression(Regression):
    """
    Simple unweighted regression ignoring uncertainties.
    """

    def __init__(self, table, data_dict, n=2):
        """
        Initialize regression ignoring uncertainties.
        :param table: Table = Table containing the data for the regression
        :param data_dict: Dict[str, int] = Dictionary specifying which data should be used in Table
        In this case: {'x': <column_index1>, 'y': <column_index2>}
        :param n: int = number of significant digits for the parameters
        """

        Regression.__init__(self, table, data_dict, 2)

        type_check((table, Table))
        type_check((data_dict, dict))
        type_check((n, int))

        self.n = n
        self.a = 0
        self.b = 0
        self.chi2 = None
        self.f = None

        self.__calc()

    def __str__(self):
        """
        Creates a string representing the results of the Regression.
        :return: str = representation of the Regression
        """

        return f"Regression:\n\ty = a + b * x\n\ta: {self.a}\n\tb: {self.b}\n\t{self.chi2}"

    def __calc(self):
        """
        Performs the regression.
        :return: void
        """

        x_pos = self.data_dict["x"]
        y_pos = self.data_dict["y"]
        xs = [row[x_pos].value if isinstance(row[x_pos], (Data, Const)) else row[x_pos] for row in self.tab.datas]
        ys = [row[y_pos].value if isinstance(row[y_pos], (Data, Const)) else row[y_pos] for row in self.tab.datas]

        x_2 = sum(x ** 2 for x in xs)
        x_y = sum(x * y for x, y in zip(xs, ys))
        x = sum(xs)
        y = sum(ys)
        n = len(xs)

        delta_2 = n * x_2 - x ** 2

        a = 1 / delta_2 * (x_2 * y - x * x_y)
        b = 1 / delta_2 * (n * x_y - x * y)

        s_2 = 1 / (n - 2) * sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))

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

        self.chi2 = Chi2(self)
        self.f = Formula("a+b*x")

    def calc(self, x):
        """
        Calculate the result for a given x. Regression result can be seen as function f(x).
        :param x: Union[float, int] = value to determine f(x) for
        :return: Union[float, int] = f(x)
        """

        if type(x) not in [int, float]:
            raise TypeError(f"get unexpected type '{type(x)}'. Try int or float instead")

        data = self.f.calc({"a": self.a, "b": self.b, "x": x})
        data.sign = self.tab.units[self.data_dict["y"]]
        return data

    def residues(self):
        self.chi2.show_residues()


class GaussRegression(Regression):
    """
    weighted linear regression:
        ignore x-uncertainty
        need y-uncertainty
    """

    def __init__(self, table, data_dict, n=2):
        """
        Initialize regression ignoring uncertainties.
        :param table: Table = Table containing the data for the regression
        :param data_dict: Dict[str, int] = Dictionary specifying which data should be used in Table
        In this case: {'x': <column_index1>, 'y': <column_index2>}
        :param n: int = number of significant digits for the parameters
        """

        Regression.__init__(self, table, data_dict, 2)

        type_check((table, Table))
        type_check((data_dict, dict))
        type_check((n, int))

        self.a = 0
        self.b = 0
        self.n = n
        self.chi2 = None
        self.f = None

        self.__calc()

    def __calc(self):
        """
        Performs the regression.
        :return: void
        """

        x_pos = self.data_dict["x"]
        y_pos = self.data_dict["y"]

        xs = [row[x_pos].value if isinstance(row[x_pos], (Data, Const)) else row[x_pos] for row in self.tab.datas]
        ys = [row[y_pos] for row in self.tab.datas]

        if not list_type_check(ys, Data):
            raise TypeError("At least element is not of type Data!")

        one_error2 = sum([1 / y.error ** 2 for y in ys])
        x2_error2 = sum([x ** 2 / y.error ** 2 for x, y in zip(xs, ys)])
        x_error2 = sum([x / y.error ** 2 for x, y in zip(xs, ys)])
        xy_error2 = sum([(x * y.value) / y.error ** 2 for x, y in zip(xs, ys)])
        y_error2 = sum([y.value / y.error ** 2 for y in ys])

        a_value = (y_error2 * x2_error2 - x_error2 * xy_error2) / (one_error2 * x2_error2 - x_error2 ** 2)
        a_error = (x2_error2 / (one_error2 * x2_error2 - x_error2 ** 2)) ** 0.5
        unit = self.tab.units[self.data_dict["y"]]
        # y-intercept
        self.a = Data(str(a_value), str(a_error), n=2, sign=unit)

        b_value = (one_error2 * xy_error2 - x_error2 * y_error2) / (one_error2 * x2_error2 - x_error2 ** 2)
        b_error = (one_error2 / (one_error2 * x2_error2 - x_error2 ** 2)) ** 0.5
        unit = unit / self.tab.units[self.data_dict["x"]]
        # slope
        self.b = Data(str(b_value), str(b_error), n=2, sign=unit)

        self.chi2 = Chi2(self)
        self.f = Formula("a+b*x")

    def __str__(self):
        """
        Creates a string representing the results of the Regression.
        :return: str = representation of the Regression
        """

        return f"Regression:\n\ty = a + b * x\n\ta: {self.a}\n\tb: {self.b}\n\t{self.chi2}"

    def calc(self, x):
        """
        Calculate the result for a given x. Regression result can be seen as function f(x).
        :param x: Union[float, int] = value to determine f(x) for
        :return: Union[float, int] = f(x)
        """

        if isinstance(x, (int, float)):
            raise TypeError(f"get unexpected type '{type(x)}'. Try int or float instead")

        data = self.f.calc({"a": self.a, "b": self.b, "x": x})
        data.sign = self.tab.units[self.data_dict["y"]]
        return data

    def residues(self):
        self.chi2.show_residues()


class CovRegression(Regression):
    """
    Regression using a covariance matrix.
    """

    def __init__(self, formula_string, table, data_dict, pars, n=2):
        """
        Initialize covariance Regression.
        :param formula_string: str = string of the formula which should be fitted.
            **formula_string-EBNF:**
            S := 'y = ' exprs
            exprs := expr | expr '+' exprs | expr '-' exprs
            expr := para '*' func | para
            para := char ?has to be unique?
            func := ?mathematical function of x. Has to be a valid sympy expression?
        :param table: Table = Table containing the data for the regression
        :param data_dict: Dict[str, int] = Dictionary specifying which data should be used in Table
        :param pars: List[str] = List of parameter used in the formula_string
        :param n: int = number of significant digits for the parameters
        """

        type_check((formula_string, str))
        type_check((table, Table))
        type_check((data_dict, dict))
        type_check((n, int))

        Regression.__init__(self, table, data_dict, len(pars))

        self.formula_string = formula_string.split("=")[1]
        self.pars = pars
        self.n = n
        self.chi2 = None

        # prepare dummy environment for calculations
        self.dummy = {}
        exec("import sympy", self.dummy)
        exec("from sympy.functions import *", self.dummy)

        # create a symbol for each parameter
        for par in pars:
            exec(f"{par} = sympy.Symbol('{par}')", self.dummy)

        # create formula and symbol for variable
        exec("x = sympy.Symbol('x')", self.dummy)
        exec("formula = " + formula_string, self.dummy)

        if not self.__isvalide():
            raise ArithmeticError(f"Formula: \n'{formula_string}'\n is invalid")

        self.__calc()

    def __isvalide(self):
        """
        Checks if the given formula is valid.
        :return: bool = validity of the formula
        """

        if isinstance(self.dummy["formula"], sympy.core.add.Add):
            exprs = self.dummy["formula"].args
        else:
            exprs = [self.dummy["formula"]]

        for expr in exprs:
            for arg in expr.args:
                if any([True if str(arg).count(var) > 0 else False for var in self.pars]) and \
                        any([True if str(arg).count(key) > 0 else False for key in self.data_dict]):
                    return False
        return True

    def __calc(self):
        """
        Calculates the covariance matrix.
        :return: void
        """

        if isinstance(self.dummy["formula"], sympy.core.add.Add):
            parts = self.dummy["formula"].args
        else:
            parts = [self.dummy["formula"]]

        b_list = []
        a_list = []
        alpha_list = []

        for part in parts:
            if isinstance(part, sympy.Symbol):
                coeff = part
                expr = sympy.core.numbers.One()
            else:
                coeff, expr = part.args
            a_list.append(coeff)

            self.dummy["__b__"] = 0
            x_pos = self.data_dict["x"]
            y_pos = self.data_dict["y"]
            for row in self.tab.datas:
                x = row[x_pos].value if isinstance(row[x_pos], (Const, Data)) else row[x_pos]

                if not isinstance(row[y_pos], Data):
                    raise TypeError(f"y has to be an object of type Data not {type(row[y_pos])}")

                exec(f"__b_f__ = (1 / {row[y_pos].error})**2 * {row[y_pos].value} * {expr} * sympy.core.numbers.One()",
                     self.dummy)
                exec(f"__b__ += __b_f__.subs(x, {x})", self.dummy)
            b_list.append(self.dummy["__b__"])

            alpha_line = []
            for part_2 in parts:
                if isinstance(part_2, sympy.Symbol):
                    expr_2 = sympy.core.numbers.One()
                else:
                    expr_2 = part_2.args[1]

                self.dummy["__alpha__"] = 0
                for row in self.tab.datas:
                    x = row[x_pos].value if isinstance(row[x_pos], (Const, Data)) else row[x_pos]
                    exec(f"__alpha_f__ = (1 / {row[y_pos].error})**2 * {expr} * {expr_2} * sympy.core.numbers.One()",
                         self.dummy)
                    exec(f"__alpha__ += __alpha_f__.subs(x, {x})", self.dummy)

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

        self.chi2 = Chi2(self)

    def __str__(self):
        """
        Creates a string representing the results of the Regression.
        :return: str = representation of the Regression
        """

        string = f"Regression:\n\ty = {self.formula_string}"
        for index in range(self.coeff_matrix.shape[0]):
            string += f"\n\t{self.coeff_matrix_names[index]}: {self.coeff_matrix[index]}"

        string += f"\n\t{self.chi2}"
        return string

    def calc(self, x):
        """
        Calculate the result for a given x. Regression result can be seen as function f(x).
        :param x: Union[float, int] = value to determine f(x) for
        :return: Union[float, int] = f(x)
        """

        if isinstance(x, (Const, Data)):
            raise TypeError(f"get unexpected type '{type(x)}'. Try int or float instead")

        # calculate the mean value
        exec("__value__ = formula", self.dummy)
        for index in range(self.coeff_matrix_names.shape[0]):
            exec(f"__value__ = __value__.subs({self.coeff_matrix_names[index, 0]}, {self.coeff_matrix[index, 0]})",
                 self.dummy)
        exec(f"__value__ = __value__.subs(x, {x})", self.dummy)
        value = self.dummy["__value__"]

        # calculate the error
        exec("__error__ = 0", self.dummy)
        for index in range(self.coeff_matrix_names.shape[0]):
            # first all not mixed terms
            exec(
                f"__error__ += (sympy.diff(formula, {self.coeff_matrix_names[index, 0]}))**2 * {self.inverse_alphas[index, index]}**2",
                self.dummy)

        indices = list(range(self.coeff_matrix_names.shape[0]))
        combis = [(first, second) for first in indices for second in indices if first != second]
        for index1, index2 in combis:
            # include mixed terms
            exec(f"__error__ += sympy.diff(formula, {self.coeff_matrix_names[index1, 0]}) * sympy.diff(formula, {self.coeff_matrix_names[index2, 0]}) * {self.inverse_alphas[index1, index2]}**2",
                self.dummy)

        exec(f"__error__ = sqrt(__error__.subs(x, {x}))", self.dummy)
        error = self.dummy["__error__"]
        unit = self.tab.units[self.data_dict["y"]]

        return Data(str(value), str(error), n=self.n, sign=unit)

    def residues(self):
        self.chi2.show_residues()


if __name__ == "__main__":
    from logik.table import Table
    from random import randint as rand


    def gauss(x_max):
        return sum(rand(-10, 10) for i in range(5)) / 50 * x_max


    data = [
        -0.849, -0.738, -0.537, -0.354, -0.196,
        -0.019, 0.262, 0.413, 0.734, 0.882,
        1.258, 1.305, 1.541, 1.768, 1.935,
        2.147, 2.456, 2.676, 2.994, 3.200,
        3.318]

    datas = [(Const(i, sign="°C"), Data(str(data[i // 5]), "0.05", sign="mV")) for i in range(0, 105, 5)]

    tab = Table(columns=2, column_names=["x", "y"], signs=["°C", "mV"])
    for data in datas:
        tab.add(data)
    print(tab)
    a = CovRegression("y = a + b*x + c*x**2", tab, {"x": 0, "y": 1}, ["a", "b", "c"])
    print(a)
    print(a.calc(80))
