# Pyrror
Package for uncertainty analysis in Python.
It was developed while I was doing my Bachelor in physics.
The functionality is based on the lab courses.

## Warnings
The function exec is used within some functionalities.
This can cause harm if exploited.

## General introduction
The main classes of the package are `Data`, `Table` and `Formula`.
The package holds functionality for:

- Error/Uncertainty propagation in equations
- Create tables and calculate different types of averages including arithmetic, geometric, modus, ...
- Normal and simplified gauss propagation of uncertainties
- Regressions including covariant matrices as well as automated chi2 test and residuum plot
- Propagation of units within equations

The `Data`-class holds a mean value and an error.
Furthermore, can a `Data` carry a `Unit`.
The basic arithmetic methods including `*, /, +, -` are implemented.
Using these the error is propagated using simplified gauss.
For a normal propagation use a `Formula`.
For natural and other constants the `Const`-class can be used. 
A `Const` also carries a `Unit` but not an uncertainty.


## Documentation
### controls.py

---

#### instancemethod
Controls if an instance of a class is modified during a method.\
Raises an `AttributeError` if the instance is changed.\
**USAGE AS DECORATOR:**
```
class Dummy:

   @instancemethod
   def fuzz(self, a):
      return Dummy(...)
```

---

#### type_check
Controls for a given sequence of tuples if each variable has a specific type.\
Raises an `TypeError` if the type is incorrect.\
`type_check(*args) -> True`

**USAGE:**
```
>>> type_check((3, int), (1.2, float))
True
>>> type_check([("3", int)])
TypeError: Type of '<class 'str'>' is false! Try <class 'int'> instead
```

---

#### list_type_check
Controls if each element of a given list as a given type.\
`list_type_check(lst, data_type) -> bool`
- `lst`: `List[object]` = list of objects which should have the same type `data_type`
- `data_type`: `type` = specific type

Returns `True` if all `objects` in `lst` have the type `data_type` otherwise returns `False`.\
**USAGE:**
```
>>> list_type_check([2, 3, 1], int)
True
>>> list_type_check([2, "3", 1], int)
False
```

---
---

### unit.py

---

#### Unit-class
Represents a unit like 'm' for meter.\
``Unit(numerator="", denominator="")``
- `numerator` = `str` represents the upper units in a fraction
- `denominator` = `str` represents the lower units a fraction

For each `numerator` and `denominator` can a sequence of units be defined as specified by the following sign-EBNF:
```
S := '"' units '"'
units := unit | unit ';' units
unit := string | string '^' integer
```

**METHODS:**
-  `flip()`:\
    inverts the unit which means an exchange of numerator and denominator
      

**SPECIAL OPERATIONS:**

| types | + | - | *    | /    | \> | < | ==   | <= | >= |
|-------|---|---|------|------|----|---|------|----|----|
|`Unit` |   |   |`Unit`|`Unit`|    |   |`bool`|    |    |

**USAGE:**
```
>>> a = Unit("m", "s")
>>> a
m/s
>>> b = Unit("J;s", "m")
>>> b
(J*s)/m
>>> c = a * b
>>> c
J
```

---
---

### unit_helper.py
Assistance functionality for working with units.

---

#### unit_control
Controls if the given argument `other` carries the same unit as `self`.\
Raises an `TypeError` if `other` does not carry any unit.\
Raises an `ValueError` if `other` does not carry the same unit.

**USAGE AS DECORATOR:**
```
class Dummy:

   @unit_control
   def __add__(self, other):
      pass
```

---

#### has_unit
Returns if the given variable has a `unit` attribute.\
`has_unit(variable) -> bool`
- `variable` = object to check 

**USAGE:**
```
>>> has_unit(3)
False
```

---
---

### data.py
Provides the `Data`-class and the `Const`-class.

---

#### Data-class
Represents a real measurement with an uncertainty.\
`Data(value: str, error: str, sign: Union[str, Unit] = "", power: int = 0, n: int = 0)`
- `value` = string of the mean value
- `error` = string of the uncertainty
- `sign` = either string or `Unit`. Since only one string is given the usage differs a bit from the one in `Unit`. 
  The extended sign-EBNF reads:
  ```
  S := '"' units '"' | '"' units '/' units '"'
  units := unit | unit ';' units
  unit := string | string '^' integer
  ```
  The string will be split at '/' into `numerator` and `denominator`.
- `power` = additional factor to compensate pre-factors (eg. km -> 10^3 m -> power = 3). 
  It is advantageous to work with SI-units only and use `power` instead of kilo, milli, ...
- `n` = number of significant digits. Has to be greater than 0. If 0 (or not set seperatly), the number of digits
  will be determined from the length of `error`

**SPECIAL OPERATIONS:**

| types | +    | -    | *    | /    |  **  | \>   | <    | ==   | <=   | >=   |
|-------|------|------|------|------|------|------|------|------|------|------|
|`Data` |`Data`|`Data`|`Data`|`Data`|      |`bool`|`bool`|`bool`|`bool`|`bool`|
|`Const`|`Data`|`Data`|`Data`|`Data`|      |`bool`|`bool`|`bool`|`bool`|`bool`|
|`int`  |`Data`|`Data`|`Data`|`Data`|`Data`|`bool`|`bool`|`bool`|`bool`|`bool`|
|`float`|`Data`|`Data`|`Data`|`Data`|`Data`|`bool`|`bool`|`bool`|`bool`|`bool`|


