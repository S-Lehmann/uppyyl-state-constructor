"""This module provides an info transformation."""

__author__ = "Jonas Rinast"

from .transformation import (
    Transformation
)


class InfoTransformation(Transformation):
    """
    The abstract InfoTransformation class provides the basic functionality for
    attaching and retrieving an additional TransformationInfo object. This class
    is meant to be used as a base class for a class implementing the
    Transformation interface and the TransformationInfo object is used.
    """

    def __init__(self):
        """Initializes InfoTransformation."""
        self.info = None

    def set_info(self, info):
        """Attaches an additional TransformationInfo object to the Transformation.

        Args:
            info: The TransformationInfo object to attach.
        """
        self.info = info

    def get_info(self):
        """
        Getter for the attached TransformationInfo object.

        Returns:
            The attached TransformationInfo object.
        """
        return self.info

    def get_read_set(self):
        """
        Getter for a set of variables read by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables read.
        """
        pass

    def get_write_set(self):
        """
        Getter for a set of variables written by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables written.
        """
        pass

    def apply(self, evaluation):
        """
        Applies the transformation to the provided Evaluation object. The
        provided Evaluation object may not be modified, a copy should be
        returned.

        Args:
            evaluation: The Evaluation object to transform.

        Returns:
            The transformed Evaluation object.
        """
        pass
