"""Workflow registration for the example optical orchestrator.

Registers every shipped workflow of the orchestrator-optical module with the
standard orchestrator-core mechanism (one ``LazyWorkflowInstance`` line per
workflow). The workflow names and import paths mirror the shipped workflows of
the module (discoverable via
``python -c "import orchestrator.optical.workflows"`` or the module README);
keep this list in sync when the module ships new workflows.
"""

from orchestrator.core.workflows import LazyWorkflowInstance

LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.create", "create_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.create", "create_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.create", "create_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.create", "create_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service", "create_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.create", "create_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.create", "create_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.create", "create_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.create", "create_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum", "create_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.modify", "modify_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.modify", "modify_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.modify", "modify_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.modify", "modify_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service", "modify_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.modify", "modify_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.modify", "modify_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.modify", "modify_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.modify", "modify_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum", "modify_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.reconcile", "reconcile_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.reconcile", "reconcile_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.reconcile", "reconcile_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate", "terminate_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.terminate", "terminate_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate", "terminate_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.terminate", "terminate_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.terminate_optical_digital_service", "terminate_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.terminate", "terminate_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.terminate", "terminate_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.terminate", "terminate_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.terminate", "terminate_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum", "terminate_optical_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_patch.validate", "validate_fiber_patch"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.fiber_span.validate", "validate_fiber_span"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_pipe.leased_spectrum.validate", "validate_leased_spectrum"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_coherent_pluggable.validate", "validate_optical_coherent_pluggable"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_digital_service.validate_optical_digital_service", "validate_optical_digital_service"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_location.validate", "validate_optical_module_location"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_flexils.validate", "validate_optical_node_nokia_flexils"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_groove_g30.validate", "validate_optical_node_nokia_groove_g30"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_node.nokia_gx_g42.validate", "validate_optical_node_nokia_gx_g42"),
LazyWorkflowInstance("orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum", "validate_optical_spectrum"),
