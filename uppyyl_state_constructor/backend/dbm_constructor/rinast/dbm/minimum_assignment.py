"""This module provides a minimum assignment mapping."""

__author__ = "Jonas Rinast"

from ..trans.simple_transformation import (
    SpecificationMapping
)


class MinimumAssignment(SpecificationMapping):
    """
    The MinimumAssignment class implements the SpecificationMapping interface to
    specify a calculation used in DBM Transformation objects. This class performs
    the following function and requires one parameter:

    ret = min(value, par1)
    """

    def __init__(self, value):
        """
        Constructor for the MinimumAssignment object with the provided minimum value.

        Args:
            value: The minimum value.
        """
        self.value = value

    def map(self, parameters):
        """Maps the function to the parameters.

        Args:
            parameters: The list of parameters.

        Returns:
            None
        """
        if self.value.compare_to(parameters[0]) < 0:
            return self.value
        return parameters[0]

    def __str__(self):
        return "minAssign_" + str(self.value)
