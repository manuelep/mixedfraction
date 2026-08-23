# Task: Implement a pedagogical MixedFraction Python library

This is a request to implement a real, reusable, installable Python library, not a single Python script or a standalone educational example.

The primary goal of the library is educational: it should illustrate the relationship between mathematical representations of fractions and their computational representation, while following idiomatic Python practices.

The library should NOT attempt to replace Python's standard-library `fractions.Fraction`. Instead, it should provide a pedagogical mixed-fraction representation built on top of `fractions.Fraction` for exact arithmetic.

---

# 1. Core design principles

The class must explicitly distinguish between:

1. The **user-facing representation** of a mixed fraction.
2. The **mathematical value** represented by that fraction.
3. The **computational representation** used to perform exact arithmetic.

The class must preserve the original mixed-fraction representation supplied to the constructor.

Python's standard-library `fractions.Fraction` must be used as the computational engine for rational arithmetic.

Do NOT reimplement rational arithmetic using floating-point numbers.

Do NOT immediately convert the constructor arguments into a normalized `Fraction` and discard the original representation.

For example:

```python
f = MixedFraction(1, 6, 8)
```

must retain the original components:

```python
f.whole == 1
f.numerator == 6
f.denominator == 8
```

and:

```python
str(f) == "1 6/8"
```

even though the mathematical value is `7/4`.

The distinction between representation and mathematical value is a fundamental feature of the project.

---

# 2. Constructor and input constraints

The primary constructor must have the following conceptual signature:

```python
MixedFraction(whole=0, numerator=None, denominator=1)
```

where:

- `whole` defaults to `0`;
- `numerator` is REQUIRED;
- `denominator` defaults to `1`.

The constructor must enforce these constraints:

```text
whole >= 0
numerator >= 0
denominator > 0
```

All three values must be integers.

Therefore:

```python
MixedFraction(whole=1, numerator=3, denominator=4)
```

is valid.

The following must be rejected:

```python
MixedFraction(whole=-1, numerator=3, denominator=4)
MixedFraction(whole=1, numerator=-3, denominator=4)
MixedFraction(whole=1, numerator=3, denominator=0)
MixedFraction(whole=1, numerator=3, denominator=-4)
```

The implementation should use appropriate exceptions, preferably `TypeError` for invalid types and `ValueError` for invalid numeric values.

The constructor must NOT silently convert floats, strings, or other non-integer values into integers.

For example, this should not silently truncate:

```python
MixedFraction(1.5, 3, 4)
```

---

# 3. Proper fractional component

Because the class represents a mixed fraction, the fractional component should be a proper fraction.

Therefore the constructor must enforce:

```text
0 <= numerator < denominator
```

This means:

```python
MixedFraction(whole=1, numerator=3, denominator=4)
```

is valid.

But:

```python
MixedFraction(whole=1, numerator=5, denominator=4)
```

must be rejected.

The constructor must NOT automatically transform:

```text
1 5/4
```

into:

```text
2 1/4
```

because preserving the user's input representation is a core design principle.

Conversion from an improper `Fraction` into a canonical mixed fraction should instead be handled explicitly through a conversion method or class method.

Document this distinction clearly.

---

# 4. Representation must be preserved

The three constructor components must remain available as public, read-only attributes or properties:

```python
f.whole
f.numerator
f.denominator
```

For:

```python
f = MixedFraction(1, 6, 8)
```

the object must preserve:

```python
f.whole == 1
f.numerator == 6
f.denominator == 8
```

even though the fractional component is reducible.

Do NOT automatically reduce:

```text
6/8
```

to:

```text
3/4
```

during construction.

Likewise, do not automatically convert a representation into another equivalent representation unless explicitly requested by the user.

This means that:

```python
MixedFraction(1, 6, 8)
```

and:

```python
MixedFraction(1, 3, 4)
```

represent the same mathematical value but retain different structural representations.

---

# 5. Mathematical value

Provide a method such as:

```python
as_fraction()
```

