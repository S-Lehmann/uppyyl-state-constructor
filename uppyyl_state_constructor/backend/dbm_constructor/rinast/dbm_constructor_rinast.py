"""This module implements the DBM state constructor based on the Rinast approach."""

import time

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationGenerator, DBMOperationSequence, Reset, Constraint, DelayFuture, Close
)
from uppyyl_state_constructor.backend.dbm_constructor.rinast.dbm.db_value import (
    DBValue
)
from uppyyl_state_constructor.backend.dbm_constructor.rinast.trans.transformation_info import (
    Type
)
from uppyyl_state_constructor.backend.dbm_constructor.rinast.uppaal.ta_system import (
    TASystem
)


def split_full_clock_name(full_clock_name):
    """Splits a full clock name into its instance and name.

    Args:
        full_clock_name: The full clock name ("inst.clock").

    Returns:
        The instance and clock name.
    """
    parts = full_clock_name.split(".")
    if len(parts) == 1:
        instance = None
        name = parts[0]
    elif len(parts) >= 2:
        instance = parts[0]
        name = parts[1]
    else:
        raise Exception(f'Clock name "{full_clock_name}" cannot be parsed.')
    return instance, name


############################
# DBM Reconstructor Rinast #
############################
class DBMReconstructorRinast:
    """A class for DBM state constructor based on the Rinast approach."""

    def __init__(self, clock_names, var_names, on_the_fly=False):
        """Initializes DBMReconstructorRinast.

        Args:
            dbm_init: The initial DBM.
            clock_names: A list of all system clock names
                         (Note: The clock list should already contain the artificial reference clock TO_REF).
            var_names: A list of all system variable names.
        """
        # self.dbm_init = dbm_init
        self.clock_names = clock_names
        self.var_names = var_names

        self.on_the_fly = on_the_fly

        # self.seq_source = None
        self.ta_system = None
        self.seq_rec = None

        self.clear()

    def clear(self):
        """Clears the currently generated sequence.

        Returns:
            None
        """
        self.ta_system = TASystem(clock_names=self.clock_names, var_names=self.var_names)
        self.seq_rec = DBMOperationSequence()

    def update_sequence(self, data):
        """Updates the construction sequence based on a given data observation increment.

        Args:
            data: The data of the observation increment.

        Returns:
            The updated construction sequence.
        """
        if self.seq_rec is None:
            raise Exception("Reconstruction sequence must be defined before it is updated.")
        self._append_sequence_to_ta_system(data["seq_incr"])
        self.seq_rec = self._generate_sequence_from_ta_system_path()
        return self.seq_rec

    def generate_sequence(self, data):
        """Generates the construction sequence based on given sequence data.

        Args:
            data: The observed sequence and DBM data.

        Returns:
            The construction sequence.
        """
        # if self.seq_source is None:
        if data["seq_full"] is None:
            raise Exception(f'A source sequence is required by DBMReconstructorRinast.')
        self.ta_system = TASystem(clock_names=self.clock_names, var_names=self.var_names)
        self._append_sequence_to_ta_system(data["seq_full"])
        seq = self._generate_sequence_from_ta_system_path()
        return seq

    def time_measured_reconstruction(self, data_for_rec):
        """Performs the DBM state construction and measures the required times and sequence lengths.

        Args:
            data_for_rec: The observed data for reconstruction.

        Returns:
            The time measures.
        """
        if data_for_rec["dbm_init"] is None:
            raise Exception("")

        # Get rec. sequence
        start_time = time.time()
        if self.on_the_fly:
            seq_rec = self.update_sequence(data=data_for_rec)
        else:
            seq_rec = self.generate_sequence(data=data_for_rec)
        seq_rec_gen_time = time.time() - start_time
        # Apply rec. sequence
        start_time = time.time()
        dbm_rec = seq_rec.apply(data_for_rec["dbm_init"].copy())
        seq_rec_app_time = time.time() - start_time

        measures = {
            "seq_full_length": len(seq_rec),
            "full_gen_time": seq_rec_gen_time,
            "full_app_time": seq_rec_app_time,
            "full_time": seq_rec_gen_time + seq_rec_app_time,
        }

        return {
            "dbm_rec": dbm_rec,
            "seq_rec": seq_rec,
            "measures": measures
        }

    def _append_sequence_to_ta_system(self, seq):
        """Appends an operation sequence to the internal TA system.

        Args:
            seq: The operation sequence.

        Returns:
            None
        """
        dbm_system = self.ta_system.dbm_system
        for operation in seq:
            if isinstance(operation, Reset):
                clock_inst, clock_name = split_full_clock_name(operation.clock)
                clock = self.ta_system.get_clock(instance=clock_inst, name=clock_name)
                val = operation.val

                reset_transf = dbm_system.get_reset_transformation(clock.get_value(), val)
                dbm_system.apply_transformation(reset_transf)

            elif isinstance(operation, Constraint):  # Expects Constraint operation to be in "<=" form
                clock1_inst, clock1_name = split_full_clock_name(operation.clock1) if (
                            operation.clock1 is not None) else (None, None)
                clock1 = self.ta_system.get_clock(instance=clock1_inst, name=clock1_name)
                clock2_inst, clock2_name = split_full_clock_name(operation.clock2) if (
                            operation.clock2 is not None) else (None, None)
                clock2 = self.ta_system.get_clock(instance=clock2_inst, name=clock2_name)
                bound = "=" in operation.rel
                val = operation.val

                constr_transf = dbm_system.get_constraint_transformation(clock1.get_value(), clock2.get_value(),
                                                                         DBValue(value=val, bound=bound))
                dbm_system.apply_transformation(constr_transf)

            elif isinstance(operation, DelayFuture):
                df_transf = dbm_system.get_up_transformation()
                dbm_system.apply_transformation(df_transf)

            elif isinstance(operation, Close):
                pass

            else:
                raise Exception(f'Operation of type "{type(operation)}" is not supported.')

    def _generate_sequence_from_ta_system_path(self):
        """Generate an operation sequence form the generated path data of the interval TA system.

        Returns:
            The generated operation sequence.
        """
        path = self.ta_system.dbm_system.get_transformation_system().get_reduced_path()
        dbm_op_gen = DBMOperationGenerator()
        op_seq = DBMOperationSequence()
        close_needed = False

        for trans in path:
            info = trans.get_info()
            # Add close operation after a sequence of constraint operations
            if (info.type != Type.Constraint) and close_needed:
                close = dbm_op_gen.generate_close()
                op_seq.append(close)
                close_needed = False

            if info.type == Type.Up:
                delay_future = dbm_op_gen.generate_delay_future()
                op_seq.append(delay_future)
            elif info.type == Type.Urgent:
                pass
            elif info.type == Type.Reset:
                clock = self.ta_system.clocks[info.clock1].get_full_name()
                val = info.value.value

                reset = dbm_op_gen.generate_reset(clock=clock, val=val)
                op_seq.append(reset)

            elif info.type == Type.Constraint:
                clock1_name = self.ta_system.clocks[info.clock1].get_full_name()
                clock1 = None if clock1_name == "t(0)" else clock1_name
                clock2_name = self.ta_system.clocks[info.clock2].get_full_name()
                clock2 = None if clock2_name == "t(0)" else clock2_name
                rel = "<=" if info.value.bound else "<"
                val = info.value.value

                constr = dbm_op_gen.generate_constraint(clock1=clock1, clock2=clock2, rel=rel, val=val)
                op_seq.append(constr)

                close_needed = True

        # Final close, if needed
        if close_needed:
            close = dbm_op_gen.generate_close()
            op_seq.append(close)

        return op_seq
