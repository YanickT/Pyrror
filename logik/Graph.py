import matplotlib.pyplot as plt


class Graph:

    dots = ["o", "--", "^", "s"]
    colors = ["b", "g", "r"]
    line = "-"

    def __init__(self):
        self.size = {
            "x_min": 0, "x_max": 10,
            "y_min": 0, "y_max": 10
        }
        self.scale_flag = False
        self.args = {
            "xlabel": "x",
            "ylabel": "y"
        }
        self.datas = []
        self.counter = {
            "lines": 0,
            "dots": 0
        }

    def label(self, xlabel=None, ylabel=None):
        if xlabel is not None:
            self.args["xlabel"] = xlabel
        if ylabel is not None:
            self.args["ylabel"] = ylabel
        plt.xlabel(self.args["xlabel"])
        plt.ylabel(self.args["ylabel"])

    def scale(self, x=(None, None), y=(None, None)):
        # x = (x_1, x_2) y aquivalent
        if len(x) != len(y) or len(y) != 2:
            raise TypeError("invalid data pairs:\n\t" + str(x) + "\n\t" + str(y) + "\nat least one is invalid")
        plt.axis(self.size["x_min"], self.size["x_max"], self.size["y_min"], self.size["y_max"])
        self.scale_flag = True

    def add_datas(self, x, y, *args, **kwargs):
        plt.plot( x, y, "b" + self.dots[self.counter["dots"] % len(self.dots)], *args, **kwargs)
        self.counter["dots"] += 1

    def add_curve(self):
        pass

    @staticmethod
    def show():
        plt.show()