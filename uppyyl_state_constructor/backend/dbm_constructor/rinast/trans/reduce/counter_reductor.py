"""This module provides a counter reductor."""

__author__ = "Jonas Rinast"

from .reductor import (
    Reductor
)


class UniqueTransformation:
    """
    The UniqueTransformation class is a Transformation object wrapper used to
    distinguish between two identical Transformation objects. This is
    necessary when the Transformation object occurs multiple times in the
    Transformation sequence subject to reduction. The UniqueTransformation
    class associates a Transformation object with an id of type long for this
    purpose.

    Adjusted "equals()" and "hashCode()" methods are provided.
    """

    def __init__(self, transformation, id_):
        """Initializes UniqueTransformation.

        Args:
            transformation: The transformation object.
            id_: The transformation id.
        """
        self.transformation = transformation
        self.id = id_

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if (self.id is None) else hash(self.id))
        result = prime * result + (0 if (self.transformation is None) else hash(self.transformation))
        return result

    def __eq__(self, other):
        if isinstance(other, UniqueTransformation):
            if self.transformation == other.transformation and self.id == other.id:
                return True
        return False


class CounterReductor(Reductor):
    """
    The CounterReductor class implements a reduction algorithm based on
    use-definition chains. It counts how often an Evaluation object is referenced
    in read and write operations during the application of the Transformation
    object sequence and eliminates Transformation object, which do not have an
    influence on the final Evaluation object.

    Two cases where a Transformation object is removed exist:
    1. The Transformation does not write any element of the Evaluation vector.
    2. Elements of the Evaluation vector written by the Transformation are not
    read before they are overwritten by another subsequent Transformation object.
    """

    def __init__(self):
        """Initializes CounterReductor."""

        # The highest unique identification number currently unused for Transformation objects
        self.uniqueId = 0

        self.transformations = []

        # The reference counter map associates an UniqueTransformation object with
        # an integer representing how many other UniqueTransformation objects
        # depend on it.
        self.counters = {}

        # The responsibility map associates every element of the current Evaluation
        # vector, identified by its index, with the UniqueTransformation that wrote
        # that element last.
        self.responsibilities = {}

        # The use-definition map associates an UniqueTransformation object with all
        # the UniqueTransformation objects that are required for it to produce the
        # same Evaluation object when applied.
        self.uses = {}

    def initialize(self, system, initial_evaluation):
        """
        Initializes the Reductor object. The Reductor reduces Transformation
        sequences obtained from the given TransformationSystem object. The given
        Evaluation object is the first object of the sequence to reduce.

        Args:
            system: The TransformationSystem object.
            initial_evaluation: The initial Evaluation object.
        """
        # the virtual Transformation "None" is responsible for all variables initially
        self.counters[None] = system.get_variable_count()

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
        unique = UniqueTransformation(transformation, self.uniqueId)
        self.uniqueId += 1
        self.transformations.append(unique)

        loci = set()
        for i in transformation.get_read_set():
            responsible = self.responsibilities[i]
            self.counters[responsible] += 1
            loci.add(responsible)
        self.uses[unique] = loci

        writes = transformation.get_write_set()
        for i in writes:
            responsible = self.responsibilities[i]
            self.counters[responsible] -= 1
            self.responsibilities[i] = unique
        self.counters[unique] = writes.size()

    def eliminate(self):
        """
        Instructs the Reductor to eliminate unnecessary Transformation objects in
        the Transformation sequence established using "apply()". Thereby
        validating subsequent calls to "getPath()".
        """
        # Fixed point iteration
        while True:
            fixpoint = True

            for i in range(0, len(self.transformations)):
                t = self.transformations[i]

                if self.counters[t] == 0:
                    self.transformations.remove(t)
                    for s in self.uses[t]:
                        self.counters[s] -= 1

                    # Adjust index due to removed transformation
                    i -= 1
                    fixpoint = False
            if fixpoint:
                break

    def get_path(self):
        """
        Getter for the resulting reduced Transformation object sequence. Always
        returns a fresh List object. Be aware of timing constraints for calling
        "getPath()" as it may not return the most recent result.
        """
        path = []
        for t in self.transformations:
            path.append(t.transformation)
        return path

    def __str__(self):
        string = ""
        string += "[COUNTERREDUCTOR] {\n"

        for c_key, c_val in self.counters.items():
            string += '\t'
            string += "Counter: "
            string += str(c_val)
            string += " {"
            if c_key is None:
                string += "[TRANSFORMATION] { initial }"
            else:
                string += str(c_key.transformation)
                string += ' '
                string += str(c_key.id)
            string += "}\n"

        for r_key, r_val in self.responsibilities.items():
            string += '\t'
            string += "Responsibility: "
            string += str(r_key)
            string += " {"
            string += str(r_val.transformation)
            string += ' '
            string += str(r_val.id)
            string += "}\n"

        for u_key, u_val in self.uses.items():
            string += '\t'
            string += "Uses for {"
            string += str(u_key.transformation)
            string += ' '
            string += str(u_key.id)
            string += "} {\n"
            for t in u_val:
                string += "\t\t"
                if t is None:
                    string += "[TRANSFORMATION] { initial }"
                else:
                    string += str(t.transformation)
                    string += ' '
                    string += str(t.id)
                string += '\n'
            string += "\t}\n"
        string += '}'

        return string
