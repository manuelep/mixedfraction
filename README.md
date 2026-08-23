# mixedfraction

A small, **pedagogical** Python library for working with *mixed fractions*
(e.g. `1 3/4`), built on top of the standard library's `fractions.Fraction`.

```python
from mixedfraction import MixedFraction

f = MixedFraction(1, 3, 4)
print(f)              # 1 3/4
print(f.as_fraction()) # 7/4
```

## Why does this exist? Python already has `fractions.Fraction`

It does, and `mixedfraction` does not try to replace it. `fractions.Fraction`
is the right tool for exact rational arithmetic, and this library uses it
internally for every calculation.

What `Fraction` does *not* do is distinguish between how a fraction was
**written** and what it **means**. `Fraction(7, 4)` and `Fraction(14, 8)`
are the same object as far as `Fraction` is concerned — the `14/8` you
typed is gone the moment it's constructed, replaced by the reduced `7/4`.

`MixedFraction` exists specifically to keep that distinction visible. It
models three separate ideas explicitly:

```text
USER REPRESENTATION            (whole, numerator, denominator) — exactly as written
        |
        v
MATHEMATICAL VALUE              what that representation means, e.g. 7/4
        |
        v
COMPUTATIONAL REPRESENTATION    a fractions.Fraction, used for exact arithmetic
```

This makes it a useful teaching tool for the difference between *notation*
and *value* — a distinction that's easy to lose once everything gets
silently normalized.

## The core idea: construction preserves; arithmetic normalizes

```python
f = MixedFraction(1, 6, 8)

f.whole, f.numerator, f.denominator   # (1, 6, 8) — unchanged, unreduced
str(f)                                # "1 6/8"
f.as_fraction()                       # Fraction(7, 4) — the value, computed on demand

g = f.simplified()                    # an explicit request to reduce
str(g)                                # "1 3/4"
str(f)                                # still "1 6/8" — f itself never changes
```

Contrast this with arithmetic, where there is no "original representation"
to preserve — the result of `a + b` is a brand-new value, so it is returned
in canonical form:

```python
a = MixedFraction(1, 3, 4)   # 7/4
b = MixedFraction(2, 1, 3)   # 7/3

a + b                        # MixedFraction(4, 1, 12) -> "4 1/12"
```

Internally this is computed as `Fraction(7, 4) + Fraction(7, 3)`, and the
resulting `Fraction` is converted back into a canonical `MixedFraction` via
`MixedFraction.from_fraction`.

## Constructor

```python
MixedFraction(whole=0, numerator=None, denominator=1)
```

- `whole` — non-negative `int`, defaults to `0`.
- `numerator` — non-negative `int`, **required** (no sensible default).
- `denominator` — positive `int`, defaults to `1`.

All three arguments must be actual `int` values — floats, strings, and
`bool` are rejected with `TypeError` rather than silently converted.
Out-of-range values (negative components, a zero or negative denominator)
raise `ValueError`.

The fractional part does **not** need to be proper. Construction never
simplifies and never folds anything into `whole` on its own —
`MixedFraction(1, 6, 8)` stays `1 6/8`, and `MixedFraction(whole=1,
numerator=5, denominator=4)` is accepted exactly as written (`1 5/4`,
worth `9/4`) rather than being silently turned into `2 1/4`. Call
`simplified()` when you actually want the canonical form.

## Negative values

There is no `positive=` / `negative=` constructor flag. Negative values are
created with unary `-`:

```python
f = MixedFraction(1, 3, 4)
-f            # -1 3/4
-(-f) == f    # True
```

The sign lives at the value level, not inside `whole`/`numerator`/
`denominator`, which always hold non-negative magnitudes.

## Explicit simplification

```python
MixedFraction(1, 6, 8).simplified()   # -> "1 3/4"
MixedFraction(2, 4, 8).simplified()   # -> "2 1/2"
MixedFraction(3, 0, 5).simplified()   # -> "3"
MixedFraction(1, 6, 4).simplified()   # -> "2 1/2"  (6/4 -> 3/2, carried: 1 + 3/2 = 2 1/2)
```

`simplified()` returns the canonical form: it reduces the fractional part
to lowest terms *and* carries any resulting improper part into `whole`, so
the result always has the largest possible whole part and a proper,
reduced fraction — equivalent to
`MixedFraction.from_fraction(self.as_fraction())`, just expressed as a
method on an existing `MixedFraction`. It always returns a *new* object —
`MixedFraction` is immutable, so there is no in-place `simplify()`.

## Equality compares by value, not by representation

```python
MixedFraction(1, 2, 4) == MixedFraction(1, 1, 2)   # True
```

Two `MixedFraction` objects with different stored components can be equal,
because equality (and all other comparisons: `<`, `<=`, `>`, `>=`) is based
on the exact mathematical value (`as_fraction()`), not on the stored
`(whole, numerator, denominator)` triple.

## Arithmetic

`+`, `-`, `*`, `/`, `**` are all implemented, always via `fractions.Fraction`
— never floating point. `MixedFraction`, `fractions.Fraction`, and `int`
operands are all supported, including reflected operations (`1 + f`,
`2 * f`, ...). Division by a zero-valued operand raises `ZeroDivisionError`,
matching `Fraction`'s own behavior.

## Not a general-purpose numeric type

This project is intentionally scoped to be a small, readable teaching
example. It is **not** meant to replace `fractions.Fraction` as Python's
general-purpose rational-number type — use `Fraction` directly for that.
`MixedFraction` is for the specific case where the *mixed-fraction
notation itself* (not just the value) matters.

## Installation

```bash
pip install .
# or, for development:
pip install -e .
```

## Usage

```python
from mixedfraction import MixedFraction

a = MixedFraction(1, 3, 4)
b = MixedFraction(2, 1, 3)

a + b                          # 4 1/12
a - b                          # -7/12
a.simplified()                 # 1 3/4 (already simplified here)
a == MixedFraction(1, 6, 8)    # True: both represent 7/4
```

Equivalent representations always compare equal, regardless of how they're
written.

## Development

Run the test suite:

```bash
python -m unittest discover
```

Build the distribution (requires the `build` package, an optional
development dependency):

```bash
python -m build
```
