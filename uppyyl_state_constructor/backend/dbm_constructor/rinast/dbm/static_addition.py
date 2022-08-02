"""This module provides a static addition mapping."""

__author__ = "Jonas Rinast"

from ..trans.simple_transformation import (
    SpecificationMapping
)


class StaticAddition(SpecificationMapping):
    """
    The StaticAddition class implements the SpecificationMapping interface to
    specify a calculation used in DBM Transformation objects. This class performs
    the following function and requires one parameter:

    ret = adder + par1
    """

    def __init__(self, adder):
        """
        Constructor for a StaticAddition object that adds the provided value.

        Args:
            adder: The value to add.
        """
        self.adder = adder

    def map(self, parameters):
        """Maps the function to the parameters.

        Args:
            parameters: The list of parameters.

        Returns:
            None
        """
        return parameters[0].add(self.adder)

    def __str__(self):
        return "add_" + str(self.adder)
