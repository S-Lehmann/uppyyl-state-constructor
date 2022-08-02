"""This module provides a static assignment mapping."""

__author__ = "Jonas Rinast"

from ..trans.simple_transformation import (
    SpecificationMapping
)


class StaticAssignment(SpecificationMapping):
    """
    The StaticAssignment class implements the SpecificationMapping interface to
    specify a calculation used in DBM Transformation objects. This class performs
    the following function and requires no parameters:

    ret = value
    """
    def __init__(self, value):
        """
        Constructor for a StaticAssignment object that assigns the given value.

        Args:
            value: The value to assign.
        """
        self.value = value

    def map(self, parameters):
        """Maps the function to the parameters.

        Args:
            parameters: The list of parameters.

        Returns:
            None
        """
        return self.value

    def __str__(self):
        return "assign_" + str(self.value)
