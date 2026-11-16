import math
import random
import subprocess
import sys
import unittest
from pathlib import Path

from hypothesis import example, given, settings, strategies as st

from warranty_claims import age_average, parse_claim, payable_charge


MODULE_PATH = Path(__file__).with_name("warranty_claims.py")


fuzz_settings = settings(max_examples=300, deadline=None, derandomize=True, database=None)


unexpected = st.one_of(st.text(), st.none(), st.integers(), st.booleans(),
                       st.binary(), st.lists(st.integers(), max_size=5))


@fuzz_settings
@given(st.text() | st.none())
def test_parse_claim_no_crash(s):
    result = parse_claim(s)
    if result is not None:
        plan, age = result
        assert plan in {"Basic", "Standard", "Premium"}
        assert math.isfinite(age) and age >= 0


@fuzz_settings
@given(st.text() | st.none())
def test_age_average_no_crash(s):
    result = age_average(s)
    assert result is None or (isinstance(result, int) and result >= 0)


@fuzz_settings
@given(st.text() | st.none())
def test_payable_charge_no_crash(s):
    result = payable_charge(s)
    assert result is None or (math.isfinite(result) and result >= 0)


@fuzz_settings
@given(unexpected)
def test_all_functions_handle_unexpected_types(value):
    for function in (parse_claim, age_average, payable_charge):
        result = function(value)
        if not isinstance(value, str):
            assert result is None


@fuzz_settings
@given(st.sampled_from(["basic", "standard", "premium"]),
       st.floats(min_value=0, max_value=1e100, allow_nan=False,
                 allow_infinity=False))
def test_valid_claims(plan, age):
    assert parse_claim("  {} : {}  ".format(plan.upper(), age)) == (plan.title(), age)


@fuzz_settings
@given(st.lists(st.integers(min_value=0, max_value=10**30),
                min_size=1, max_size=100))
@example([0])
@example([1, 2])
def test_valid_ages(values):
    text = ",".join(str(value) for value in values)
    average = age_average(text)
    assert average == sum(values) // len(values)
    assert min(values) <= average <= max(values)


@fuzz_settings
@given(st.integers(min_value=0, max_value=10**9),
       st.integers(min_value=0, max_value=10**9))
def test_valid_charges(charge, discount):
    assert payable_charge("{}|{}".format(charge, discount)) == max(
        float(charge) * 1.18 - float(discount), 0.0)


@fuzz_settings
@given(st.integers(min_value=0, max_value=10**9),
       st.integers(min_value=0, max_value=10**9),
       st.integers(min_value=0, max_value=10**9))
def test_more_discount_never_increases_payable(charge, first, extra):
    before = payable_charge("{}|{}".format(charge, first))
    after = payable_charge("{}|{}".format(charge, first + extra))
    assert after <= before


@fuzz_settings
@given(st.sampled_from(["nan", "NaN", "inf", "-inf", "1e309", "-1e309"]))
def test_nonfinite_numbers_are_rejected(number):
    assert parse_claim("basic:" + number) is None
    assert payable_charge(number + "|0") is None
    assert payable_charge("100|" + number) is None


@fuzz_settings
@given(st.integers(min_value=1, max_value=10**30))
def test_negative_values_are_rejected(value):
    assert parse_claim("standard:-{}".format(value)) is None
    assert age_average("0,-{}".format(value)) is None
    assert payable_charge("-{}|0".format(value)) is None
    assert payable_charge("100|-{}".format(value)) is None


class WarrantyRegressionTests(unittest.TestCase):
    def test_parse_claim_no_crash(self):
        for value in [None, "", "standard", "a:b:c", 5, [], b"x", True]:
            with self.subTest(value=value):
                self.assertIsNone(parse_claim(value))

    def test_age_average_no_crash(self):
        for value in [None, "", " ", "12,,24", 5, [], b"x", True]:
            with self.subTest(value=value):
                self.assertIsNone(age_average(value))

    def test_payable_charge_no_crash(self):
        for value in [None, "", "100", "1|2|3", 5, [], b"x", True]:
            with self.subTest(value=value):
                self.assertIsNone(payable_charge(value))

    def test_claim_examples(self):
        for text, expected in [("standard:30", ("Standard", 30.0)),
                               (" BASIC : 0 ", ("Basic", 0.0)),
                               ("premium:12.5", ("Premium", 12.5))]:
            self.assertEqual(parse_claim(text), expected)

    def test_claim_invalid_numbers_and_plans(self):
        for text in ["gold:12", ":12", "basic:", "basic:-1", "basic:nan",
                     "basic:inf", "basic:1e309", "basic:abc", "basic:1:2"]:
            with self.subTest(text=text):
                self.assertIsNone(parse_claim(text))

    def test_age_examples_and_floor_behavior(self):
        for text, expected in [("12,24,36", 24), ("1,2", 1),
                               ("0", 0), (" 12 , 24 ", 18)]:
            self.assertEqual(age_average(text), expected)

    def test_invalid_age_tokens(self):
        for text in ["1,-2", "1,2.5", "one,two", ",12", "12,", "nan", "inf"]:
            with self.subTest(text=text):
                self.assertIsNone(age_average(text))

    def test_long_integer_does_not_crash(self):
        result = age_average("9" * 5000)
        self.assertTrue(result is None or (isinstance(result, int) and result >= 0))

    def test_charge_examples(self):
        self.assertEqual(payable_charge("1500|200"), 1570.0)
        self.assertEqual(payable_charge("100|200"), 0.0)
        self.assertEqual(payable_charge(" 0 | 0 "), 0.0)
        self.assertAlmostEqual(payable_charge("12.5|2.5"), 12.25)

    def test_charge_invalid_numbers(self):
        for text in ["-100|0", "100|-1", "nan|0", "100|nan", "inf|0",
                     "1e309|0", "1.7e308|0", "100|", "|2", "a|b"]:
            with self.subTest(text=text):
                self.assertIsNone(payable_charge(text))

    def test_generated_valid_claims(self):
        rng = random.Random(173)
        for _ in range(500):
            plan = rng.choice(["basic", "standard", "premium"])
            age = rng.randrange(10000) / 10
            self.assertEqual(parse_claim(f"{plan}:{age}"), (plan.title(), age))

    def test_generated_valid_ages(self):
        rng = random.Random(174)
        for _ in range(500):
            ages = [rng.randrange(100000) for _ in range(rng.randrange(1, 25))]
            self.assertEqual(age_average(",".join(map(str, ages))), sum(ages) // len(ages))

    def test_generated_valid_charges(self):
        rng = random.Random(175)
        for _ in range(500):
            charge, discount = rng.randrange(100000), rng.randrange(100000)
            result = payable_charge(f"{charge}|{discount}")
            self.assertEqual(result, max(float(charge) * 1.18 - float(discount), 0.0))
            self.assertTrue(math.isfinite(result))

    def test_random_text_and_wrong_types(self):
        rng = random.Random(176)
        alphabet = "abc0123 :|,.-+" + "\x00\n\t\u03a9\u0967"
        for _ in range(1000):
            value = "".join(rng.choices(alphabet, k=rng.randrange(50)))
            for function in [parse_claim, age_average, payable_charge]:
                function(value)

    def test_cli_handles_invalid_input(self):
        result = subprocess.run([sys.executable, str(MODULE_PATH)],
                                input="bad\n12,,24\nnan|0\n", text=True,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("Invalid input."), 3)

    def test_cli_handles_eof(self):
        result = subprocess.run([sys.executable, str(MODULE_PATH)], input="",
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Input cancelled.", result.stdout)
