import unittest
from logik.table import Table
from logik.data import Data

liste = [(1, 1, 1), (2, 1, 1), (3, 1, 1), (4, 1, 1), (5, 1, 1), (6, 1, 1), (7, 1, 1)]
tab = Table(column_names=["x", "y", "z"], columns=3)
for element in liste:
    tab.add(element)

liste = [(9.0000, 3.11111, Data("14.0", "1.0")), (8.222312, 2, Data("12.0", "1.5")), (2, 7, Data("15.0", "2.0")),
         (4, 9, Data("11.0", "0.50")), (5, 8, Data("1.0", "10")), (6, 1, Data("13.5", "1.5")),
         (7, 2, Data("14.0", "0.70"))]
tab2 = Table(column_names=["x2", "y2", "z2"], columns=3)
for element in liste:
    tab2.add(element)

liste = [(1, 2), (2, 3), (5, 6)]
tab3 = Table(columns=2, column_names=["x", "y"])
for element in liste:
    tab3.add(element)

liste = [(3, 4, 5), (7, 8, 9)]
tab4 = Table(column_names=["x", "y", "z"], columns=3)
for element in liste:
    tab4.add(element)


class MyTestCase(unittest.TestCase):

    def test_add_spe(self):
        try:
            tab + tab2
            raise AssertionError("Tables should not be addable")
        except NameError:
            pass

        try:
            tab + tab3
            raise AssertionError("Tables should not be addable")
        except ValueError:
            pass

        tab5 = tab + tab4
        if tab5.datas != tab.datas + tab4.datas:
            raise AssertionError("Add failed")

    def test_arithmetic_average(self):
        self.assertEqual([str(result) for result in tab.arithmetic_average()], ["(40.0±8.2)*10^-1", "1.0", "1.0"])
        self.assertEqual([str(result) for result in tab2.arithmetic_average()], ["(58.9±9.2)*10^-1", "(4.6±1.2)",
                                                                                 "(124.1±3.5)*10^-1"])

    def test_add(self):
        tab5 = Table(columns=1)
        insert = (1,)  # (1,) ist nötig, da der Rechner (1) direkt auf int 1 vereinfacht
        tab5.add(insert)
        if tab5.datas != [insert]:
            raise AssertionError("add an dataset faild")

        tab6 = Table(columns=10)
        insert = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        tab6.add(insert)
        if tab6.datas != [insert]:
            raise AssertionError("add an dataset failed")

    def test_median(self):
        self.assertEqual(tab.median(), [4, 1, 1])
        self.assertEqual("[%s,%s,%s]" % tuple(tab2.median()), "[6,3.11111,13.5]")
        self.assertEqual(tab3.median(), [2, 3])

    def test_find_peaks(self):
        self.assertEqual(tab.find_peaks(), [[], [], []])
        result = tab2.find_peaks()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], [])
        self.assertEqual(result[1], [9])
        self.assertEqual(len(result[2]), 0)
        self.assertEqual(tab3.find_peaks(), [[], []])

    def test_find_dips(self):
        self.assertEqual(tab.find_dips(), [[], [], []])

        result = tab2.find_dips()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], [2])
        self.assertEqual(result[1], [2, 1])
        self.assertEqual(len(result[2]), 0)

        self.assertEqual(tab3.find_dips(), [[], []])

    def test_modus(self):
        self.assertEqual(tab.modus(), [[1, 2, 3, 4, 5, 6, 7], [1], [1]])
        self.assertEqual(tab2.modus(), [[9.0, 8.222312, 2, 4, 5, 6, 7], [2], [14.0]])
        self.assertEqual(tab3.modus(), [[1, 2, 5], [2, 3, 6]])

    def test_max(self):
        self.assertEqual(tab.max(), [7, 1, 1])
        self.assertEqual("[%s, %s, %s]" % tuple(tab2.max()), "[9.0, 9, (15.0±2.0)]")
        self.assertEqual(tab3.max(), [5, 6])
        self.assertEqual(tab4.max(), [7, 8, 9])

    def test_min(self):
        self.assertEqual(tab.min(), [1, 1, 1])
        self.assertEqual("[%s, %s, %s]" % tuple(tab2.min()), "[2, 1, (0.1±1.0)*10^1]")
        self.assertEqual(tab3.min(), [1, 2])
        self.assertEqual(tab4.min(), [3, 4, 5])


if __name__ == '__main__':
    print("Manuelle Prüfung nöetig")
    print(tab)
    print("")
    print(tab2)
    print("")
    print(tab3)
    print("")
    print(tab4)
    unittest.main()
