"""Unit tests for the MixedFraction class.

Run with:

    python -m unittest discover
"""

from __future__ import annotations

import unittest
from fractions import Fraction

from mixedfraction import MixedFraction


class ConstructorTests(unittest.TestCase):
    def test_whole_defaults_to_zero(self):
        f = MixedFraction(numerator=3, denominator=4)
        self.assertEqual(f.whole, 0)

    def test_denominator_defaults_to_one(self):
        f = MixedFraction(whole=2, numerator=0)
        self.assertEqual(f.denominator, 1)

    def test_numerator_is_required(self):
        with self.assertRaises(TypeError):
            MixedFraction(whole=1)

    def test_valid_positive_values(self):
        f = MixedFraction(whole=1, numerator=3, denominator=4)
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 3, 4))

    def test_all_zero_components(self):
        f = MixedFraction(whole=0, numerator=0, denominator=1)
        self.assertEqual((f.whole, f.numerator, f.denominator), (0, 0, 1))
        self.assertEqual(f.as_fraction(), Fraction(0))

    def test_negative_whole_rejected(self):
        with self.assertRaises(ValueError):
            MixedFraction(whole=-1, numerator=3, denominator=4)

    def test_negative_numerator_rejected(self):
        with self.assertRaises(ValueError):
            MixedFraction(whole=1, numerator=-3, denominator=4)

    def test_zero_denominator_rejected(self):
        with self.assertRaises(ValueError):
            MixedFraction(whole=1, numerator=3, denominator=0)

    def test_negative_denominator_rejected(self):
        with self.assertRaises(ValueError):
            MixedFraction(whole=1, numerator=3, denominator=-4)

    def test_non_integer_whole_rejected(self):
        with self.assertRaises(TypeError):
            MixedFraction(1.5, 3, 4)

    def test_non_integer_numerator_rejected(self):
        with self.assertRaises(TypeError):
            MixedFraction(1, "3", 4)

    def test_non_integer_denominator_rejected(self):
        with self.assertRaises(TypeError):
            MixedFraction(1, 3, 4.0)

    def test_bool_rejected_as_component(self):
        with self.assertRaises(TypeError):
            MixedFraction(True, 3, 4)

    def test_improper_numerator_is_accepted_as_is(self):
        f = MixedFraction(whole=1, numerator=5, denominator=4)
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 5, 4))
        self.assertEqual(str(f), "1 5/4")
        self.assertEqual(f.as_fraction(), Fraction(9, 4))

    def test_numerator_equal_to_denominator_is_accepted_as_is(self):
        f = MixedFraction(whole=1, numerator=4, denominator=4)
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 4, 4))
        self.assertEqual(f.as_fraction(), Fraction(2, 1))


class RepresentationPreservationTests(unittest.TestCase):
    def test_reducible_fraction_is_not_reduced_on_construction(self):
        f = MixedFraction(1, 6, 8)
        self.assertEqual(f.whole, 1)
        self.assertEqual(f.numerator, 6)
        self.assertEqual(f.denominator, 8)

    def test_str_reflects_unreduced_representation(self):
        f = MixedFraction(1, 6, 8)
        self.assertEqual(str(f), "1 6/8")

    def test_equivalent_representations_stay_structurally_distinct(self):
        a = MixedFraction(1, 6, 8)
        b = MixedFraction(1, 3, 4)
        self.assertNotEqual((a.whole, a.numerator, a.denominator), (b.whole, b.numerator, b.denominator))

    def test_equivalent_representations_compare_equal(self):
        a = MixedFraction(1, 6, 8)
        b = MixedFraction(1, 3, 4)
        self.assertEqual(a, b)

    def test_as_fraction_does_not_mutate_original(self):
        f = MixedFraction(1, 6, 8)
        self.assertEqual(f.as_fraction(), Fraction(7, 4))
        self.assertEqual(str(f), "1 6/8")