that returns the exact mathematical value as a standard-library `fractions.Fraction`.

For example:

```python
f = MixedFraction(1, 3, 4)

f.as_fraction()
```

must return:

```python
Fraction(7, 4)
```

The conversion should be conceptually:

```python
Fraction(
    whole * denominator + numerator,
    denominator
)
```

The returned `Fraction` is allowed and expected to be normalized by Python.

Calling `as_fraction()` must NOT modify the original `MixedFraction`.

For example:

```python
f = MixedFraction(1, 6, 8)

f.as_fraction()
# Fraction(7, 4)

str(f)
# "1 6/8"
```

---

# 6. Simplification

Simplification must be an explicit operation.

Construction must not automatically simplify the fractional part.

Provide:

```python
simplified()
```

which returns a new `MixedFraction` containing a simplified representation.

For example:

```python
f = MixedFraction(1, 6, 8)

str(f)
# "1 6/8"

g = f.simplified()

str(g)
# "1 3/4"
```

The original object must remain unchanged:

```python
str(f)
# "1 6/8"
```

The method should return a new object rather than mutating the original.

If an in-place operation such as `simplify()` is also provided, its semantics must be clearly documented. Do not provide both methods merely for completeness; prefer the simplest and most Pythonic API.

Simplification must correctly handle cases such as:

```text
1 6/8  -> 1 3/4
2 4/8  -> 2 1/2
3 0/5  -> 3
```

The implementation may use `Fraction` or `math.gcd` for simplification.

---

# 7. Improper fraction representation

Provide a way to obtain the improper rational representation.

For example:

```python
f = MixedFraction(1, 3, 4)

f.as_fraction()
# Fraction(7, 4)
```

If useful, also provide a clearly named method or property exposing the improper numerator and denominator without necessarily creating a `Fraction`.

For example:

```python
f.improper_numerator
# 7

f.improper_denominator
# 4
```

This is optional if `as_fraction()` already provides a sufficiently clear API.

---

# 8. Construction from Fraction

Provide a class method:

```python
MixedFraction.from_fraction(...)
```

which constructs a mixed fraction from a standard-library `Fraction`.

For example:

```python
MixedFraction.from_fraction(Fraction(7, 4))
```

should return a `MixedFraction` representing:

```text
1 3/4
```

Since a `Fraction` does not contain information about the original mixed representation, this conversion should produce a canonical mixed representation.

For example:

```python
Fraction(14, 8)
```

may produce:

```text
1 3/4
```

rather than preserving the original `14/8`, because that original representation is unavailable.

The behavior for negative `Fraction` values must be explicitly defined and tested.

---

# 9. Negative values

The constructor must NOT accept negative values in any of the three components.

Do NOT introduce a constructor argument such as:

```python
positive=True
```

or:

```python
negative=False
```

Instead, negative values must be created using Python's unary minus operator.

Implement:

```python
__neg__()
```

so that:

```python
f = MixedFraction(1, 3, 4)

-f
```

represents:

```text
-1 3/4
```

The sign should be treated as a property of the mathematical value rather than as part of the three primary constructor components.

The implementation may internally store sign information, but it must not be exposed as a fourth constructor component.

The original absolute mixed-fraction components should remain conceptually intact.

For example, negating:

```python
MixedFraction(1, 3, 4)
```

should produce a value whose absolute mixed representation is still:

```text
1 3/4
```

with a negative sign applied to the complete value.

Also implement unary plus if appropriate:

```python
__pos__()
```

so that:

```python
+f
```

behaves consistently with Python numeric types.

Implement:

```python
__abs__()
```

where appropriate.

Double negation must work:

```python
-(-f) == f
```

---

# 10. Zero

Define zero explicitly and consistently.

A valid representation should allow:

```python
MixedFraction(whole=0, numerator=0, denominator=1)
```

to represent zero.

The implementation must define how zero is displayed and how its sign behaves.

Negative zero must not be treated as a distinct mathematical value.

For example, negating zero should still represent zero.

