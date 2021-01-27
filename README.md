# Pyrror
Package for uncertainty analysis in Python.
It was developed while I was doing my Bachelor in physics.
The functionality is based on the practical courses.

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


## Usage
if sign is a string:
         there are different rules for more complex dimensions. They are also described in the Unit class only "/" not:
            #. powered dimensions have the form of  sign = dimension_syombol '^' power. *Attention: power >= 0*!
               Example: Area = m^2
            #. mixed dimensions are separated by ';'.
               Example: torque: = N;m
            #. fractions are created by a '/'. *There can only apper one '/' in each sign*. If a dimension appears left
               to an '/' it is count to the numerator. If it appears to the right its part of the denominator.
               Example: speed: m/s or acceleration: m/s^2

            **sign-EBNF:**
            S := '"' units '"' | '"' units '/' units '"'
            units := unit | unit ';' units
            unit := string | string '^' integer


## Documentation
### controls.py

#### instancemethod
Controls if an instance of a class is modified during a method.\
Raises an `AttributeError` if the instance is changed.\
Usage as a decorator:
```
class Dummy:

   @instancemethod
   def fuzz(self, a):
      return Dummy(...)
```

#### type_check
Controls for a given sequence of tuples if each variable has a specific type.\
Raises an `TypeError` if the type is incorrect.\
`type_check(*args) -> True`

Usage:
```
>>> type_check((3, int), (1.2, float))
True
>>> type_check([("3", int)])
TypeError: Type of '<class 'str'>' is false! Try <class 'int'> instead
```

#### list_type_check
Controls if each element of a given list as a given type.\
`list_type_check(lst, data_type) -> bool`
- `lst`: `List[object]` = list of objects which should have the same type `data_type`
- `data_type`: `type` = specific type

Returns `True` if all `objects` in `lst` have the type `data_type` otherwise returns `False`.
Usage:
```
>>> list_type_check([2, 3, 1], int)
True
>>> list_type_check([2, "3", 1], int)
False
```

### unit.py
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

Overview of different methods implemented for the class

| method | args | description |
|--------|------|-------------|
| `flip` |      | inverts the unit which means an exchange of numerator and denominator


Overview of different implemented operations with different types

| types | + | - | *    | /    | \> | < | ==   | <= | >= |
|-------|---|---|------|------|----|---|------|----|----|
|`Unit` |   |   |`Unit`|`Unit`|    |   |`bool`|    |    |


Legend:
- ` ` = not defined
- `<type>` = returns object of type `<type>`

Usage:
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

### unit_helper.py
Assistance functionallity for working with units.

#### unit_control
Controls if the given argument `other` carries the same unit as `self`.\
Raises an `TypeError` if `other` does not carry any unit.\
Raises an `ValueError` if `other` does not carry the same unit.

Usage as a decorator:
```
class Dummy:

   @unit_control
   def __add__(self, other):
      pass
```

#### has_unit
Returns if the given variable has a `unit` attribute.\
`has_unit(variable) -> bool`
- `variable` = object to check 

Usage:
```
>>> has_unit(3)
False
```

### data.py
Provides the `Data`-class and the `Const`-class.

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

Overview of different implemented operations with different types

| types | +    | -    | *    | /    |  **  | \>   | <    | ==   | <=   | >=   |
|-------|------|------|------|------|------|------|------|------|------|------|
|`Data` |`Data`|`Data`|`Data`|`Data`|      |`bool`|`bool`|`bool`|`bool`|`bool`|
|`Const`|`Data`|`Data`|`Data`|`Data`|      |`bool`|`bool`|`bool`|`bool`|`bool`|
|`int`  |`Data`|`Data`|`Data`|`Data`|`Data`|`bool`|`bool`|`bool`|`bool`|`bool`|
|`float`|`Data`|`Data`|`Data`|`Data`|`Data`|`bool`|`bool`|`bool`|`bool`|`bool`|


Legend:
- ` ` = not defined
- `<type>` = returns object of type `<type>`

Usage:
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

Overview of different implemented operations with different types

| types | +     | -     | *     | /     |  **   | \>   | <    | ==   | <=   | >=   |
|-------|-------|-------|-------|-------|-------|------|------|------|------|------|
|`Data` |`Data` |`Data` |`Data` |`Data` |       |`bool`|`bool`|`bool`|`bool`|`bool`|
|`Const`|`Const`|`Const`|`Const`|`Const`|       |`bool`|`bool`|`bool`|`bool`|`bool`|
|`int`  |`float`|`float`|`Const`|`Const`|`Const`|`bool`|`bool`|`bool`|`bool`|`bool`|
|`float`|`float`|`float`|`Const`|`Const`|`Const`|`bool`|`bool`|`bool`|`bool`|`bool`|

Legend:
- ` ` = not defined
- `<type>` = returns object of type `<type>`

The addition and subtraction with ints, floats is only possible if the `Const` has a `Unit` equal to `Unit()`

Usage:
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