class ConversionToFractionTests(unittest.TestCase):
    def test_proper_mixed_fraction(self):
        self.assertEqual(MixedFraction(1, 3, 4).as_fraction(), Fraction(7, 4))

    def test_unreduced_mixed_fraction(self):
        self.assertEqual(MixedFraction(1, 6, 8).as_fraction(), Fraction(7, 4))

    def test_zero_whole(self):
        self.assertEqual(MixedFraction(0, 3, 4).as_fraction(), Fraction(3, 4))

    def test_negative_value(self):
        f = -MixedFraction(1, 3, 4)
        self.assertEqual(f.as_fraction(), Fraction(-7, 4))


class SimplificationTests(unittest.TestCase):
    def test_six_eighths(self):
        f = MixedFraction(1, 6, 8)
        g = f.simplified()
        self.assertEqual(str(g), "1 3/4")

    def test_four_eighths(self):
        f = MixedFraction(2, 4, 8)
        g = f.simplified()
        self.assertEqual(str(g), "2 1/2")

    def test_zero_numerator(self):
        f = MixedFraction(3, 0, 5)
        g = f.simplified()
        self.assertEqual(str(g), "3")

    def test_original_object_unchanged(self):
        f = MixedFraction(1, 6, 8)
        f.simplified()
        self.assertEqual(str(f), "1 6/8")

    def test_simplified_returns_new_object(self):
        f = MixedFraction(1, 6, 8)
        g = f.simplified()
        self.assertIsNot(f, g)

    def test_simplify_method_does_not_exist(self):
        # Immutable design: only the copy-returning simplified() is provided.
        self.assertFalse(hasattr(MixedFraction(1, 6, 8), "simplify"))

    def test_improper_fractional_part_carries_into_whole(self):
        f = MixedFraction(1, 6, 4)  # 1 + 6/4 = 1 + 1 1/2 = 2 1/2
        g = f.simplified()
        self.assertEqual((g.whole, g.numerator, g.denominator), (2, 1, 2))
        self.assertEqual(str(g), "2 1/2")

    def test_improper_fractional_part_with_no_whole(self):
        f = MixedFraction(0, 9, 4)  # 9/4 = 2 1/4
        g = f.simplified()
        self.assertEqual((g.whole, g.numerator, g.denominator), (2, 1, 4))

    def test_numerator_equal_to_denominator_carries_fully(self):
        f = MixedFraction(1, 4, 4)  # 1 + 4/4 = 2
        g = f.simplified()
        self.assertEqual((g.whole, g.numerator, g.denominator), (2, 0, 1))
        self.assertEqual(str(g), "2")

    def test_simplified_matches_from_fraction_for_non_negative_values(self):
        f = MixedFraction(3, 11, 6)
        self.assertEqual(f.simplified(), MixedFraction.from_fraction(f.as_fraction()))
        g = f.simplified()
        h = MixedFraction.from_fraction(f.as_fraction())
        self.assertEqual((g.whole, g.numerator, g.denominator), (h.whole, h.numerator, h.denominator))

    def test_simplified_preserves_value(self):
        f = MixedFraction(1, 6, 4)
        self.assertEqual(f.simplified().as_fraction(), f.as_fraction())

    def test_simplified_of_negative_value_carries_correctly(self):
        f = -MixedFraction(1, 6, 4)  # -(2 1/2)
        g = f.simplified()
        self.assertEqual((g.whole, g.numerator, g.denominator), (2, 1, 2))
        self.assertEqual(str(g), "-2 1/2")


class SignTests(unittest.TestCase):
    def test_negation_of_positive(self):
        f = MixedFraction(1, 3, 4)
        self.assertEqual(str(-f), "-1 3/4")

    def test_double_negation(self):
        f = MixedFraction(1, 3, 4)
        self.assertEqual(-(-f), f)

    def test_negation_preserves_absolute_representation(self):
        f = -MixedFraction(1, 3, 4)
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 3, 4))

    def test_negation_of_zero_stays_zero(self):
        f = MixedFraction(0, 0, 1)
        self.assertEqual(-f, MixedFraction(0, 0, 1))
        self.assertEqual(str(-f), "0")

    def test_pos_of_positive(self):
        f = MixedFraction(1, 3, 4)
        self.assertEqual(+f, f)

    def test_abs_of_negative(self):
        f = -MixedFraction(1, 3, 4)
        self.assertEqual(abs(f), MixedFraction(1, 3, 4))

    def test_abs_of_positive(self):
        f = MixedFraction(1, 3, 4)
        self.assertEqual(abs(f), f)

    def test_abs_of_zero(self):
        self.assertEqual(abs(MixedFraction(0, 0, 1)), MixedFraction(0, 0, 1))

    def test_negative_arithmetic_result_sign(self):
        result = MixedFraction(1, 3, 4) - MixedFraction(2, 1, 3)
        self.assertEqual(result.as_fraction(), Fraction(-7, 12))


