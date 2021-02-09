import unittest
from pyrror.data import Data

a = Data("10", "1")
b = Data("10", "1.0")
c = Data("3", "1.0", sign="m")

d = Data("10", "1")
e = Data("13", "2.0")
f = Data("20", "2")


class MyTestCase(unittest.TestCase):
    def test_str(self):
        self.assertEqual(str(Data("10.1", "2.2", n=1)), "(10±2)")
        self.assertEqual(str(Data("10.1", "2.2", n=2)), "(10.1±2.2)")
        self.assertEqual(str(Data("10.1", "2.0", n=4)), "(10.100±2.000)")
        self.assertEqual(str(Data("10.1", "2", n=2)), "(10.1±2.0)")
        self.assertEqual(str(Data("100.1", "20", n=2)), "(10.0±2.0)*10^1")
        self.assertEqual(str(Data("100.1", "1")), "(100±1)")

    def test_mul(self):
        self.assertEqual(str(a * 10), "(10±1)*10^1")
        self.assertEqual(str(a * a), "(10±1)*10^1")
        self.assertEqual(str(b * b), "(10.0±1.4)*10^1")
        self.assertEqual(str(c), "(3.0±1.0) m")
        self.assertEqual(str(c * a), "(3±1)*10^1 m")
        self.assertEqual(str(c * b), "(3.0±1.0)*10^1 m")
        self.assertEqual(str(c * c), "(9.0±4.2) m^2")

    def test_rmul(self):
        self.assertEqual(str(10 * a), str(a * 10))
        self.assertEqual(str(10 * b), str(b * 10))

    def test_add(self):
        self.assertEqual(str(a + a), "(20±1)")
        self.assertEqual(str(a + b), "(20±1)")
        self.assertEqual(str(b + b), "(20.0±1.4)")
        self.assertEqual(str(c + c), "(6.0±1.4) m")

    def test_sun(self):
        self.assertEqual(str(a - a), "(0±1)")
        self.assertEqual(str(a - b), "(0±1)")
        self.assertEqual(str(b - b), "(0.0±1.4)")
        self.assertEqual(str(c - c), "(0.0±1.4) m")

    def test_truediv(self):
        self.assertEqual(str(a / 10), "(10±1)*10^-1")
        self.assertEqual(str(a / a), "(10±1)*10^-1")
        self.assertEqual(str(b / b), "(10.0±1.4)*10^-1")
        self.assertEqual(str(c / a), "(3±1)*10^-1 m")
        self.assertEqual(str(c / b), "(3.0±1.0)*10^-1 m")
        self.assertEqual(str(c / c), "(10.0±4.7)*10^-1")
        self.assertEqual(str(b / c), "(3.3±1.2) 1/m")

    def test_pow(self):
        self.assertEqual(str(a ** 2), "(10±1)*10^1")
        self.assertEqual(str(b ** 2), "(10.0±1.0)*10^1")
        self.assertEqual(str(c ** 2), "(9.0±3.0) m^2")
        self.assertEqual(str(a ** -2), "(10±1)*10^-3")
        self.assertEqual(str(b ** -2), "(10.0±1.0)*10^-3")
        self.assertEqual(str(c ** -2), "(11.1±3.7)*10^-2 1/m^2")

    def test_lt(self):
        self.assertEqual((d < e), False)
        self.assertEqual((d < f), True)
        self.assertEqual((e < d), False)
        self.assertEqual((e < f), True)
        self.assertEqual((f < e), False)
        self.assertEqual((f < d), False)

    def test_le(self):
        self.assertEqual((d <= e), True)
        self.assertEqual((d <= f), True)
        self.assertEqual((e <= d), True)
        self.assertEqual((e <= f), True)
        self.assertEqual((f <= d), False)
        self.assertEqual((f <= e), False)

    def test_eq(self):
        self.assertEqual((d == e), True)
        self.assertEqual((d == f), False)
        self.assertEqual((e == d), True)
        self.assertEqual((e == f), False)
        self.assertEqual((f == d), False)
        self.assertEqual((f == e), False)

    def test_ne(self):
        self.assertEqual((d != e), False)
        self.assertEqual((d != f), True)
        self.assertEqual((e != d), False)
        self.assertEqual((e != f), True)
        self.assertEqual((f != d), True)
        self.assertEqual((f != e), True)

    def test_ge(self):
        self.assertEqual((d >= e), True)
        self.assertEqual((e >= d), True)
        self.assertEqual((d >= f), False)
        self.assertEqual((f >= d), True)
        self.assertEqual((e >= f), False)
        self.assertEqual((f >= e), True)

    def test_gt(self):
        self.assertEqual((d > e), False)
        self.assertEqual((d > f), False)
        self.assertEqual((e > d), False)
        self.assertEqual((e > f), False)
        self.assertEqual((f > d), True)
        self.assertEqual((f > e), True)


if __name__ == '__main__':
    unittest.main()