Document the chosen behavior.

---

# 11. Arithmetic

Implement the standard arithmetic operators relevant to rational numbers:

```text
+
-
*
/
**
```

through the appropriate Python special methods:

```python
__add__
__sub__
__mul__
__truediv__
__pow__
```

Arithmetic MUST be performed using `fractions.Fraction`.

Do not implement the arithmetic using floats.

For example:

```python
a = MixedFraction(1, 3, 4)
b = MixedFraction(2, 1, 3)

a + b
```

should produce a mathematically correct `MixedFraction` representing:

```text
4 1/12
```

The intermediate calculation should conceptually be:

```python
Fraction(7, 4) + Fraction(7, 3)
```

The resulting `Fraction` should then be converted back into a `MixedFraction`.

---

# 12. Arithmetic result representation

When an arithmetic operation produces a `MixedFraction`, the result should be represented canonically.

This is different from construction.

For example:

```python
a = MixedFraction(1, 3, 4)
b = MixedFraction(2, 1, 3)

a + b
```

may return:

```text
4 1/12
```

rather than preserving unreduced intermediate representations.

The key distinction is:

```text
Construction:
    preserve the supplied representation.

Arithmetic:
    calculate using Fraction,
    then create an appropriate canonical MixedFraction.
```

This distinction must be documented.

Arithmetic results may therefore be simplified even though constructor input is not automatically simplified.

---

# 13. Negative arithmetic results

Arithmetic operations must support negative results.

For example:

```python
a = MixedFraction(1, 3, 4)
b = MixedFraction(2, 1, 3)

a - b
```

must correctly represent:

```text
-7/12
```

The implementation must not attempt to encode a negative value by putting a negative sign into `whole`, `numerator`, or `denominator`.

Instead, the sign must be represented at the value level, consistent with the `__neg__()` design.

Likewise:

```python
a - a
```

must produce zero.

---

# 14. Reflected arithmetic operators

Where appropriate, implement reflected arithmetic operators such as:

```python
__radd__
__rsub__
__rmul__
__rtruediv__
```

so that expressions involving integers and `Fraction` objects can behave naturally.

For example, where mathematically appropriate:

```python
2 + f
2 * f
Fraction(1, 2) + f
```

should work.

Use Python's `NotImplemented` protocol correctly for unsupported operand types.

Do not add arbitrary implicit conversions that could hide errors.

---

# 15. Powers

Implement `__pow__()`.

At minimum, support integer exponents.

Use `Fraction` for the actual calculation.

Test:

```text
f ** 0
f ** 1
f ** 2
f ** -1
```

where mathematically meaningful.

Clearly define behavior for invalid cases.

---

# 16. Division and zero

Division by zero must raise:

```python
ZeroDivisionError
```

Test both:

```python
f / 0
```

and division by a `MixedFraction` whose value is zero.

---

# 17. Comparison operators

Implement exact comparisons based on mathematical value:

```text
==
!=
<
<=
>
>=
```

using:

```python
__eq__
__ne__
__lt__
__le__
__gt__
__ge__
```

Comparisons must NOT be based on the stored representation.

Therefore:

```python
MixedFraction(1, 2, 4) == MixedFraction(1, 1, 2)
```

must be:

```python
True
```

even though the representations differ.

Similarly, all ordering comparisons must be evaluated according to mathematical value.

Comparisons should use exact `Fraction` values.

---

# 18. Hashing

Consider whether the class should be hashable.

If equality is based on mathematical value, any implementation of `__hash__()` must respect:

```text
a == b  => hash(a) == hash(b)
```

For example:

```python
MixedFraction(1, 2, 4)
```

and:

```python
MixedFraction(1, 1, 2)
```

are mathematically equal and therefore must have identical hashes if the class is hashable.

If the class is mutable, it should probably not be hashable.

Prefer immutability if this simplifies the design and makes the numeric semantics cleaner, but do not introduce unnecessary complexity.

---

# 19. String representation

Implement both:

