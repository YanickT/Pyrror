from scipy.stats import chi2
from logik.data import Const, Data
from logik.graph import Graph


class Chi2:

    def __init__(self, reg, tab):
        self.reg = reg
        self.residues = []

        self.__calc()

    def __str__(self):
        return "Chi2     : %s" % (self.p * 100) + "%" + "\nChi2 red.: %s" % self.red

    def __calc(self):
        degree_of_freedom = len(self.reg.tab.datas) - self.reg.n
        total_diff = 0
        for data in self.reg.tab.datas:
            x = data[self.reg.data_dict["x"]]
            y = data[self.reg.data_dict["y"]]
            y_theo = self.reg.calc(x)
            if type(x) in [Const, Data]:
                x = x.value
            if type(y) in [Const, Data]:
                y = y.value
            if type(y_theo) in [Const, Data]:
                y_theo = y_theo.value
            self.residues.append((x, y - y_theo))
            total_diff += (y - y_theo) ** 2 / y_theo
        self.diff = total_diff
        
        self.p = 1 - chi2.cdf(total_diff, degree_of_freedom)
        self.red = total_diff / degree_of_freedom

    def residues_show(self):
        graph = Graph()
        graph.add_datas([data[0] for data in self.residues], [data[1] for data in self.residues])
        graph.show()
