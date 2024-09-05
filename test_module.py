"""
This is a test module to demonstrate AutoDoc functionality.
"""
from autodoc import autodoc
import math
from typing import List, Dict

autodoc('test_module.py', 'test_module_docs')
GLOBAL_CONSTANT = 42

def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle.

    Args:
        radius (float): The radius of the circle.

    Returns:
        float: The area of the circle.
    """
    return math.pi * radius ** 2

class Shape:
    """
    A base class for geometric shapes.
    """

    def __init__(self, name: str):
        self.name = name

    def area(self) -> float:
        """
        Calculate the area of the shape.

        Returns:
            float: The area of the shape.
        """
        raise NotImplementedError("Subclasses must implement area() method")

class Circle(Shape):
    """
    A class representing a circle.
    """

    def __init__(self, name: str, radius: float):
        super().__init__(name)
        self.radius = radius

    def area(self) -> float:
        """
        Calculate the area of the circle.

        Returns:
            float: The area of the circle.
        """
        return calculate_area(self.radius)

def process_shapes(shapes: List[Shape]) -> Dict[str, float]:
    """
    Process a list of shapes and return their areas.

    Args:
        shapes (List[Shape]): A list of Shape objects.

    Returns:
        Dict[str, float]: A dictionary mapping shape names to their areas.
    """
    return {shape.name: shape.area() for shape in shapes}