import unittest
from logik.formula import Formula
from logik.data import Data

"""Es wird die calc-Methode der Formula Klasse getestet"""

d1 = Data("10.1", "2.2", n=1)
d2 = Data("9.7", "2.2", n=2)
d3 = Data("3.466", "2.0", n=4)

d4 = Data("8.3", "2", n=2)
d5 = Data("99.25", "20", n=2)
d6 = Data("100.1", "1")

d7 = Data("1", "1", n=2, sign="m/s")
d8 = Data("1", "1", n=2, sign="m^2/s;J")
d9 = Data("1", "1", n=2, sign="J")
d10 = Data("1", "1", n=2, sign="s")


class MyTestCase(unittest.TestCase):
    def test_with_native(self):
        f1 = Formula("x - y")
        f2 = Formula("x/y")
        f3 = Formula("x*y")
        f4 = Formula("x+y")

        #f1
        self.assertEqual(f1.calc({"x": 1, "y": 2}), -1)
        self.assertEqual(f1.calc({"x": 7, "y": 5}), 2)
        self.assertEqual(f1.calc({"x": 2, "y": 2}), 0)

        # f2
        self.assertEqual(f2.calc({"x": 1, "y": 2}), 0.5)
        self.assertEqual(f2.calc({"x": 7, "y": 5}), 1.4)
        self.assertEqual(f2.calc({"x": 2, "y": 2}), 1)

        # f3
        self.assertEqual(f3.calc({"x": 1, "y": 2}), 2)
        self.assertEqual(f3.calc({"x": 7, "y": 5}), 35)
        self.assertEqual(f3.calc({"x": 2, "y": 2}), 4)

        # f4
        self.assertEqual(f4.calc({"x": 1, "y": 2}), 3)
        self.assertEqual(f4.calc({"x": 7, "y": 5}), 12)
        self.assertEqual(f3.calc({"x": 2, "y": 2}), 4)

    def test_with_data(self):
        f1 = Formula("x - y")

        self.assertEqual("%s" % (f1.calc({"x": d1, "y": d1})), "(0±3)")
        self.assertEqual("%s" % (f1.calc({"x": d1, "y": d2})), "(0±3)")
        self.assertEqual("%s" % (f1.calc({"x": d1, "y": d3})), "(7±3)")
        self.assertEqual("%s" % (f1.calc({"x": d1, "y": d4})), "(2±3)")
        self.assertEqual("%s" % (f1.calc({"x": d1, "y": d5})), "(-9±2)*10^1")
        self.assertEqual("%s" % (f1.calc({"x": d1, "y": d6})), "(-90±2)")

        self.assertEqual("%s" % (f1.calc({"x": d2, "y": d1})), "(0±3)")
        self.assertEqual("%s" % (f1.calc({"x": d2, "y": d2})), "(0.0±3.1)")
        self.assertEqual("%s" % (f1.calc({"x": d2, "y": d3})), "(6.2±3.0)")
        self.assertEqual("%s" % (f1.calc({"x": d2, "y": d4})), "(1.4±3.0)")
        self.assertEqual("%s" % (f1.calc({"x": d2, "y": d5})), "(-8.9±2.0)*10^1")
        self.assertEqual("%s" % (f1.calc({"x": d2, "y": d6})), "(-90±2)")

    def test_with_units(self):
        f1 = Formula("x * y")
        self.assertEqual(str(f1.calc({"x": d7, "y": d10})), "(1.0±1.4) m")
        self.assertEqual(str(f1.calc({"x": d9, "y": d7})), "(1.0±1.4) (J*m)/s")

        f2 = Formula("x * y / u")
        self.assertEqual(str(f1.calc({"x": d8, "y": d9, "z": d7, "u": d10})), "(1.0±1.4)")


if __name__ == '__main__':
    unittest.main()
