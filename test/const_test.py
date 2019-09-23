import unittest
from logik.data import Const

a = Const(10, "m")
b = Const(1, "s")
c = Const(10, "m/s")
d = Const(10, "m^2")
e = a / b
# e = Const(10, "m/s)
f = Const(100, "m")


class MyTestCase(unittest.TestCase):

    def test_lt(self):
        self.assertEqual(a < f, True)
        self.assertEqual(f < a, False)
        self.assertEqual(e < c, False)
        self.assertEqual(c < e, False)

    def test_le(self):
        self.assertEqual(a <= f, True)
        self.assertEqual(f <= a, False)
        self.assertEqual(e <= c, True)
        self.assertEqual(c <= e, True)

    def test_eq(self):
        self.assertEqual(c == e, True)
        self.assertEqual(e == c, True)
        self.assertEqual(a == f, False)
        self.assertEqual(f == a, False)

    def test_ne(self):
        self.assertEqual(c != e, False)
        self.assertEqual(e != c, False)
        self.assertEqual(a != f, True)
        self.assertEqual(f != a, True)

    def test_ge(self):
        self.assertEqual(c >= e, True)
        self.assertEqual(e >= c, True)
        self.assertEqual(a >= f, False)
        self.assertEqual(f >= a, True)

    def test_gt(self):
        self.assertEqual(a > f, False)
        self.assertEqual(f > a, True)
        self.assertEqual(e > c, False)
        self.assertEqual(c > e, False)

    def test_pow(self):
        self.assertEqual(str(a**2), "100.0 m^2")
        self.assertEqual(str(b**2), "1.0 s^2")
        self.assertEqual(str(c**3), "1000.0 m^3/s^3")
        self.assertEqual(str(c**0), "1.0")
        self.assertEqual(str(a ** (-2)), "0.01 1/m^2")

    def test_truediv(self):
        self.assertEqual(str(a / b), "10.0 m/s")
        self.assertEqual(str(f / a), "10.0")
        self.assertEqual(str(a / c), "1.0 s")
        self.assertEqual(str(e), "10.0 m/s")

    def test_rtruediv(self):
        self.assertEqual(str(a / 10), "1.0 m")
        self.assertEqual(str(c / (-10)), "-1.0 m/s")
        self.assertEqual(str(f / 4), "25.0 m")

        self.assertEqual(str(10 / a), "1.0 1/m")
        self.assertEqual(str(0 / b), "0.0 1/s")
        self.assertEqual(str(-10 / c), "-1.0 s/m")
        self.assertEqual(str(4 / f), "0.04 1/m")

    def test_add(self):
        self.assertEqual(a + f, Const(110, "m"))
        self.assertEqual(c + e, Const(20, "m/s"))

    def test_mul(self):
        self.assertEqual(str(a * b), "10.0 m*s")
        self.assertEqual(str(c * b), "10.0 m")
        self.assertEqual(str(d * c), "100.0 m^3/s")

    def test_str(self):
        self.assertEqual(str(a), "10.0 m")
        self.assertEqual(str(b), "1.0 s")
        self.assertEqual(str(c), "10.0 m/s")
        self.assertEqual(str(d), "10.0 m^2")
        self.assertEqual(str(e), "10.0 m/s")
        self.assertEqual(str(f), "100.0 m")

    def test_rmul(self):
        self.assertEqual(str(a*10), "100.0 m")
        self.assertEqual(str(b*0), "0.0 s")
        self.assertEqual(str(c*(-10)), "-100.0 m/s")
        self.assertEqual(str(f*4), "400.0 m")

        self.assertEqual(str(10 * a), "100.0 m")
        self.assertEqual(str(0 * b), "0.0 s")
        self.assertEqual(str(-10 * c), "-100.0 m/s")
        self.assertEqual(str(4 * f), "400.0 m")


if __name__ == '__main__':
    unittest.main()
