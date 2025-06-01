from langchain_core.tools import tool
import math

# https://python.langchain.com/v0.2/docs/how_to/custom_tools/
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return round(a * b, 3)

@tool
def solve_quadratic_equation(a: float, b: float, c: float) -> str:
    """ Solve the quadratic equation ax**2 + bx + c = 0."""
    discriminant = b**2 - 4*a*c

    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        return f"Two distinct real roots: {x1}, {x2}"
    elif discriminant == 0:
        x = -b / (2*a)
        return f"One real root: {x}"
    else:
        real_part = -b / (2*a)
        imaginary_part = math.sqrt(abs(discriminant)) / (2*a)
        return f"Two complex roots: {real_part} + {imaginary_part}i, {real_part} - {imaginary_part}i"