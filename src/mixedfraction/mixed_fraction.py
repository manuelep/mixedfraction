"""Pedagogical mixed-fraction representation built on top of ``fractions.Fraction``.

This module defines :class:`MixedFraction`, a small, immutable class that
models a *mixed fraction* the way it is usually written on paper, e.g.::

    1 3/4

The central idea of this module -- and the reason it exists even though
Python already ships with :class:`fractions.Fraction` -- is to make an
explicit, visible distinction between three things that are easy to
conflate:

1. The **user-facing representation** supplied to the constructor: the
   triple ``(whole, numerator, denominator)`` exactly as written by the
   caller, e.g. ``(1, 6, 8)``.
2. The **mathematical value** that representation denotes, e.g. ``7/4``.
3. The **computational representation** used to perform exact arithmetic
   on that value: a standard-library :class:`fractions.Fraction`.

``MixedFraction`` never silently normalizes (1) into (2)/(3) during
construction. The stored ``whole``, ``numerator`` and ``denominator`` are
exactly what was supplied, unreduced. Normalization only happens when it is
explicitly requested (:meth:`MixedFraction.simplified`) or when it is an
unavoidable consequence of an operation that has no other representation to
preserve, such as arithmetic (:meth:`MixedFraction.__add__` and friends) or
conversion from a bare :class:`fractions.Fraction`
(:meth:`MixedFraction.from_fraction`).
"""

from __future__ import annotations

import math
import re
from fractions import Fraction
from functools import total_ordering
from typing import Union

__all__ = ["MixedFraction"]

#: Types that can be coerced into an exact mathematical value and combined
#: with a MixedFraction in arithmetic and comparisons.
_Operand = Union["MixedFraction", Fraction, int]

_STRING_FRACTION_RE = re.compile(r"^(?:(?P<whole>\d+)\s+)?(?P<num>\d+)/(?P<den>\d+)$")
_STRING_WHOLE_RE = re.compile(r"^\d+$")


def _require_int(name: str, value: object) -> None:
    """Raise ``TypeError`` unless *value* is a plain ``int`` (not ``bool``)."""
    # bool is a subclass of int in Python; accepting it silently would let
    # ``True``/``False`` sneak in as ``1``/``0``, which is not an int literal
    # the way the API is meant to be used.
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"{name} must be an int, got {type(value).__name__!r}"
        )


def _coerce_to_fraction(value: object) -> Fraction | None:
    """Best-effort conversion of *value* to an exact :class:`Fraction`.

    Returns ``None`` (rather than raising) when *value* is not a supported
    operand type, so callers can return ``NotImplemented`` and let Python's
    numeric protocol try the reflected operation on the other operand.

    Floats are intentionally *not* accepted here: converting a float to an
    exact rational is not something this class does implicitly, since it
    would silently mix inexact and exact arithmetic.
    """
    if isinstance(value, MixedFraction):
        return value.as_fraction()
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Fraction(value)
    return None


