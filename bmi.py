"""
BMI Calculation Module
======================
This module provides core business logic for calculating Body Mass Index (BMI),
classifying BMI into standard World Health Organization (WHO) health categories,
mapping categories to distinct UI theme colors, providing health recommendations,
and validating user input.
"""

from typing import Tuple, Dict, Any


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculates the Body Mass Index (BMI) given weight in kilograms and height in meters.

    Formula:
        BMI = weight / (height ^ 2)

    Args:
        weight_kg (float): Weight of the user in kilograms (kg).
        height_m (float): Height of the user in meters (m).

    Returns:
        float: Calculated BMI rounded to 2 decimal places.

    Raises:
        ValueError: If height is zero or negative, or weight is negative.
    """
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")

    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def get_bmi_category(bmi: float) -> Dict[str, Any]:
    """
    Classifies a numerical BMI value into a health category, assigns a color code,
    and provides a friendly health advice message.

    Categories:
        - Underweight: BMI < 18.5 (Color: Blue)
        - Normal Weight: 18.5 <= BMI <= 24.9 (Color: Green)
        - Overweight: 25.0 <= BMI <= 29.9 (Color: Orange)
        - Obese: BMI >= 30.0 (Color: Red)

    Args:
        bmi (float): The Body Mass Index value.

    Returns:
        dict: Dictionary containing:
            - 'category': String category name
            - 'color': Hex color string for GUI styling
            - 'message': Health recommendation message string
    """
    if bmi < 18.5:
        return {
            "category": "Underweight",
            "color": "#2563EB",  # Royal Blue
            "message": "You are underweight. Consider consulting a nutritionist for a balanced weight-gain plan."
        }
    elif 18.5 <= bmi <= 24.9:
        return {
            "category": "Normal Weight",
            "color": "#16A34A",  # Emerald Green
            "message": "Great job! You have a normal body weight. Maintain your healthy diet and regular physical activity."
        }
    elif 25.0 <= bmi <= 29.9:
        return {
            "category": "Overweight",
            "color": "#EA580C",  # Vivid Orange
            "message": "You are in the overweight range. Regular exercise and a balanced diet can help manage your weight."
        }
    else:
        return {
            "category": "Obese",
            "color": "#DC2626",  # Crimson Red
            "message": "You are in the obese category. It is recommended to consult a healthcare provider for personalized health guidance."
        }


def validate_inputs(username_str: str, weight_str: str, height_str: str) -> Tuple[bool, str, str, float, float]:
    """
    Validates user input fields before performing calculations or database storage.

    Rules checked:
        1. Username must not be empty or whitespace only.
        2. Weight and Height must not be empty.
        3. Weight and Height must be valid numeric values (float convertible).
        4. Weight and Height must be positive numbers (> 0).
        5. Height must be within a realistic meter range (e.g. height between 0.4m and 3.0m).

    Args:
        username_str (str): Raw username string from GUI input.
        weight_str (str): Raw weight input from GUI.
        height_str (str): Raw height input from GUI.

    Returns:
        Tuple[bool, str, str, float, float]:
            - is_valid (bool): True if inputs are valid, False otherwise.
            - error_message (str): Description of validation failure, or empty if valid.
            - clean_username (str): Trimmed username.
            - parsed_weight (float): Converted weight in kg (0.0 if invalid).
            - parsed_height (float): Converted height in m (0.0 if invalid).
    """
    clean_username = username_str.strip()
    clean_weight = weight_str.strip()
    clean_height = height_str.strip()

    # Check for empty fields
    if not clean_username:
        return False, "Please enter a user name.", "", 0.0, 0.0
    if not clean_weight:
        return False, "Please enter weight in kilograms (kg).", clean_username, 0.0, 0.0
    if not clean_height:
        return False, "Please enter height in meters (m).", clean_username, 0.0, 0.0

    # Parse numeric weight
    try:
        weight = float(clean_weight)
    except ValueError:
        return False, f"Invalid weight value '{clean_weight}'. Please enter a valid number.", clean_username, 0.0, 0.0

    # Parse numeric height
    try:
        height = float(clean_height)
    except ValueError:
        return False, f"Invalid height value '{clean_height}'. Please enter a valid number.", clean_username, 0.0, 0.0

    # Range and sign validation
    if weight <= 0:
        return False, "Weight must be greater than 0 kg.", clean_username, 0.0, 0.0

    if height <= 0:
        return False, "Height must be greater than 0 meters.", clean_username, 0.0, 0.0

    if height > 3.0:
        return False, (
            f"Height entered is {height} meters. Please ensure height is specified in meters (m), not centimeters (cm).\n"
            "Example: 175 cm should be entered as 1.75 m."
        ), clean_username, 0.0, 0.0

    if height < 0.4:
        return False, "Height is unrealistically low (minimum 0.4 m). Please check your input.", clean_username, 0.0, 0.0

    return True, "", clean_username, weight, height
