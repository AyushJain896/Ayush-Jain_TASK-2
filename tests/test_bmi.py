"""
Unit Tests for BMI Calculation and Validation Logic (bmi.py)
"""

import unittest
from bmi import calculate_bmi, get_bmi_category, validate_inputs


class TestBMICalculation(unittest.TestCase):

    def test_calculate_bmi_normal(self):
        """Test BMI calculation formula."""
        # 70 kg, 1.75 m -> 70 / (1.75^2) = 22.86
        bmi = calculate_bmi(70.0, 1.75)
        self.assertEqual(bmi, 22.86)

    def test_calculate_bmi_zero_or_negative_height(self):
        """Test that non-positive height raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_bmi(70.0, 0.0)

        with self.assertRaises(ValueError):
            calculate_bmi(70.0, -1.5)

    def test_get_bmi_category_underweight(self):
        """Test Underweight classification (< 18.5)."""
        info = get_bmi_category(17.5)
        self.assertEqual(info["category"], "Underweight")
        self.assertEqual(info["color"], "#2563EB")

    def test_get_bmi_category_normal(self):
        """Test Normal Weight classification (18.5 - 24.9)."""
        info = get_bmi_category(22.0)
        self.assertEqual(info["category"], "Normal Weight")
        self.assertEqual(info["color"], "#16A34A")

    def test_get_bmi_category_overweight(self):
        """Test Overweight classification (25.0 - 29.9)."""
        info = get_bmi_category(27.5)
        self.assertEqual(info["category"], "Overweight")
        self.assertEqual(info["color"], "#EA580C")

    def test_get_bmi_category_obese(self):
        """Test Obese classification (>= 30.0)."""
        info = get_bmi_category(32.1)
        self.assertEqual(info["category"], "Obese")
        self.assertEqual(info["color"], "#DC2626")

    def test_validate_inputs_valid(self):
        """Test valid input parsing."""
        is_valid, msg, user, weight, height = validate_inputs("Alice", "65.5", "1.68")
        self.assertTrue(is_valid)
        self.assertEqual(user, "Alice")
        self.assertEqual(weight, 65.5)
        self.assertEqual(height, 1.68)

    def test_validate_inputs_empty_username(self):
        """Test empty username rejection."""
        is_valid, msg, user, weight, height = validate_inputs("  ", "65", "1.7")
        self.assertFalse(is_valid)
        self.assertIn("user name", msg.lower())

    def test_validate_inputs_non_numeric(self):
        """Test non-numeric weight/height rejection."""
        is_valid, msg, user, weight, height = validate_inputs("Bob", "abc", "1.7")
        self.assertFalse(is_valid)
        self.assertIn("invalid weight", msg.lower())


if __name__ == "__main__":
    unittest.main()