**USAGE:**
```
>>> a = Data("123.456", "1.234", power=-2, sign="m/s")
>>> a
(123.456±1.234)*10^-2 m/s
>>> b = Data("4", "1.00000001", sign="s", n=2)
>>> b
(4.0±1.0) s
>>> c = a * b
>>> c
(4.9±1.2) m
```

---

#### Const-class
Represents a natural constant (through SI definition some may have no error, eg. the speed of light), or a measurement with neglected uncertainty.\
`Const(value: Union[int, float], sign: Union[str, Unit])`
- `value` = value of the constant
- `sign` = either string or `Unit`. Since only one string is given the usage differs a bit from the one in `Unit`. 
  The extended sign-EBNF reads:
  ```
  S := '"' units '"' | '"' units '/' units '"'
  units := unit | unit ';' units
  unit := string | string '^' integer
  ```
  The string will be split at '/' into `numerator` and `denominator`.

**SPECIAL OPERATIONS:**

| types | +     | -     | *     | /     |  **   | \>   | <    | ==   | <=   | >=   |
|-------|-------|-------|-------|-------|-------|------|------|------|------|------|
|`Data` |`Data` |`Data` |`Data` |`Data` |       |`bool`|`bool`|`bool`|`bool`|`bool`|
|`Const`|`Const`|`Const`|`Const`|`Const`|       |`bool`|`bool`|`bool`|`bool`|`bool`|
|`int`  |`float`|`float`|`Const`|`Const`|`Const`|`bool`|`bool`|`bool`|`bool`|`bool`|
|`float`|`float`|`float`|`Const`|`Const`|`Const`|`bool`|`bool`|`bool`|`bool`|`bool`|


The addition and subtraction with ints, floats is only possible if the `Const` has a `Unit` equal to `Unit()`

**USAGE:**
```
>>> a = Const(1, "m")
>>> a
1.0 m
>>> a + 1
ArithmeticError: Addition of values with different units is not possible
>>> b = Const(1, "")
>>> b
1.0
>>> b + 1
2.0
>>> type(b + 1)
<class 'float'>
```

---
---

### data_helper.py
Assistance functionality for working with Data.

---

#### digits
Returns the number of significant digits from a given error.\
`digits(error: Union[str, int, float]) -> int`
- `error` = the error the significant digits should be determined for

The result is the number of significant digits.\
**USAGE:**
```
>>> digits(1.23)
3
>>> digits("0.0012")
2
>>> digits(99.25)
4
```

---

#### round_data
Shortens the `value` and `error` of a `Data` to its length `Data.n`. Furthermore, it calculates which power should be used in the representation.\
`round_data(data: Data)`
- `data` = a instance of type `Data` to round values to correct length

Usage:\
It is used inside `Data` automatically. There should not be any need to use this.

---
---

### formula.py

---

#### Formula
Used for more complex functions and connections of uncertain data as well as a better
uncertainty analysis.\
`Formula(formula_string: str)`
- `formula_string` = `str` the given formula. This can be any valid `sympy` expression.


**METHODS:**
-  `latex(type_dict: Dict[str: type]) -> str`
    - `type_dict` = Dictionary specifying which type each variable in the `Formula` has\
    Returns a string of Latex-code of the given `Formula`
      

- `show_error(type_dict: Dict[str: type]) -> str`
    - `type_dict` = Dictionary specifying which type each variable in the `Formula` has\
    Returns a string of the propagation formula for the uncertainty
      

- `calc_unit(value_dict: Dict[Data, Const, float, int]) -> Unit`
    - `value_dict` = Dictionary assign a python object to each variable in the `Formula`\
    Returns a `Unit` for the result. If the `Unit` could not be determined shows a `warning`
      

- `calc(value_dict: Dict[Data, Const, float, int]) -> Unit`
    - `value_dict` = Dictionary assign a python object to each variable in the `Formula`\
    Returns the result of the calculation. If the `Unit` could not be determined shows a `warning`

**USAGE:**
```
>>> f = Formula("x**2 + exp(y)")
>>> f.latex({'x': Data, 'y': Data})
('x^{2} + e^{y}', '\sqrt{4 \left(__delta^{x}\right)^{2} x^{2} + \left(__delta^{y}\right)^{2} e^{2 y}}')
>>> a = Data("2.12", "0.05")
>>> b = Data("1.23", "0.02")
>>> f.calc({'x': a, 'y': b})
(79±2)*10^-1
>>> 
>>> f2 = Formula("x**2 + 2 * y")
>>> x = Data("1.3", "0.3", sign="m")
>>> y = Data("0.1", "0.22", sign="m^2")
>>> f2.calc({'x': x, 'y': y})
(19±9)*10^-1 m^2
```

---
---

### regression.py
Holds classes for different types of regressions. 
For implementing new Regressions an abstract base class `Regression` is given.

---

### chi_2.py

### table.py

## Currently in progress

(for the update to python 3.9 and better (newer constructs) code)
TODO: 
table.py
Improve Formula unit


## TODO:

- README
- make to python package
- Tests for chi_2
- Tests for regression
- Improve Tests
- script with natural constants and factors for changing a unit

## FIXME:
- Covariant Matrix has problem with error (comparison with presentaion result shows a missing 2* in the total error)
- Data should format in such a way, that the mean value is given by 1,...
not the error