@total_ordering
class MixedFraction:
    """An immutable pedagogical mixed-fraction value.

    A ``MixedFraction`` stores exactly the three components it was
    constructed with -- ``whole``, ``numerator`` and ``denominator`` -- and
    preserves them unchanged for the lifetime of the object. Its
    mathematical value is exposed separately through :meth:`as_fraction`.

    Parameters
    ----------
    whole:
        The non-negative whole part. Defaults to ``0``.
    numerator:
        The non-negative numerator of the fractional part. Required (there
        is no meaningful default).
    denominator:
        The positive denominator of the fractional part. Defaults to ``1``.

    Constraints
    ----------
    ``whole >= 0``, ``numerator >= 0``, ``denominator > 0``. All three
    components must be ``int``. None of these constraints are silently
    "fixed" -- violating them raises ``TypeError`` (wrong type) or
    ``ValueError`` (wrong value).

    The fractional part is **not** required to be proper:
    ``MixedFraction(1, 6, 4)`` (i.e. ``1 6/4``) is accepted as-is, exactly
    as supplied -- it is not rejected and not auto-carried into ``whole``.
    Use :meth:`simplified` to explicitly obtain the canonical form (largest
    possible ``whole``, reduced proper fraction) as a new object.

    Negative values are represented by negating a ``MixedFraction`` with
    the unary ``-`` operator, never by a constructor argument. There is no
    ``positive=`` / ``negative=`` flag: the sign lives at the value level,
    not in the stored components.

    Construction never simplifies. ``MixedFraction(1, 6, 8)`` keeps
    ``6/8`` exactly as given; call :meth:`simplified` to obtain
    ``1 3/4`` as a new object.
    """

    __slots__ = ("_whole", "_numerator", "_denominator", "_sign")

    def __init__(self, whole: int = 0, numerator: int | None = None, denominator: int = 1) -> None:
        if numerator is None:
            raise TypeError(
                "numerator is a required argument (there is no default value)"
            )

        _require_int("whole", whole)
        _require_int("numerator", numerator)
        _require_int("denominator", denominator)

        if whole < 0:
            raise ValueError(f"whole must be >= 0, got {whole}")
        if numerator < 0:
            raise ValueError(f"numerator must be >= 0, got {numerator}")
        if denominator <= 0:
            raise ValueError(f"denominator must be > 0, got {denominator}")

        self._whole = whole
        self._numerator = numerator
        self._denominator = denominator
        # The public constructor never accepts negative components, so a
        # freshly-constructed MixedFraction is always non-negative. Negative
        # values only ever come from __neg__ / _from_parts below.
        self._sign = 1

    # ------------------------------------------------------------------
    # Internal constructor bypassing validation, used only by code paths
    # that have already computed a valid, normalized (whole, numerator,
    # denominator, sign) tuple themselves (__neg__, __abs__, simplified(),
    # from_fraction(), arithmetic results, ...).
    # ------------------------------------------------------------------
    @classmethod
    def _from_parts(cls, whole: int, numerator: int, denominator: int, sign: int) -> "MixedFraction":
        obj = object.__new__(cls)
        obj._whole = whole
        obj._numerator = numerator
        obj._denominator = denominator
        # Negative zero is not a distinct value: normalize its sign to +1.
        obj._sign = 1 if (whole == 0 and numerator == 0) else sign
        return obj

    # ------------------------------------------------------------------
    # Read-only access to the preserved representation
    # ------------------------------------------------------------------
    @property
    def whole(self) -> int:
        """The whole part exactly as supplied to the constructor."""
        return self._whole

    @property
    def numerator(self) -> int:
        """The numerator of the fractional part exactly as supplied."""
        return self._numerator

    @property
    def denominator(self) -> int:
        """The denominator of the fractional part exactly as supplied."""
        return self._denominator

    @property
    def sign(self) -> int:
        """``1`` for non-negative values, ``-1`` for negative values.

        The sign is a property of the mathematical value, not one of the
        three constructor components; it is exposed here read-only for
        convenience.
        """
        return self._sign

    @property
    def improper_numerator(self) -> int:
        """The numerator of the equivalent *improper* (unsigned) fraction.

        For ``MixedFraction(1, 3, 4)`` this is ``7``. This is the magnitude
        only; use :meth:`as_fraction` for the signed mathematical value.
        """
        return self._whole * self._denominator + self._numerator

    @property
    def improper_denominator(self) -> int:
        """The denominator of the equivalent improper fraction.

        This is always equal to :attr:`denominator`.
        """
        return self._denominator

    # ------------------------------------------------------------------
    # Conversion to the mathematical value
    # ------------------------------------------------------------------
    def as_fraction(self) -> Fraction:
        """Return the exact mathematical value as a :class:`fractions.Fraction`.

        This never mutates ``self`` and never changes the preserved
        representation; it only computes the value that representation
        denotes.
        """
        magnitude = Fraction(self.improper_numerator, self._denominator)
        return magnitude if self._sign >= 0 else -magnitude

    @classmethod
    def from_fraction(cls, fraction: Fraction) -> "MixedFraction":
        """Build a canonical ``MixedFraction`` from a :class:`fractions.Fraction`.

        Because a bare ``Fraction`` carries no information about how it was
        originally written as a mixed fraction, this always produces a
        *canonical* representation: the largest possible whole part and a
        reduced, proper fractional part. For example both
        ``Fraction(7, 4)`` and ``Fraction(14, 8)`` produce ``1 3/4``.

        Negative fractions are supported: the sign is carried on the
        result as a whole, and ``whole``/``numerator``/``denominator`` hold
        the magnitude, exactly as with any other negative ``MixedFraction``.
        For example ``MixedFraction.from_fraction(Fraction(-7, 4))``
        produces the value ``-1 3/4`` (``whole=1``, ``numerator=3``,
        ``denominator=4``, negated).
        """
        if not isinstance(fraction, Fraction):
            raise TypeError(f"fraction must be a fractions.Fraction, got {type(fraction).__name__!r}")

        sign = -1 if fraction < 0 else 1
        magnitude = -fraction if sign < 0 else fraction

        whole, remainder_numerator = divmod(magnitude.numerator, magnitude.denominator)
        return cls._from_parts(whole, remainder_numerator, magnitude.denominator, sign)

    # ------------------------------------------------------------------
    # Simplification (explicit only -- never automatic)
    # ------------------------------------------------------------------
    def simplified(self) -> "MixedFraction":
        """Return the canonical form: largest possible ``whole``, reduced proper fraction.

        Two things happen here, both driven by the same goal -- turning
        whatever was supplied into the simplest, most "proper" mixed
        fraction with the same value:

        - the fractional part is reduced to lowest terms (e.g. ``6/8``
          becomes ``3/4``);
        - if the (reduced) fractional part is improper (``numerator >=
          denominator``), the extra whole units it contains are carried
          into ``whole``, so the result always has a proper fractional
          part.

        Does not mutate ``self``; the original object and its original
        representation are left exactly as they were.

        Examples
        --------
        ``1 6/8`` -> ``1 3/4``
        ``2 4/8`` -> ``2 1/2``
        ``3 0/5`` -> ``3``
        ``1 6/4`` -> ``2 1/2``   (carry: 6/4 reduces to 3/2, then 1 + 3/2 = 2 1/2)

        This makes ``simplified()`` equivalent to
        ``MixedFraction.from_fraction(self.as_fraction())`` for non-negative
        values -- but as a method on ``self`` it reads more naturally where
        the source is already a ``MixedFraction``, and it does not require
        going through an intermediate ``Fraction``.

        Note
        ----
        There is intentionally no in-place ``simplify()`` method:
        ``MixedFraction`` is immutable, so an in-place simplification would
        be inconsistent with every other operation on this class, all of
        which return new objects.
        """
        if self._numerator == 0:
            numerator, denominator = 0, 1
        else:
            divisor = math.gcd(self._numerator, self._denominator)
            numerator = self._numerator // divisor
            denominator = self._denominator // divisor

        extra_whole, numerator = divmod(numerator, denominator)
        whole = self._whole + extra_whole
        return MixedFraction._from_parts(whole, numerator, denominator, self._sign)

    # ------------------------------------------------------------------
    # String parsing / formatting
    # ------------------------------------------------------------------
    @classmethod
    def from_string(cls, text: str) -> "MixedFraction":
        """Parse a ``MixedFraction`` from a string such as ``"1 3/4"``.

        Accepted forms (optionally prefixed with ``-`` or ``+``):

        - ``"1 3/4"``  -- whole plus fractional part (may be improper, e.g. ``"1 5/4"``)
        - ``"3/4"``    -- fraction only (``whole`` defaults to ``0``)
        - ``"2"``      -- whole number only
        - ``"-1 3/4"`` -- negative value

        Parsing is strict: extra whitespace beyond a single separating
        space, missing components, non-digit characters, or a zero
        denominator all raise ``ValueError``. Passing a non-``str`` raises
        ``TypeError``.
        """
        if not isinstance(text, str):
            raise TypeError(f"text must be a str, got {type(text).__name__!r}")

        body = text.strip()
        if not body:
            raise ValueError(f"cannot parse an empty string as a MixedFraction: {text!r}")

        sign = 1
        if body[0] in "+-":
            if body[0] == "-":
                sign = -1
            body = body[1:].strip()
            if not body:
                raise ValueError(f"invalid MixedFraction string: {text!r}")

        fraction_match = _STRING_FRACTION_RE.match(body)
        if fraction_match:
            whole_str = fraction_match.group("whole")
            whole = int(whole_str) if whole_str is not None else 0
            numerator = int(fraction_match.group("num"))
            denominator = int(fraction_match.group("den"))
        elif _STRING_WHOLE_RE.match(body):
            whole = int(body)
            numerator = 0
            denominator = 1
        else:
            raise ValueError(f"invalid MixedFraction string: {text!r}")

        try:
            magnitude = cls(whole, numerator, denominator)
        except ValueError as exc:
            raise ValueError(f"invalid MixedFraction string: {text!r} ({exc})") from exc

        return -magnitude if sign < 0 else magnitude

    def __str__(self) -> str:
        if self._whole == 0 and self._numerator == 0:
            return "0"

        parts: list[str] = []
        if self._whole != 0:
            parts.append(str(self._whole))
        if self._numerator != 0:
            parts.append(f"{self._numerator}/{self._denominator}")

        body = " ".join(parts)
        return f"-{body}" if self._sign < 0 else body

    def __repr__(self) -> str:
        base = f"MixedFraction({self._whole}, {self._numerator}, {self._denominator})"
        return f"-{base}" if self._sign < 0 else base

    # ------------------------------------------------------------------
    # Sign
    # ------------------------------------------------------------------
    def __neg__(self) -> "MixedFraction":
        return MixedFraction._from_parts(self._whole, self._numerator, self._denominator, -self._sign)

    def __pos__(self) -> "MixedFraction":
        return self

    def __abs__(self) -> "MixedFraction":
        return MixedFraction._from_parts(self._whole, self._numerator, self._denominator, 1)

    # ------------------------------------------------------------------
    # Arithmetic -- always computed via fractions.Fraction, never floats.
    # Results are canonical (see from_fraction), unlike constructor input.
    # ------------------------------------------------------------------
    def __add__(self, other: _Operand) -> "MixedFraction":
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return MixedFraction.from_fraction(self.as_fraction() + other_fraction)

    __radd__ = __add__

    def __sub__(self, other: _Operand) -> "MixedFraction":
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return MixedFraction.from_fraction(self.as_fraction() - other_fraction)

    def __rsub__(self, other: _Operand) -> "MixedFraction":
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return MixedFraction.from_fraction(other_fraction - self.as_fraction())

    def __mul__(self, other: _Operand) -> "MixedFraction":
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return MixedFraction.from_fraction(self.as_fraction() * other_fraction)

    __rmul__ = __mul__

    def __truediv__(self, other: _Operand) -> "MixedFraction":
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return MixedFraction.from_fraction(self.as_fraction() / other_fraction)

    def __rtruediv__(self, other: _Operand) -> "MixedFraction":
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return MixedFraction.from_fraction(other_fraction / self.as_fraction())

    def __pow__(self, exponent: object) -> "MixedFraction":
        if isinstance(exponent, bool) or not isinstance(exponent, int):
            return NotImplemented
        # fractions.Fraction already implements exactly the semantics we
        # want here, including raising ZeroDivisionError for 0 ** negative.
        return MixedFraction.from_fraction(self.as_fraction() ** exponent)

    # ------------------------------------------------------------------
    # Numeric conversions
    # ------------------------------------------------------------------
    def __int__(self) -> int:
        """Truncate toward zero, consistent with Python's numeric conventions."""
        return int(self.as_fraction())

    def __float__(self) -> float:
        """Approximate conversion to a Python ``float``.

        This is inherently inexact for values whose denominator is not a
        power of two; ``MixedFraction`` never uses this conversion
        internally for its own arithmetic.
        """
        return float(self.as_fraction())

    # ------------------------------------------------------------------
    # Comparisons -- always by mathematical value, never by representation.
    # ------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return self.as_fraction() == other_fraction

    def __lt__(self, other: object) -> bool:
        other_fraction = _coerce_to_fraction(other)
        if other_fraction is None:
            return NotImplemented
        return self.as_fraction() < other_fraction

    def __hash__(self) -> int:
        # Equality is defined purely in terms of as_fraction(), so the hash
        # must be too, in order to keep `a == b => hash(a) == hash(b)`.
        return hash(self.as_fraction())
