"""This module provides a minimum addition mapping."""

__author__ = "Jonas Rinast"

from ..trans.simple_transformation import (
    SpecificationMapping
)


class MinimumAddition(SpecificationMapping):
    """
    The MinimumAddition class implements the SpecificationMapping interface to
    specify a calculation used in DBM Transformation objects. This class performs
    the following function and requires three parameters:

    ret = min(par1, par2 + par3)
    """

    def map(self, parameters):
        """Maps the function to the parameters.

        Args:
            parameters: The list of parameters.

        Returns:
            None
        """
        ret = parameters[0]
        sum_val = parameters[1].add(parameters[2])

        if sum_val.compare_to(ret) < 0:
            ret = sum_val

        return ret

    def __str__(self):
        return "minAdd"