```python
__str__()
__repr__()
```

`__str__()` must provide a human-readable mixed-fraction representation.

Examples:

```python
str(MixedFraction(1, 3, 4))
# "1 3/4"

str(MixedFraction(0, 3, 4))
# "3/4"

str(MixedFraction(2, 0, 1))
# "2"
```

For negative values:

```python
str(-MixedFraction(1, 3, 4))
# "-1 3/4"
```

Avoid displaying unnecessary components such as `0 3/4` or `2 0/1`.

`__repr__()` should provide an unambiguous Python-oriented representation that preserves the constructor representation.

For example:

```python
repr(MixedFraction(1, 6, 8))
# "MixedFraction(1, 6, 8)"
```

Ideally:

```python
eval(repr(f)) == f
```

should be true where safe and appropriate.

The `repr()` should not silently replace the original representation with its simplified equivalent.

---

# 20. String parsing

Consider supporting construction from strings such as:

```text
"1 3/4"
"3/4"
"2"
"-1 3/4"
```

through a dedicated class method such as:

```python
MixedFraction.from_string(...)
```

rather than overloading the constructor with too many input forms, unless there is a compelling reason otherwise.

Parsing should be strict and well documented.

The parser should reject malformed or ambiguous input.

Examples of invalid input should be covered by tests.

All parsing logic, identifiers, comments, documentation, and error messages must use English.

---

# 21. Numeric conversions

Consider implementing:

```python
__int__()
__float__()
```

where their semantics are mathematically well-defined.

`__float__()` should explicitly document that conversion to floating point is approximate.

Do not use floating-point values for internal calculations.

Consider whether `__int__()` should truncate toward zero, following Python's numeric conventions.

---

# 22. Immutability and representation integrity

Strongly consider making `MixedFraction` immutable or otherwise ensuring that its internal state cannot become inconsistent.

If the class exposes:

```python
whole
numerator
denominator
```

they should preferably be read-only properties.

The object must always satisfy its documented invariants.

Do not allow external mutation to create invalid states such as:

```text
denominator <= 0
numerator < 0
whole < 0
numerator >= denominator
```

unless the API explicitly provides a validated way to construct such a state.

---

# 23. Type handling

Use Python type hints throughout the public API.

The implementation should clearly define supported operand types, especially:

- `MixedFraction`
- `fractions.Fraction`
- `int`

Support for `float` should be considered carefully.

Do not silently convert floating-point values into exact rational values unless the behavior is explicitly documented.

Use `NotImplemented` where appropriate for unsupported operand types.

---

# 24. Standard Python package

The project MUST be implemented as a proper, installable Python package following modern standard Python packaging practices.

Use the `src/` layout:

```text
project-root/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── mixedfraction/
│       ├── __init__.py
│       └── mixed_fraction.py
├── tests/
│   ├── __init__.py
│   └── test_mixed_fraction.py
└── ...
```

The exact package/module names may be adjusted if a better naming convention is justified, but the project must follow the standard `src/` package layout.

The package must be installable using standard Python tooling, for example:

```bash
pip install .
```

and, for development:

```bash
pip install -e .
```

The package metadata and build configuration MUST be declared in `pyproject.toml`.

Prefer a modern PEP 621-compatible `pyproject.toml` configuration.

Do NOT require:

- `setup.py`;
- `setup.cfg`;
- custom installation scripts;
- Makefiles;
- shell scripts;
- external package managers;
- non-standard build systems;

unless there is a clear technical reason to use them.

The library itself must have no third-party runtime dependencies.

Its runtime dependencies should be limited to Python's standard library, in particular:

```python
from fractions import Fraction
```

If a third-party tool is useful for development or testing, keep it as an optional development dependency and do not make it a runtime requirement.

---

# 25. Supported Python versions

Declare a clear minimum supported Python version in `pyproject.toml`.

Use modern Python syntax and type hints consistently with that minimum version.

Do not introduce compatibility code for obsolete Python versions unless explicitly required.

---

