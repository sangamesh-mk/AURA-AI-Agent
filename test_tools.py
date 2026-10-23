
import unittest
from tools import calculate


class TestCalculate(unittest.TestCase):

    def test_addition(self):
        self.assertEqual(calculate("2 + 3"), 5)

    def test_multiplication(self):
        self.assertEqual(calculate("10 * 5"), 50)

    def test_parentheses_and_division(self):
        self.assertEqual(calculate("(100 - 20) / 4"), 20)

    def test_exponentiation(self):
        self.assertEqual(calculate("2 ** 8"), 256)

    def test_division_by_zero(self):
        result = calculate("10 / 0")
        self.assertTrue(result.startswith("Calculation error:"))

    def test_oversized_exponent(self):
        result = calculate("2 ** 1000")
        self.assertTrue(result.startswith("Calculation error:"))

    def test_unsafe_expression(self):
        result = calculate("__import__('os').system('dir')")
        self.assertTrue(result.startswith("Calculation error:"))


if __name__ == "__main__":
    unittest.main()
