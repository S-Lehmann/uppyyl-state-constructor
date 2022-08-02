"""This module provides a DBM value."""

__author__ = "Jonas Rinast"

import sys


class DBValue:
    """
    The DBValue class is a simple data class to represent a single value in a
    difference bound matrix. An entry consists of an integer value and either the
    comparator less, or the comparator less-equal: (v,<) or (v,<=). The infinity
    element is created by providing Integer.MAX_VALUE as the value. The
    comparator is adjusted automatically.
    """

    def __init__(self, value=None, bound=None, other=None):
        """
        Constructs a DBValue from the given integer and boolean. If bound is true
        the comparator is less-equal, false represents strictly less.

        Args:
            value: The integer value.
            bound: The comparator type.
            other: Another DBM value.
        """
        if other is not None:
            self.value = other.value
            self.bound = other.bound
        elif value is not None and bound is not None:
            self.value = value
            self.bound = False if value == sys.maxsize else bound

    def get_value(self):
        """Gets the DBM value.

        Returns:
            The DBM value.
        """
        return self.value

    def get_bound(self):
        """
    Getter for the comparator type.

        Returns:
            True if less-equal, False if strictly less.
        """
        return self.bound

    def set_value(self, value):
        """Sets the value.

        Args:
            value: The value.
        """
        self.value = value
        if value == sys.maxsize:
            self.bound = False

    def set_bound(self, bound):
        """
        Setter for the comparator type

        true: less-equal
        false: strictly less

        Args:
            bound: The comparator type to set
        """
        if self.value != sys.maxsize:
            self.bound = bound

    def add(self, other):
        """
        Adds this DBValue object to another one. A strictly less comparator is
        only kept if both operands had strictly less comparators. Adding
        something to infinity has no effect. Always returns a new object.

        Args:
            other: The other DBValue object to add.

        Returns:
            The new DBValue object resulting from the add.
        """
        ret = DBValue(other=self)
        if ret.value == sys.maxsize or other.value == sys.maxsize:
            ret.value = sys.maxsize
            ret.bound = False
        else:
            ret.value += other.value
            ret.bound &= other.bound

        return ret

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (1231 if self.bound else 1237)
        result = prime * result + self.value
        return result

    def __eq__(self, other):
        if isinstance(other, DBValue):
            if self.bound == other.bound and self.value == other.value:
                return True
        return False

    def compare_to(self, other):
        """Compares the value to another.

        Args:
            other: The other value.

        Returns:
            The comparison result.
        """
        if self.value == other.value:
            if self.bound == other.bound:
                return 0
            return 1 if self.bound else -1
        else:
            if self.value == sys.maxsize:
                return 1
            elif other.value == sys.maxsize:
                return -1
            return self.value - other.value

    def __str__(self):
        string = ""

        string += '('
        if self.value == sys.maxsize:
            string += "inf"
        elif self.value == -sys.maxsize:
            string += "-inf"
        else:
            string += str(self.value)

        string += ",<"
        if self.bound:
            string += '='
        string += ')'

        return string
