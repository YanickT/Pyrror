from data import Const


# convert units (pre-factors)
KM2M = Const(1000, "m/km")
M2KM = 1 / KM2M
M2CM = Const(100, "cm/m")
CM2M = 1 / M2CM
M2MM = Const(1000, "mm/m")
MM2M = 1 / M2MM

T2KG = Const(1000, "kg/t")
KG2T = 1 / T2KG
KG2G = Const(1000, "g/kg")
G2KG = 1 / KG2G
G2MG = Const(1000, "mg/g")
MG2G = 1 / G2MG

A2D = Const(365, "d/a")
D2A = 1 / A2D
D2H = Const(24, "h/d")
H2D = 1 / D2H
H2MIN = Const(60, "min/h")
MIN2H = 1 / H2MIN
MIN2S = Const(60, "s/min")
S2MIN = 1 / MIN2S

A2MA = Const(1000, "mA/A")
MA2A = 1 / A2MA


# convert units
J2SI = Const(1, "kg*m^2/s^2")


# natural constants
C = Const(2.99792458e8, "m/s")
H = Const(6.62607015e-34, "J/s")
N = Const(6.02214076e23, "1/mol")