# 26. Package API

The public API should be deliberately exposed through the package's `__init__.py`.

For example:

```python
from mixedfraction import MixedFraction
```

should be sufficient for normal use.

Users should not need to import the class from an internal module such as:

```python
from mixedfraction.mixed_fraction import MixedFraction
```

unless they explicitly want to access implementation details.

Keep the public API small and intentional.

If additional public types, exceptions, or utilities are introduced, expose them explicitly through the package namespace and document them.

Avoid exposing internal implementation details unnecessarily.

---

# 27. Import behavior

The following should work after installation:

```python
from mixedfraction import MixedFraction
```

For example:

```python
from mixedfraction import MixedFraction

fraction = MixedFraction(1, 3, 4)

print(fraction)
# 1 3/4
```

The package should not execute unexpected code, print output, or perform side effects when imported.

---

# 28. Development and testing

The project must support running the complete test suite using standard Python tooling.

At minimum, this should work from the project root:

```bash
python -m unittest discover
```

If a different standard test discovery configuration is used, document it clearly.

Tests must remain separate from the package source code.

The package must be testable both:

1. directly from a development checkout;
2. after installation with `pip`.

---

# 29. Build and installation validation

Before considering the task complete, verify the complete packaging workflow.

If the standard `build` development tool is available, run:

```bash
python -m build
```

Then verify that the generated distribution can be installed into a clean environment.

At minimum, verify:

```bash
pip install .
```

and:

```python
from mixedfraction import MixedFraction
```

work correctly.

Do not make `build` a runtime dependency.

If the build tool is not available in the environment, explicitly report that limitation rather than silently skipping the packaging validation.

---

# 30. Package metadata

The `pyproject.toml` should contain appropriate metadata, including at least:

- package name;
- version;
- description;
- readme;
- Python requirement;
- license information;
- author/maintainer information where appropriate;
- project dependencies;
- optional development dependencies if needed.

Do not invent personal author information.

If author information has not been provided, use a neutral placeholder or leave it configurable rather than fabricating an identity.

---

# 31. No unnecessary dependencies

The runtime package must depend only on Python's standard library.

In particular, rational arithmetic must use:

```python
from fractions import Fraction
```

and not external packages such as:

- `sympy`;
- `numpy`;
- third-party fraction libraries.

The purpose of using `Fraction` is specifically to demonstrate that the custom `MixedFraction` representation can be built on top of Python's existing exact rational-number implementation.

---

# 32. Packaging quality

The package should be suitable for publication as a normal Python library.

Avoid putting executable examples, exploratory notebooks, temporary files, generated artifacts, or development-only files inside the runtime package.

Include an appropriate `.gitignore` and, if useful, package-development configuration.

Do not commit generated directories such as:

```text
__pycache__/
*.pyc
build/
dist/
*.egg-info/
```

unless there is a specific reason.

The final project should be clean enough that it could later be published to PyPI without requiring a restructuring of the package.

---

# 33. Unit tests

A comprehensive unit-test suite is an explicit requirement of this task.

Use Python's standard `unittest` framework unless there is a strong technical reason to use another framework.

All test names, test descriptions, variables, comments, and assertions should use English.

Tests must cover at least the following.

## Constructor

Test:

- `whole` defaulting to `0`;
- `numerator` being required;
- `denominator` defaulting to `1`;
- valid positive values;
- `whole == 0`;
- `numerator == 0`;
- `denominator == 1`;
- invalid negative `whole`;
- invalid negative `numerator`;
- zero denominator;
- negative denominator;
- non-integer arguments;
- `numerator >= denominator`.

## Representation preservation

Verify that:

```python
f = MixedFraction(1, 6, 8)
```

preserves:

```python
f.whole == 1
f.numerator == 6
f.denominator == 8
```

and does NOT automatically simplify to `1 3/4`.

Test that two mathematically equivalent representations remain structurally distinct while comparing equal.

## Conversion to Fraction

Test:

