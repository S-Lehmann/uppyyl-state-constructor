"""This modules provides a random DBM operation sequence generation."""

import random

import numpy as np

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationGenerator, DBMOperationSequence
)

dbm_op_gen = DBMOperationGenerator()


class RandomSequenceGenerator:
    """A generator for random DBM operation sequences."""

    def __init__(self, sequence_length, dbm_init, non_zero_resets=True, include_init_sequence=False):
        """Initializes RandomSequenceGenerator.

        Args:
            sequence_length: The targeted sequence length.
            dbm_init: The initial DBM to which the sequence is applied.
            non_zero_resets: Choose whether non-zero resets should be allowed.
            include_init_sequence: Choose whether an initial sequence resetting all clocks to zero should be included.
        """
        self.sequence_length = sequence_length
        self.dbm_init = dbm_init
        self.non_zero_resets = non_zero_resets
        self.include_init_sequence = include_init_sequence

        self.sequence = None
        self.dbm = None

    def generate(self):
        """Generate a random valid DBM operation sequence.

        Returns:
            The generated operation sequence.
        """
        self.dbm = self.dbm_init.copy()
        self.sequence = DBMOperationSequence()

        if self.include_init_sequence:
            self._append_init_sequence()

        # Initial locations
        self._append_random_sequence_for_locations()

        # (Repeated) transitions
        while len(self.sequence) < self.sequence_length:
            self._append_random_sequence_for_edges()
            self._append_random_sequence_for_locations()

        return self.sequence

    # Generate init sequence
    def _append_init_sequence(self):
        """Appends the optional initial all-zero-reset sequence.

        Returns:
            None
        """
        if len(self.dbm.clocks) - 1 > self.sequence_length:
            raise Exception(
                f'Init sequence length ({len(self.dbm.clocks) - 1}) is greater '
                f'than targeted sequence length ({self.sequence_length})')
        for clock in self.dbm.clocks[1:]:
            reset = dbm_op_gen.generate_reset(clock=clock, val=0)
            reset.apply(self.dbm)
            self.sequence.append(reset)

    def _append_random_sequence_for_edges(self):
        """Appends a random sequence following the structure of an Uppaal edge.

        Returns:
            None
        """
        if random.choice([True, False]):
            # Edge guard
            clocks = random.sample(self.dbm.clocks[1:], random.randint(1, len(self.dbm.clocks[1:])))
            guard_count = 0
            for clock in clocks:
                if len(self.sequence) > (self.sequence_length - 2):
                    break
                clock_index = self.dbm.clocks.index(clock)
                clock_lower_bound = -self.dbm.matrix[0][clock_index].val
                clock_upper_bound = self.dbm.matrix[clock_index][0].val
                if clock_upper_bound == np.inf:
                    clock_upper_bound = clock_lower_bound + 20
                grd_val = random.randint(0, clock_upper_bound)

                guard = dbm_op_gen.generate_constraint(clock1=clock, clock2=None, rel=">=", val=grd_val)
                guard.apply(self.dbm)
                self.sequence.append(guard)
                guard_count += 1

            if guard_count > 0:
                if not (len(self.sequence) > (self.sequence_length - 1)):
                    close = dbm_op_gen.generate_close()
                    close.apply(self.dbm)
                    self.sequence.append(close)

        if random.choice([True, False]):
            # Reset (only to 0 if non_zero_resets is False)
            clocks = random.sample(self.dbm.clocks[1:], random.randint(1, len(self.dbm.clocks[1:])))
            for clock in clocks:
                if len(self.sequence) > (self.sequence_length - 1):
                    break
                rst_val = random.randint(0, 10) if self.non_zero_resets else 0

                reset = dbm_op_gen.generate_reset(clock=clock, val=rst_val)
                reset.apply(self.dbm)
                self.sequence.append(reset)

    def _append_random_sequence_for_locations(self):
        """Appends a random sequence following the structure of an Uppaal location.

        Returns:
            None
        """
        if random.choice([True, False]):
            if not (len(self.sequence) > (self.sequence_length - 1)):
                # Delay future
                delay_future = dbm_op_gen.generate_delay_future()
                delay_future.apply(self.dbm)
                self.sequence.append(delay_future)

        if random.choice([True, False]):
            # Target location invariant
            clocks = random.sample(self.dbm.clocks[1:], random.randint(1, len(self.dbm.clocks[1:])))
            inv_count = 0
            for clock in clocks:
                if len(self.sequence) > (self.sequence_length - 2):
                    break

                clock_index = self.dbm.clocks.index(clock)
                clock_lower_bound = -self.dbm.matrix[0][clock_index].val
                clock_upper_bound = self.dbm.matrix[clock_index][0].val
                if clock_upper_bound == np.inf:
                    clock_upper_bound = clock_lower_bound + 20
                inv_val = random.randint(clock_lower_bound, clock_upper_bound)

                invariant = dbm_op_gen.generate_constraint(clock1=clock, clock2=None, rel="<=", val=inv_val)
                invariant.apply(self.dbm)
                self.sequence.append(invariant)
                inv_count += 1

            if inv_count > 0:
                if not (len(self.sequence) > (self.sequence_length - 1)):
                    close = dbm_op_gen.generate_close()
                    close.apply(self.dbm)
                    self.sequence.append(close)