class ArithmeticTests(unittest.TestCase):
    def test_addition(self):
        a = MixedFraction(1, 3, 4)
        b = MixedFraction(2, 1, 3)
        self.assertEqual((a + b).as_fraction(), Fraction(49, 12))
        self.assertEqual(str(a + b), "4 1/12")

    def test_subtraction_negative_result(self):
        a = MixedFraction(1, 3, 4)
        b = MixedFraction(2, 1, 3)
        self.assertEqual(str(a - b), "-7/12")

    def test_subtraction_zero_result(self):
        a = MixedFraction(1, 3, 4)
        self.assertEqual(a - a, MixedFraction(0, 0, 1))

    def test_multiplication(self):
        a = MixedFraction(1, 1, 2)  # 3/2
        b = MixedFraction(0, 2, 3)  # 2/3
        self.assertEqual((a * b).as_fraction(), Fraction(1, 1))

    def test_division(self):
        a = MixedFraction(1, 1, 2)  # 3/2
        b = MixedFraction(0, 1, 2)  # 1/2
        self.assertEqual((a / b).as_fraction(), Fraction(3, 1))

    def test_power_positive_exponent(self):
        a = MixedFraction(1, 1, 2)  # 3/2
        self.assertEqual((a ** 2).as_fraction(), Fraction(9, 4))

    def test_power_zero(self):
        a = MixedFraction(1, 1, 2)
        self.assertEqual(a ** 0, MixedFraction(1, 0, 1))

    def test_power_one(self):
        a = MixedFraction(1, 1, 2)
        self.assertEqual(a ** 1, a)

    def test_power_negative_exponent(self):
        a = MixedFraction(0, 1, 2)  # 1/2
        self.assertEqual((a ** -1).as_fraction(), Fraction(2, 1))

    def test_arithmetic_with_int(self):
        a = MixedFraction(0, 1, 2)
        self.assertEqual((a + 1).as_fraction(), Fraction(3, 2))
        self.assertEqual((1 + a).as_fraction(), Fraction(3, 2))
        self.assertEqual((2 * a).as_fraction(), Fraction(1, 1))

    def test_arithmetic_with_fraction(self):
        a = MixedFraction(0, 1, 2)
        self.assertEqual((a + Fraction(1, 2)).as_fraction(), Fraction(1, 1))
        self.assertEqual((Fraction(1, 2) + a).as_fraction(), Fraction(1, 1))

    def test_arithmetic_result_is_reduced(self):
        a = MixedFraction(0, 2, 4)
        b = MixedFraction(0, 2, 4)
        result = a + b
        self.assertEqual((result.numerator, result.denominator), (0, 1))
        self.assertEqual(result.whole, 1)

    def test_large_values(self):
        a = MixedFraction(1_000_000, 1, 2)
        b = MixedFraction(2_000_000, 1, 2)
        self.assertEqual((a + b).as_fraction(), Fraction(3_000_001, 1))

    def test_reflected_subtraction(self):
        a = MixedFraction(0, 1, 2)
        self.assertEqual((1 - a).as_fraction(), Fraction(1, 2))

    def test_reflected_division(self):
        a = MixedFraction(0, 1, 2)
        self.assertEqual((1 / a).as_fraction(), Fraction(2, 1))

    def test_unsupported_operand_returns_not_implemented(self):
        a = MixedFraction(0, 1, 2)
        with self.assertRaises(TypeError):
            a + "not a number"
        with self.assertRaises(TypeError):
            a + 1.5


