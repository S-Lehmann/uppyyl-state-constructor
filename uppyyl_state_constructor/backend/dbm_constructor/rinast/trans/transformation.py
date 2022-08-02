"""This module provides an abstract transformation."""

__author__ = "Jonas Rinast"
import abc


class Transformation(abc.ABC):
    """
    The Transformation interface allows the specification of transformations
    applicable to Evaluation objects of the underlying TransformationSystem
    object. The Transformation object is required to not only implement the
    actual modification to the Evaluation object, but also provide sets of the
    variables read and written by it.
    """

    @abc.abstractmethod
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

    @abc.abstractmethod
    def get_read_set(self):
        """
        Getter for a set of variables read by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables read.
        """
        pass

    @abc.abstractmethod
    def get_write_set(self):
        """
        Getter for a set of variables written by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables written.
        """
        pass

    @abc.abstractmethod
    def set_info(self, info):
        """Attaches an additional TransformationInfo object to the Transformation.

        Args:
            info: The TransformationInfo object to attach.
        """
        pass

    @abc.abstractmethod
    def get_info(self):
        """
        Getter for the attached TransformationInfo object.

        Returns:
            The attached TransformationInfo object.
        """
        pass
