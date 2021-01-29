from logik.formula import Formula
from logik.data import Data

f = Formula("acos((2*x-1) / sin(y))")
print(f)
print(f.latex({"x": Data, "y": Data}))
print(f.show_error({"x": Data, "y": Data}))