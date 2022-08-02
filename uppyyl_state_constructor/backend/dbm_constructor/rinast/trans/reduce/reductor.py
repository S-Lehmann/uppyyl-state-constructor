"""This module provides an abstract reductor."""

__author__ = "Jonas Rinast"

import abc


class Reductor(abc.ABC):
    """
    The Reductor interface allows the specification of a reduction algorithm
    applicable to sequences of Transformation objects part of a
    TransformationSystem.

    A Reductor is given an initial Evaluation object that is transformed using a
    sequence of Transformation objects. It is assumed to collect data on the
    transformation process to remove unnecessary Transformation objects from the
    sequence, i.e., Transformation objects that do not influence the final
    Evaluation object's state.

    A Reductor implementation is called as follows if we assume a declaration as "theReductor":

    1. The Reductor is initialized with a certain TransformationSystem and an
    initial Evaluation:
    "theReductor.initialize(theTransformationSystem, theInitialEvaluation)"

    2. The Reductor is repeatedly called when the TransformationSystem object
    performs a transformation of the current Evaluation object:
    "theReductor.apply(beforeEvaluation, theTransformation, afterEvaluation)"

    3. The Reductor is instructed to finalize its reduction:
    "theReductor.eliminate()"

    4. The client of the Reductor request the reduction result:
    "List theReducedSequence = theReductor.getPath()"

    Note that the Reductor is required to return a new List object for each call
    to "getPath()". Also note that step 2 and 3 may be repeated
    indefinitely, but the reduction result only needs to be recalculated during a
    call to "eliminate()".<br>
    """

    @abc.abstractmethod
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

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    def eliminate(self):
        """
        Instructs the Reductor to eliminate unnecessary Transformation objects in
        the Transformation sequence established using "apply()". Thereby
        validating subsequent calls to "getPath()".
        """
        pass

    @abc.abstractmethod
    def get_path(self):
        """
        Getter for the resulting reduced Transformation object sequence. Always
        returns a fresh List object. Be aware of timing constraints for calling
        "getPath()" as it may not return the most recent result.
        """
        pass
