"""This module implements the DBM state constructor based on the Trivial approach."""

import time

from uppyyl_simulator.backend.data_structures.dbm.dbm_operations.dbm_operations import (
    DBMOperationSequence
)


#############################
# DBM Reconstructor Trivial #
#############################
class DBMReconstructorTrivial:
    """A class for DBM state constructor based on the Trivial approach."""
    def __init__(self, on_the_fly=False):
        """Initializes DBMReconstructorTrivial.

        Args:
            dbm_init: The initial DBM.
        """
        # self.dbm_init = dbm_init
        self.seq_rec = None
        self.on_the_fly = on_the_fly

        self.clear()

    def clear(self):
        """Clears the currently generated sequence.

        Returns:
            None
        """
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
        self.seq_rec += data["seq_incr"]
        return self.seq_rec

    def generate_sequence(self, data):
        """Generates the construction sequence based on given sequence data.

        Args:
            data: The observed sequence and DBM data.

        Returns:
            The construction sequence.
        """
        if self.seq_rec is None:
            raise Exception("Reconstruction sequence must be defined before it is updated.")
        self.seq_rec = data["seq_full"].copy()
        return self.seq_rec

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
