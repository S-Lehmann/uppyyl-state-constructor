"""This module implements the DBM state constructor based on the OC approach."""

import time
from enum import Enum

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationSequence
)
from uppyyl_state_constructor.backend.dbm_constructor.oc.approximator.dbm_approximator_via_dbm import (
    DBMApproximatorViaDBM
)
from uppyyl_state_constructor.backend.dbm_constructor.oc.approximator.dbm_approximator_via_seq import (
    DBMApproximatorViaSeq
)
from uppyyl_state_constructor.backend.dbm_constructor.oc.constrainer.dbm_constrainer_via_fcs import (
    DBMConstrainerViaFCS
)
from uppyyl_state_constructor.backend.dbm_constructor.oc.constrainer.dbm_constrainer_via_mcs import (
    DBMConstrainerViaMCS
)
from uppyyl_state_constructor.backend.dbm_constructor.oc.constrainer.dbm_constrainer_via_rcs import (
    DBMConstrainerViaRCS
)


class ApproximationStrategy(Enum):
    """An enum of possible approximation strategies."""
    SEQ = 1  # Derived from source sequence
    DBM = 2  # Derived from DBM


class ConstraintStrategy(Enum):
    """An enum of possible constraining strategies."""
    FCS = 1  # Full Constraint System
    MCS = 2  # Minimal Constraint System
    RCS = 3  # Relative Constraint System


########################
# DBM Reconstructor OC #
########################
class DBMReconstructorOC:
    """A class for DBM state constructor based on the OC approach."""

    def __init__(self, dbm_init, on_the_fly=False):
        """Initializes DBMReconstructorOC.

        Args:
            dbm_init: The initial DBM.
        """
        # self.dbm_init = dbm_init
        self.dbm_target = None
        self.seq_source = None

        self.on_the_fly = on_the_fly

        self.approximation_strategy = None
        self.constraint_strategy = None

        self.seq_rec = None

        self.generators = {
            ApproximationStrategy.SEQ: DBMApproximatorViaSeq(dbm_init.clocks[1:]),
            ApproximationStrategy.DBM: DBMApproximatorViaDBM(),
            ConstraintStrategy.FCS: DBMConstrainerViaFCS(),
            ConstraintStrategy.MCS: DBMConstrainerViaMCS(),
            ConstraintStrategy.RCS: DBMConstrainerViaRCS()
        }

    def clear(self):
        """Clears the currently generated sequences.

        Returns:
            None
        """
        self.seq_rec = DBMOperationSequence()
        for generator in self.generators.values():
            generator.clear()

    # def update_sequence(self, incr_data):
    #     pass
    #
    # def generate_sequence(self, data):
    #     pass

    def time_measured_approximation(self, data_for_rec):
        """Performs the DBM approximation and measures the required times and sequence lengths.

        Args:
            data_for_rec: The observed data for reconstruction.

        Returns:
            The time measures.
        """
        if data_for_rec["dbm_init"] is None:
            raise Exception("")

        approximator = self.generators[self.approximation_strategy]

        # Get approx. sequence
        start_time = time.time()
        if self.on_the_fly:
            seq_approx = approximator.update_sequence(data=data_for_rec)
        else:
            seq_approx = approximator.generate_sequence(data=data_for_rec)
        seq_approx_gen_time = time.time() - start_time
        # Apply approx. sequence
        start_time = time.time()
        dbm_approx = seq_approx.apply(data_for_rec["dbm_init"].copy())
        seq_approx_app_time = time.time() - start_time

        measures = {
            "seq_approx_length": len(seq_approx),
            "seq_full_length": len(seq_approx),
            "seq_approx_gen_time": seq_approx_gen_time,
            "seq_approx_app_time": seq_approx_app_time,
            "full_gen_time": seq_approx_gen_time,
            "full_app_time": seq_approx_app_time,
            "full_time": seq_approx_gen_time + seq_approx_app_time,
        }

        return {
            "dbm_approx": dbm_approx,
            "seq_approx": seq_approx,
            "measures": measures
        }

    def time_measured_constraint(self, data_for_rec):
        """Performs the DBM constraining and measures the required times and sequence lengths.

        Args:
            data_for_rec: The observed data for reconstruction.

        Returns:
            The time measures.
        """
        # dbm_init = dbm_init if dbm_init else self.dbm_init
        if data_for_rec["dbm_init"] is None:
            raise Exception("")

        constrainer = self.generators[self.constraint_strategy]
        if self.constraint_strategy == ConstraintStrategy.RCS:
            constrainer.dbm_source = data_for_rec["dbm_init"].copy()

        # Get constr. sequence
        start_time = time.time()
        if self.on_the_fly:
            seq_constr = constrainer.update_sequence(data=data_for_rec)
        else:
            seq_constr = constrainer.generate_sequence(data=data_for_rec)
        seq_constr_gen_time = time.time() - start_time
        # Apply constr. sequence
        start_time = time.time()
        dbm_constr = seq_constr.apply(data_for_rec["dbm_init"].copy())
        seq_constr_app_time = time.time() - start_time

        measures = {
            "seq_constr_length": len(seq_constr),
            "seq_full_length": len(seq_constr),
            "seq_constr_gen_time": seq_constr_gen_time,
            "seq_constr_app_time": seq_constr_app_time,
            "full_gen_time": seq_constr_gen_time,
            "full_app_time": seq_constr_app_time,
            "full_time": seq_constr_gen_time + seq_constr_app_time,
        }

        return {
            "dbm_constr": dbm_constr,
            "seq_constr": seq_constr,
            "measures": measures
        }

    def time_measured_reconstruction(self, data_for_rec):
        """Performs the DBM state construction and measures the required times and sequence lengths.

        Args:
            data_for_rec: The observed data for reconstruction.

        Returns:
            The time measures.
        """
        if data_for_rec["dbm_init"] is None:
            raise Exception("")

        approx_data = self.time_measured_approximation(data_for_rec=data_for_rec)
        data_for_rec_constr = data_for_rec.copy()
        data_for_rec_constr["dbm_init"] = approx_data["dbm_approx"]
        constr_data = self.time_measured_constraint(data_for_rec=data_for_rec_constr)

        seq_rec = approx_data["seq_approx"] + constr_data["seq_constr"]
        dbm_rec = constr_data["dbm_constr"]

        measures = DBMReconstructorOC.calculate_full_measures(approx_data["measures"], constr_data["measures"])

        return {
            "dbm_rec": dbm_rec,
            "seq_rec": seq_rec,
            "seq_approx": approx_data["seq_approx"],
            "seq_constr": constr_data["seq_constr"],
            "measures": measures
        }

    @staticmethod
    def calculate_full_measures(approx_measures, constr_measures):
        """Calculates the overall construction measures based on the approximation and constraining measures.

        Args:
            approx_measures: The approximation measures.
            constr_measures: The constraining measures.

        Returns:
            The overall construction measures.
        """
        measures = {
            "seq_full_length": approx_measures["seq_approx_length"] + constr_measures["seq_constr_length"],
            "full_gen_time": approx_measures["seq_approx_gen_time"] + constr_measures["seq_constr_gen_time"],
            "full_app_time": approx_measures["seq_approx_app_time"] + constr_measures["seq_constr_app_time"],
            "full_time": approx_measures["full_time"] + constr_measures["full_time"],
        }
        return measures

    def set_strategies(self, approximation=None, constraint=None):
        """Sets the construction strategies.

        Args:
            approximation: The approximation strategy.
            constraint: The constraining strategy.
        """
        if approximation is not None:
            self.approximation_strategy = approximation
        if constraint is not None:
            self.constraint_strategy = constraint
