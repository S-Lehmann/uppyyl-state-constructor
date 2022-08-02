"""This module contains the tests for the Uppaal model adaptor."""
import pprint

import pytest

from uppyyl_simulator.backend.ast.parsers.uppaal_xml_model_parser import uppaal_system_to_xml
from uppyyl_simulator.backend.data_structures.dbm.dbm import DBM
from uppyyl_simulator.backend.models.ta.nta_modifier import SystemModifier
from uppyyl_simulator.backend.simulator.simulator import Simulator
from uppyyl_state_constructor.backend.dbm_constructor.oc.dbm_constructor_oc import DBMReconstructorOC, \
    ApproximationStrategy, ConstraintStrategy
from uppyyl_state_constructor.backend.model_adaptor.model_adaptor import StateConstructionModelAdaptor

pp = pprint.PrettyPrinter(indent=4, compact=True)
printExpectedResults = False
printActualResults = False

test_model_path = "./res/uppaal_demo_models/2doors.xml"


###########
# General #
###########
@pytest.fixture
def simulator():
    """Creates and prepares a simulator object.

    Returns:
        The simulator object.
    """
    simulator = Simulator()
    simulator.load_system(test_model_path)
    return simulator


def test_insert_state_construction_template(simulator):
    print("")
    system = simulator.system

    # Convert all instances to separate templates (for later construction of each individual instance state)
    instance_data = simulator.system_state.instance_data
    SystemModifier.convert_instances_to_templates(
        system=system, instance_data=instance_data, keep_original_templates=False)
    simulator.set_system(system)

    # Generate initial DBM
    clocks = simulator.system_state.dbm_state.clocks[1:]
    dbm_init = DBM(clocks=clocks, zero_init=True)

    # Simulate n steps to obtain some sequence
    for i in range(0, 10):
        transition = simulator.simulate_step()
        print(transition.short_string())
    seq = simulator.get_sequence()
    dbm = simulator.system_state.dbm_state.copy()

    # Generate DBM construction sequence from simulated sequence
    dbm_constructor_oc = DBMReconstructorOC(dbm_init=dbm_init)
    dbm_constructor_oc.set_strategies(approximation=ApproximationStrategy.SEQ, constraint=ConstraintStrategy.FCS)
    res_csc = dbm_constructor_oc.time_measured_reconstruction(incr_data={"seq": seq, "dbm": dbm})
    seq_csc = res_csc["seq_rec"]
    print(seq_csc)

    # Insert the state construction template
    instance_data = simulator.system_state.instance_data
    loc_state = {inst_name: loc.id for inst_name, loc in simulator.system_state.location_state.items()}
    var_state = simulator.system_state.get_compact_variable_state()
    StateConstructionModelAdaptor.add_state_construction_components(
        system=system, seq=seq_csc, instance_data=instance_data, loc_state=loc_state, var_state=var_state)

    # Export the generated model
    output_model_xml = uppaal_system_to_xml(system=system)
    with open("./res/uppaal_demo_models/adapted.xml", "w") as file:
        file.write(output_model_xml)


def test_convert_instances_to_templates(simulator):
    system = simulator.system
    instance_data = simulator.system_state.instance_data
    SystemModifier.convert_instances_to_templates(
        system=system, instance_data=instance_data, keep_original_templates=False)

    output_model_xml = uppaal_system_to_xml(system=system)
    with open("./res/uppaal_demo_models/all_inst_to_tmpl.xml", "w") as file:
        file.write(output_model_xml)