```text
1 3/4 -> Fraction(7, 4)
1 6/8 -> Fraction(7, 4)
0 3/4 -> Fraction(3, 4)
```

and negative values.

## Simplification

Test:

```text
1 6/8 -> 1 3/4
2 4/8 -> 2 1/2
3 0/5 -> 3
```

and verify that the original object remains unchanged.

## Sign

Test:

```python
-f
-(-f)
abs(f)
```

including:

- positive values;
- zero;
- fractions;
- mixed fractions;
- negative arithmetic results.

## Arithmetic

Thoroughly test:

```text
+
-
*
/
**
```

including:

- positive results;
- negative results;
- zero;
- integers;
- proper fractions;
- mixed fractions;
- reducible results;
- large values.

## Comparisons

Test mathematically equivalent representations:

```python
MixedFraction(1, 2, 4) == MixedFraction(1, 1, 2)
```

and all comparison operators.

## Edge cases

Include:

- denominator `1`;
- numerator `0`;
- very large integers;
- exact cancellation;
- negative results;
- division by zero;
- zero powers;
- negative powers;
- values crossing zero.

The tests should validate mathematical behavior rather than merely implementation details.

---

# 34. Documentation

Provide a concise but clear README explaining:

1. What `MixedFraction` represents.
2. Why it exists even though Python already provides `fractions.Fraction`.
3. The distinction between representation and mathematical value.
4. Why the constructor preserves the original `(whole, numerator, denominator)` representation.
5. The constructor constraints:
   - `whole >= 0`, default `0`;
   - `numerator >= 0`, required;
   - `denominator > 0`, default `1`;
   - `numerator < denominator`.
6. Why construction does not automatically simplify.
7. Why arithmetic uses `Fraction`.
8. How negative values are created using unary `-`.
9. How explicit simplification works.
10. How equivalent representations compare equal.
11. Examples of arithmetic and comparisons.

The README should explicitly explain that the project is primarily pedagogical and is not intended to replace `fractions.Fraction` as Python's general-purpose rational-number implementation.

---

# 35. English-only nomenclature

Use English consistently throughout the entire project.

This applies to:

- package names;
- module names;
- class names;
- method names;
- function names;
- variable names;
- constants;
- type aliases;
- comments;
- docstrings;
- error messages;
- test names;
- test descriptions;
- README/documentation.

For example, use:

```python
whole
numerator
denominator
simplified
as_fraction
```

and not Italian equivalents.

---

# 36. Code quality

The resulting implementation should be:

- idiomatic Python;
- type hinted;
- well documented;
- thoroughly tested;
- mathematically correct;
- easy to understand;
- free of unnecessary dependencies;
- based on `fractions.Fraction` for exact arithmetic;
- respectful of Python's numeric protocol.

Do not optimize prematurely.

Prioritize a clear architecture that makes the following distinction explicit:

```text
USER REPRESENTATION
        |
        v
(whole, numerator, denominator)
        |
        v
MATHEMATICAL VALUE
        |
        v
Fraction
        |
        v
EXACT ARITHMETIC
        |
        v
MixedFraction result
```

The constructor representation and the computational representation serve different purposes and must not be conflated.

---

# 37. Final validation

Before considering the task complete:

1. Run the complete unit-test suite.
2. Report the exact number of tests executed.
3. Report whether all tests pass.
4. Check that the package can be imported cleanly.
5. Check that type hints and public APIs are internally consistent.
6. Check that all documented examples behave as described.
7. Review the implementation specifically for accidental automatic normalization during construction.
8. Review the implementation specifically for incorrect handling of negative results.
9. Ensure that arithmetic is performed through `fractions.Fraction` rather than floating-point arithmetic.
10. Ensure that all project nomenclature and documentation are in English.
11. Verify that the project is installable as a standard Python package using `pip install .`.
12. Verify that the public import works as documented:

```python
from mixedfraction import MixedFraction
```

The final response should briefly summarize the implementation, the main design decisions, the test results, the packaging validation, and any design decisions that required interpretation.
