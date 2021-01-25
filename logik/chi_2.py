import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np

from logik.data import Const, Data


class Chi2:

    """
    Chi2 class. Calculates the Chi2 and the residues for a given Regression.
    """

    def __init__(self, reg):
        """
        Initialize the Chi2.
        :param reg: Regression = Regression class to calculate Chi2 for
        """

        self.reg = reg
        self.residues = []
        self.chi2 = 0
        self.probability = None
        self.chi_red = None

        self.__calc()

    def __str__(self):
        """
        Creates string representation for Chi2.
        :return: str = representation for Chi2
        """

        return f"Chi2     : {self.chi2}, Probability: {self.probability}, Chi2 red.: {self.chi_red}"

    def __calc(self):
        """
        Calculate Chi2 and Chi2_red.
        :return: void
        """

        degree_of_freedom = len(self.reg.tab.datas) - self.reg.n_o_f_p

        for row in self.reg.tab.datas:
            x = row[self.reg.data_dict["x"]]
            y = row[self.reg.data_dict["y"]]

            if isinstance(x, (Const, Data)):
                x = x.value
            if isinstance(y, (Const, Data)):
                y = y.value

            y_theo = self.reg.calc(x)
            if isinstance(y_theo, (Const, Data)):
                y_theo = y_theo.value

            self.residues.append((x, y - y_theo))
            self.chi2 += (y - y_theo) ** 2 / y_theo
        
        self.probability = stats.chi2.sf(self.chi2, degree_of_freedom)
        self.chi_red = self.chi2 / degree_of_freedom

    def show_residues(self):
        """
        Creates plot of the residues.
        :return: void
        """
        xs, ys = tuple(zip(*self.residues))

        plt.plot(xs, ys, "x")
        plt.xlabel = self.reg.tab.column_names[self.reg.data_dict['x']]
        ylabel = self.reg.tab.column_names[self.reg.data_dict['y']]
        plt.ylabel = f"{ylabel} - $\\mathrm{{{ylabel}_{{theo}}}}$"
        plt.title(f"Residues, $\chi^2 = {self.chi2}$")
        plt.show()
