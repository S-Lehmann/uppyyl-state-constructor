"""This module provides a variable implementation."""

__author__ = "Jonas Rinast"


class Variable:
    """
    The Variable class is a data class to represent a variable, for either data
    or time, in an UPPAAL system. Such a variable is identified by its local name
    and the context it is in, either global or local to an instance of a
    template. For example, the variable named "foo" in a template "bar"
    instantiated as "bat" is referred to by "bat.foo".
    """

    def __init__(self, variable):
        """
        Constructs a Variable object from a fully qualified name.

        Args:
            variable: The name of the variable.
        """
        parts = variable.split(".")
        if len(parts) == 1:
            self.instance = None
            self.name = parts[0]
        elif len(parts) >= 2:
            self.instance = parts[0]
            self.name = parts[1]
        self.value = None

    def has_instance(self):
        """
        Checks whether the variable is a template local one.

        Returns:
            True if local to a template, False otherwise.
        """
        return self.instance is not None

    def set_instance(self, instance):
        """
        Setter for the instance name of this variable.

        Args:
            instance: The instance name.
        """
        self.instance = instance

    def get_instance(self):
        """
        Getter for the instance name of this variable.

        Returns:
            The instance.
        """
        if self.instance is None:
            return "__UOI_INIT"
        return self.instance

    def get_name(self):
        """
        Getter of the name of this variable.

        Returns:
            The name.
        """
        return self.name

    def get_full_name(self):
        """
        Getter for the fully qualified name of this variable.

        Returns:
            The fully qualified name.
        """
        if self.instance is None:
            return self.name
        else:
            return self.instance + "." + self.name

    def get_value(self):
        """
        Getter of the value of this variable.

        Returns:
            The value.
        """
        return self.value

    def set_value(self, value):
        """
        Setter for the value of this variable.

        Args:
            value: The value to set.
        """
        self.value = value

    def __str__(self):
        string = ""

        string += str(self.name)
        string += " = "
        string += str(self.value)

        return string

    def __hash__(self):
        prime = 31
        result = 1
        result = prime * result + (0 if (self.instance is None) else hash(self.instance))
        result = prime * result + (0 if (self.name is None) else hash(self.name))
        return result

    def __eq__(self, other):
        if isinstance(other, Variable):
            if self.instance == other.instance and self.name == other.name:
                return True
        return False
