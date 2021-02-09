import unittest
from pyrror.unit import Unit

a = Unit("m")
b = Unit("s")
c = Unit("m^2")
d = Unit("m;s")
e = Unit("s;m")
f = Unit("N;m", "kg;s")
g = Unit()


class MyTestCase(unittest.TestCase):
    def test_truediv(self):
        self.assertEqual(str(a / b), "m/s")
        self.assertEqual(str(a / a), "")
        self.assertEqual(str(c / a), "m")
        self.assertEqual(str(f / f), "")
        self.assertEqual(str(c / a), "m")
        self.assertEqual(str(d / a), "s")
        self.assertEqual(e / f, Unit("kg;s^2", "N"))

    def test_mul(self):
        self.assertEqual((d * a == e * a), True)
        self.assertEqual((d * a == e), False)

    def test_eq(self):
        self.assertEqual((d == e), True)
        self.assertEqual((a == a), True)
        self.assertEqual((a == b), False)
        self.assertEqual((c == a * a), True)

    def test_str(self):
        self.assertEqual(str(Unit("m^2", "m")), "m")
        self.assertEqual(str(a), "m")
        self.assertEqual(str(c), "m^2")

    def test_pow(self):
        self.assertEqual(str(a**0), "")
        self.assertEqual(str(f**0), "")
        self.assertEqual(str(f**2), "(N^2*m^2)/(kg^2*s^2)")
        self.assertEqual(str(g**2), "")
    
    def test_ease(self):
        """Methode muss nicht seperat getestet werden, da sie an allen anderen Funktionen beteiligt ist"""
        pass
    
    def test_flip(self):
        self.assertEqual(str(a.flip()), "1/m")
        self.assertEqual(str(b.flip()), "1/s")
        self.assertEqual(str(c.flip()), "1/m^2")
        self.assertEqual(str(d.flip()), "1/(m*s)")
        self.assertEqual(str(e.flip()), "1/(s*m)")

        self.assertEqual(str(f.flip()), "(kg*s)/(N*m)")
        self.assertEqual(str(g.flip()), "")


if __name__ == '__main__':
    unittest.main()
