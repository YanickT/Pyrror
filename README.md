# Pyrror
Package for uncertainty analysis in Python.
It was developed while I was doing my Bachelor in physics.
The functionality is based on the practical courses.


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

## Warnings
The function exec is used within some functionalities.
This can cause harm if exploited.

# Currently in progress

(for the update to python 3.9 and better (newer constructs) code)
TODO: 
table.py
Improve Formula unit

# TODO:
README
make to python package

Tests for chi_2
Tests for regression
Improve Tests
Blatt mit Konts und umrechnungen

# FIXME:
Covariant Matrix has problem with error (comparison with presentaion result shows a missing 2* in the total error)

Data should format in such a way, that the mean value is given by 1,...
not the error