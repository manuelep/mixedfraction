"""A pedagogical mixed-fraction library built on top of ``fractions.Fraction``.

The only public symbol is :class:`MixedFraction`::

    from mixedfraction import MixedFraction

    fraction = MixedFraction(1, 3, 4)
    print(fraction)  # 1 3/4

Importing this package has no side effects: it does not print anything,
perform I/O, or execute unrelated code.
"""

from .mixed_fraction import MixedFraction

__all__ = ["MixedFraction"]
__version__ = "0.1.0"
