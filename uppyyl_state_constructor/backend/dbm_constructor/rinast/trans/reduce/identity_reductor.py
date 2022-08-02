"""This module provides an identity reductor."""

__author__ = "Jonas Rinast"

from .reductor import (
    Reductor
)


class IdentityReductor(Reductor):
    """
    The IdentityReductor class implements is a dummy Reductor implementation. No
    Transformation objects will be removed from the Transformation object
    sequence.
    """

    def __init__(self):
        """Initializes IdentityReductor."""
        self.transformations = []

    def initialize(self, system, initial_evaluation):
        """
        Initializes the Reductor object. The Reductor reduces Transformation
        sequences obtained from the given TransformationSystem object. The given
        Evaluation object is the first object of the sequence to reduce.

        Args:
            system: The TransformationSystem object.
            initial_evaluation: The initial Evaluation object.
        """
        pass

    def apply(self, evaluation, transformation, transformed_evaluation):
        """
        Instructs the Reductor that a Transformation object has been applied to
        the current Evaluation object. Note that a call to "apply()" may
        invalidate subsequent calls to "getPath()".

        Args:
            evaluation: The Evaluation object the Transformation object was applied to.
            transformation: The Transformation object that was applied.
            transformed_evaluation: the Evaluation object resulting from the Transformation application.
        """
        self.transformations.append(transformation)

    def eliminate(self):
        """
        Instructs the Reductor to eliminate unnecessary Transformation objects in
        the Transformation sequence established using "apply()". Thereby
        validating subsequent calls to "getPath()".
        """
        pass

    def get_path(self):
        """
        Getter for the resulting reduced Transformation object sequence. Always
        returns a fresh List object. Be aware of timing constraints for calling
        "getPath()" as it may not return the most recent result.
        """
        path = self.transformations.copy()
        return path

    def __str__(self):
        string = ""
        string += "[IDENTITYREDUCTOR] {\n"

        for t in self.transformations:
            string += '\t'
            string += str(t)
            string += '\n'

        string += '}'

        return string