class ComparisonTests(unittest.TestCase):
    def test_equal_representations(self):
        self.assertEqual(MixedFraction(1, 2, 4), MixedFraction(1, 1, 2))

    def test_not_equal(self):
        self.assertNotEqual(MixedFraction(1, 1, 2), MixedFraction(1, 1, 3))

    def test_less_than(self):
        self.assertTrue(MixedFraction(0, 1, 4) < MixedFraction(0, 1, 2))

    def test_less_than_or_equal(self):
        self.assertTrue(MixedFraction(0, 1, 2) <= MixedFraction(0, 1, 2))
        self.assertTrue(MixedFraction(0, 1, 4) <= MixedFraction(0, 1, 2))

    def test_greater_than(self):
        self.assertTrue(MixedFraction(0, 1, 2) > MixedFraction(0, 1, 4))

    def test_greater_than_or_equal(self):
        self.assertTrue(MixedFraction(0, 1, 2) >= MixedFraction(0, 1, 2))
        self.assertTrue(MixedFraction(0, 1, 2) >= MixedFraction(0, 1, 4))

    def test_comparison_with_negative_values(self):
        self.assertTrue(-MixedFraction(0, 1, 2) < MixedFraction(0, 1, 4))

    def test_comparison_with_int_and_fraction(self):
        self.assertEqual(MixedFraction(1, 0, 1), 1)
        self.assertEqual(MixedFraction(0, 1, 2), Fraction(1, 2))

    def test_hash_consistency_for_equal_values(self):
        a = MixedFraction(1, 2, 4)
        b = MixedFraction(1, 1, 2)
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_usable_as_dict_key(self):
        d = {MixedFraction(1, 1, 2): "a"}
        self.assertEqual(d[MixedFraction(1, 2, 4)], "a")


class ZeroAndDivisionTests(unittest.TestCase):
    def test_division_by_zero_int(self):
        with self.assertRaises(ZeroDivisionError):
            MixedFraction(1, 1, 2) / 0

    def test_division_by_zero_mixed_fraction(self):
        with self.assertRaises(ZeroDivisionError):
            MixedFraction(1, 1, 2) / MixedFraction(0, 0, 1)

    def test_zero_str(self):
        self.assertEqual(str(MixedFraction(0, 0, 1)), "0")

    def test_zero_power_of_zero(self):
        self.assertEqual(MixedFraction(0, 0, 1) ** 0, MixedFraction(1, 0, 1))

    def test_negative_power_of_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            MixedFraction(0, 0, 1) ** -1


class EdgeCaseTests(unittest.TestCase):
    def test_denominator_one(self):
        f = MixedFraction(5, 0, 1)
        self.assertEqual(f.as_fraction(), Fraction(5, 1))
        self.assertEqual(str(f), "5")

    def test_numerator_zero_with_whole(self):
        self.assertEqual(str(MixedFraction(2, 0, 1)), "2")

    def test_very_large_integers(self):
        big = 10**30
        f = MixedFraction(big, 1, 2)
        self.assertEqual(f.as_fraction(), Fraction(2 * big + 1, 2))

    def test_exact_cancellation(self):
        a = MixedFraction(0, 1, 3)
        b = MixedFraction(0, 2, 3)
        self.assertEqual((a * 3 - 1), MixedFraction(0, 0, 1))
        self.assertEqual(a + b, MixedFraction(1, 0, 1))

    def test_values_crossing_zero(self):
        a = MixedFraction(0, 1, 2)
        b = MixedFraction(1, 0, 1)
        result = a - b
        self.assertEqual(result.as_fraction(), Fraction(-1, 2))
        self.assertTrue(result < MixedFraction(0, 0, 1))
        self.assertTrue(-result > MixedFraction(0, 0, 1))


class ReprTests(unittest.TestCase):
    def test_repr_preserves_representation(self):
        self.assertEqual(repr(MixedFraction(1, 6, 8)), "MixedFraction(1, 6, 8)")

    def test_repr_of_negative_value(self):
        self.assertEqual(repr(-MixedFraction(1, 3, 4)), "-MixedFraction(1, 3, 4)")

    def test_eval_of_repr_round_trips(self):
        f = MixedFraction(1, 6, 8)
        self.assertEqual(eval(repr(f), {"MixedFraction": MixedFraction}), f)

    def test_eval_of_repr_round_trips_negative(self):
        f = -MixedFraction(1, 3, 4)
        self.assertEqual(eval(repr(f), {"MixedFraction": MixedFraction}), f)


