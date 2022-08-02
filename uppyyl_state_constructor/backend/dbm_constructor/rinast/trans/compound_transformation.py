"""This module provides a compound transformation."""

__author__ = "Jonas Rinast"

from .info_transformation import (
    InfoTransformation
)
from .evaluation import (
    Evaluation
)


class CompoundTransformation(InfoTransformation):
    """
    The CompoundTransformation class defines a transformation by executing a
    sequence of individual Transformation objects.

    Note that a CompoundTransformation object can not be instantiated by clients
    directly. To obtain a clean instance, query a TransformationSystem object by
    calling "createCompoundTransformation()".
    """

    def __init__(self):
        """Initializes CompoundTransformation."""
        super().__init__()
        self.transformations = []

    def add_transformation(self, transformation):
        """
        Appends another Transformation object to the sequence of Transformation
        to execute when applying the transformation this CompoundTransformation
        object defines. Call this function (repeatedly) to obtain the desired
        transformational behavior.

        Args:
            transformation: The transformation the append to the transformation sequence.

        Returns:
            None
        """
        if transformation is not None:
            self.transformations.append(transformation)

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
        result = Evaluation(evaluation=evaluation)
        for t in self.transformations:
            result = t.apply(result)
        return result

    def get_read_set(self):
        """
        Getter for a set of variables read by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables read.
        """
        reads = set()
        writes = set()

        for t in self.transformations:
            read = t.get_read_set()
            for w in writes:
                read.discard(w)
            for w in t.get_write_set():
                writes.add(w)
            for r in read:
                reads.add(r)

        return reads

    def get_write_set(self):
        """
        Getter for a set of variables written by the Transformation object when
        applied. The set contains the indices into the Evaluation object vector.

        Returns:
            The indices set of variables written.
        """
        writes = set()

        for t in self.transformations:
            for w in t.get_write_set():
                writes.add(w)

        return writes

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if (self.transformations is None) else hash(tuple(self.transformations)))
        return result

    def __eq__(self, other):
        if isinstance(other, CompoundTransformation):
            if self.transformations == other.transformations:
                return True
        return False

    def __str__(self):
        string = ""
        string += "[TRANSFORMATION] { "

        for t in self.transformations:
            string += str(t)
            string += ' '

        string += '}'

        return string
