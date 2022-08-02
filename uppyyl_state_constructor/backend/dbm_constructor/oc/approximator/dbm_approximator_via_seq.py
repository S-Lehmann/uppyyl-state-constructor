"""This module implements the DBM approximation based on a given operation sequence."""

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationSequence, Reset, DelayFuture
)


################
# Approximator #
################
class DBMApproximatorViaSeq:
    """A class for DBM approximation based on a given operation sequence."""

    def __init__(self, clocks):
        """Initializes DBMApproximatorViaSeq.

        Args:
            clocks: A list of all system clocks.
        """
        self.seq_approx = None
        self.clocks = clocks
        self.clear()

    def clear(self):
        """Clears the currently generated approximation sequence.

        Returns:
            None
        """
        self.seq_approx = DBMOperationSequence()

    def update_sequence(self, data):
        """Updates the approximation sequence based on a given data observation increment.

        Args:
            data: The data of the observation increment.

        Returns:
            The updated approximation sequence.
        """
        self.seq_approx = update_approximation_sequence_via_seq(self.seq_approx, data["seq_incr"], self.clocks)
        return self.seq_approx

    def generate_sequence(self, data):
        """Generates the approximation sequence based on given sequence data.

        Args:
            data: The observed sequence and DBM data.

        Returns:
            The approximation sequence.
        """
        self.seq_approx = generate_approximation_sequence_via_seq(data["seq_full"], self.clocks)
        return self.seq_approx

    def get_sequence(self):
        """Gets the approximation sequence.

        Returns:
            The approximation sequence.
        """
        return self.seq_approx


################################################################################

# Update a given approximation sequence by a newly observed sequence
def update_approximation_sequence_via_seq(seq_approx, seq, clocks):
    """Updates an approximation sequence based on a given operation sequence increment.

    Args:
        seq_approx: The current approximation sequence.
        seq: The operation sequence increment.
        clocks: A list of all system clocks.

    Returns:
        The approximation sequence.
    """
    reduced_sequence = DBMOperationSequence()
    reset_clocks = []
    df_added = False

    for i, operation in enumerate(reversed(seq_approx + seq)):
        if isinstance(operation, DelayFuture):
            if not df_added:
                reduced_sequence.append(operation.copy())
                df_added = True
        elif isinstance(operation, Reset):
            clock = operation.clock
            if clock not in reset_clocks:
                reset_clocks.append(clock)
                reduced_sequence.append(operation.copy())
                df_added = False

        if len(reset_clocks) == len(clocks):
            break

    reduced_sequence.reverse()
    return reduced_sequence


# Generate an approximation sequence from scratch from a given sequence
def generate_approximation_sequence_via_seq(seq, clocks):
    """Generates an approximation sequence based on a given operation sequence.

    Args:
        seq: The original operation sequence.
        clocks: A list of all system clocks.

    Returns:
        The approximation sequence.
    """
    empty_sequence = DBMOperationSequence()
    reduced_sequence = update_approximation_sequence_via_seq(empty_sequence, seq, clocks)
    return reduced_sequence