class StringFormattingTests(unittest.TestCase):
    def test_whole_and_fraction(self):
        self.assertEqual(str(MixedFraction(1, 3, 4)), "1 3/4")

    def test_fraction_only(self):
        self.assertEqual(str(MixedFraction(0, 3, 4)), "3/4")

    def test_whole_only(self):
        self.assertEqual(str(MixedFraction(2, 0, 1)), "2")

    def test_negative_whole_and_fraction(self):
        self.assertEqual(str(-MixedFraction(1, 3, 4)), "-1 3/4")


class FromFractionTests(unittest.TestCase):
    def test_basic(self):
        f = MixedFraction.from_fraction(Fraction(7, 4))
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 3, 4))

    def test_unreduced_input(self):
        f = MixedFraction.from_fraction(Fraction(14, 8))
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 3, 4))

    def test_negative_fraction(self):
        f = MixedFraction.from_fraction(Fraction(-7, 4))
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 3, 4))
        self.assertEqual(str(f), "-1 3/4")

    def test_zero(self):
        f = MixedFraction.from_fraction(Fraction(0))
        self.assertEqual((f.whole, f.numerator, f.denominator), (0, 0, 1))

    def test_integer_valued_fraction(self):
        f = MixedFraction.from_fraction(Fraction(5, 1))
        self.assertEqual(str(f), "5")

    def test_rejects_non_fraction(self):
        with self.assertRaises(TypeError):
            MixedFraction.from_fraction(1.5)


class FromStringTests(unittest.TestCase):
    def test_whole_and_fraction(self):
        f = MixedFraction.from_string("1 3/4")
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 3, 4))

    def test_fraction_only(self):
        f = MixedFraction.from_string("3/4")
        self.assertEqual((f.whole, f.numerator, f.denominator), (0, 3, 4))

    def test_whole_only(self):
        f = MixedFraction.from_string("2")
        self.assertEqual((f.whole, f.numerator, f.denominator), (2, 0, 1))

    def test_negative(self):
        f = MixedFraction.from_string("-1 3/4")
        self.assertEqual(str(f), "-1 3/4")

    def test_invalid_empty_string(self):
        with self.assertRaises(ValueError):
            MixedFraction.from_string("")

    def test_invalid_garbage(self):
        with self.assertRaises(ValueError):
            MixedFraction.from_string("abc")

    def test_improper_fraction_is_accepted_as_is(self):
        f = MixedFraction.from_string("1 5/4")
        self.assertEqual((f.whole, f.numerator, f.denominator), (1, 5, 4))
        self.assertEqual(f.as_fraction(), Fraction(9, 4))

    def test_invalid_type(self):
        with self.assertRaises(TypeError):
            MixedFraction.from_string(174)  # not a string


class NumericConversionTests(unittest.TestCase):
    def test_int_truncates_toward_zero_positive(self):
        self.assertEqual(int(MixedFraction(1, 3, 4)), 1)

    def test_int_truncates_toward_zero_negative(self):
        self.assertEqual(int(-MixedFraction(1, 3, 4)), -1)

    def test_float_approximation(self):
        self.assertAlmostEqual(float(MixedFraction(0, 1, 2)), 0.5)


class ImmutabilityTests(unittest.TestCase):
    def test_properties_are_read_only(self):
        f = MixedFraction(1, 3, 4)
        with self.assertRaises(AttributeError):
            f.whole = 2  # type: ignore[misc]

    def test_no_dynamic_attributes(self):
        f = MixedFraction(1, 3, 4)
        with self.assertRaises(AttributeError):
            f.extra = 1  # type: ignore[misc]


class ImproperRepresentationTests(unittest.TestCase):
    def test_improper_numerator_and_denominator(self):
        f = MixedFraction(1, 3, 4)
        self.assertEqual(f.improper_numerator, 7)
        self.assertEqual(f.improper_denominator, 4)


if __name__ == "__main__":
    unittest.main()
