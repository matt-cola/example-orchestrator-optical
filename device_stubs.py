"""HAL-level device stubs for the example optical orchestrator.

The optical workflows drive real devices (FlexILS TL1/SSH, Groove G30 / GX G42
RESTCONF, TNMS TAPI) which do not exist in this test stack. When
``FAKE_DEVICES=True`` is set, this module replaces the HAL entry points with
the same fakes the orchestrator-optical DB-backed test suite uses
(``test/conftest.py``), so every shipped workflow family can be exercised end
to end through the real orchestrator-core process engine and the UI.

The stub targets mirror ``test/conftest.py::install_device_stubs``: HAL
functions are imported by name into each workflow module, so the patch must
target the importing module's attribute (the module whose globals perform the
lookup). The modules are imported eagerly here because the shipped workflows
are registered lazily and may not be imported yet when this runs.

This is test scaffolding in the user code-space, not module code: the module
itself keeps no fake logic. Keep in sync with ``test/conftest.py``.
"""

import importlib
import os
from collections.abc import Callable
from typing import Any

from orchestrator.optical.products.product_blocks.optical_node_management import Platform
from orchestrator.optical.products.product_blocks.optical_port.abstracts import OpticalPortRole

#: Port names offered by the faked client ports.
FAKE_CLIENT_PORTS = ("port-1/2/1",)
#: Port names offered by the faked line ports.
FAKE_LINE_PORTS = ("port-1/3.1/1.1",)  # G30 OLS-card port: contains a dot, so the spectrum path engine keeps it
#: All port names offered by the faked devices.
FAKE_ALL_PORTS = (*FAKE_CLIENT_PORTS, *FAKE_LINE_PORTS)
#: Transceiver modes offered by the faked devices.
FAKE_TRANSCEIVER_MODES = ("DP16QAM",)
#: Software version reported by the faked devices.
FAKE_SOFTWARE_VERSION = "1.0.0"


def _fake_retrieve_transceiver_modes(block: Any, port_name: str) -> list[str]:
    """Return the faked transceiver modes of a device port."""
    return list(FAKE_TRANSCEIVER_MODES)


def _fake_retrieve_ports_spectral_occupations(block: Any) -> dict[str, Any]:
    """Return no spectral occupations for the faked device ports."""
    return {}


def _fake_configure_termination_when_attaching_new_fiber(*args: Any) -> dict[str, Any]:
    """Configure the faked fiber terminating port, returning the configuration state."""
    return {}


def _fake_factory_reset_port_configuration(*args: Any) -> dict[str, Any]:
    """Factory reset the faked fiber terminating port, returning the reset state."""
    return {}


def _fake_check_fiber_terminating_port(*args: Any) -> None:
    """Accept the faked fiber terminating port as consistent."""


def _fake_set_port_description(port: Any, description: str) -> None:
    """Set the description of the faked port."""


def _fake_deploy_optical_circuit(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Deploy the faked optical circuit, returning the deployment state."""
    return {}


def _fake_modify_optical_circuit(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Modify the faked optical circuit, returning the modification state."""
    return {}


def _fake_delete_optical_circuit(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Delete the faked optical circuit, returning the deletion state."""
    return {}


def _fake_validate_optical_circuit(*args: Any, **kwargs: Any) -> None:
    """Accept the faked optical circuit as consistent."""


def _fake_get_signal_bandwidth(block: Any, port_name: str) -> int:
    """Return the faked signal bandwidth of a device port."""
    return 37500


def _fake_configure_line_transceivers(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Configure the faked line transceivers, returning the configuration state."""
    return {}


def _fake_configure_transceiver_client(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Configure the faked transceiver client, returning the configuration state."""
    return {}


def _fake_configure_transponder_crossconnect(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Configure the faked transponder crossconnect, returning the configuration state."""
    return {}


def _fake_delete_transponder_crossconnect(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Delete the faked transponder crossconnect, returning the deletion state."""
    return {}


def _fake_factory_reset_transponder_client(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Factory reset the faked transponder client, returning the reset state."""
    return {}


def _fake_factory_reset_transponder_lines(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Factory reset the faked transponder lines, returning the reset state."""
    return {}


def _fake_validate_trx_line(*args: Any, **kwargs: Any) -> None:
    """Accept the faked transponder line as consistent."""


def _fake_validate_trx_client(*args: Any, **kwargs: Any) -> None:
    """Accept the faked transponder client as consistent."""


def _fake_validate_trx_crossconnect(*args: Any, **kwargs: Any) -> None:
    """Accept the faked transponder crossconnect as consistent."""


def _fake_delta_rx_power_vs_target(*args: Any, **kwargs: Any) -> float:
    """Report the faked received power already aligned to its target."""
    return 0.0


def _fake_align_tx_power_to_target(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Align the faked transmitted power to its target, returning the alignment state."""
    return {}


def _fake_retrieve_optical_node_role_and_software_version(block: Any, *args: Any, **kwargs: Any) -> tuple[str, str]:
    """Return the faked node role and software version (shared retrieval step).

    The role is discovered from the device: FlexILS nodes are line systems
    (``ROADM``), while Groove G30 and GX G42 nodes are ``TRANSPONDER``.
    """
    if block.management.optical_module_node_platform == Platform.FLEXILS:
        return ("ROADM", FAKE_SOFTWARE_VERSION)
    return ("Transponder", FAKE_SOFTWARE_VERSION)


def _fake_retrieve_software_version(*args: Any, **kwargs: Any) -> str:
    """Return the faked node software version (vendor-dispatching HAL entry point)."""
    return FAKE_SOFTWARE_VERSION


def _fake_sleep(seconds: float) -> None:
    """Skip the faked power stabilization wait."""


# Port-list fakes bound to the module-level port overrides.
def _get_device_line_ports_names(block: Any) -> list[str]:
    """Return the faked line port names of a device."""
    return list(FAKE_LINE_PORTS)


def _get_device_client_ports_names(block: Any) -> list[str]:
    """Return the faked client port names of a device."""
    return list(FAKE_CLIENT_PORTS)


def _get_device_ports_names(block: Any) -> list[str]:
    """Return all faked port names of a device."""
    return list(FAKE_ALL_PORTS)


def _get_device_ports_by_role(block: Any, roles: Any = None) -> list[str]:
    """Return the faked port names of a device filtered by role.

    The seeded test nodes are Nokia FlexILS: OLS line ports are the line
    ports, OLS add/drop (tributary) ports are the client ports.
    """
    requested = roles if roles is not None else [OpticalPortRole.OLS_LINE, OpticalPortRole.OLS_ADD_DROP]
    names: list[str] = []
    for role in requested:
        if role is OpticalPortRole.OLS_LINE:
            names.extend(FAKE_LINE_PORTS)
        elif role is OpticalPortRole.OLS_ADD_DROP:
            names.extend(FAKE_CLIENT_PORTS)
    return list(dict.fromkeys(names))


def _retrieve_transceiver_modes(block: Any, port_name: str) -> list[str]:
    """Return the faked transceiver modes of a device port (ODS family)."""
    return list(FAKE_TRANSCEIVER_MODES)


#: Stub table: family -> module whose namespace performs the lookup -> attribute -> fake.
STUBS: dict[str, dict[str, dict[str, Callable[..., Any]]]] = {
    "node": {
        "orchestrator.optical.workflows.optical_node.shared.retrieve": {
            "_retrieve_optical_node_role_and_software_version": _fake_retrieve_optical_node_role_and_software_version,
        },
        # The node validate steps import the HAL dispatcher directly
        # (retrieve_software_version), so the patch target is their namespace.
        "orchestrator.optical.workflows.optical_node.shared.validate": {
            "retrieve_software_version": _fake_retrieve_software_version,
        },
    },
    "pipe": {
        "orchestrator.optical.workflows.optical_pipe.shared": {
            "check_fiber_terminating_port": _fake_check_fiber_terminating_port,
            "configure_termination_when_attaching_new_fiber": _fake_configure_termination_when_attaching_new_fiber,
            "get_device_ports_by_role": _get_device_ports_by_role,
            "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
        },
        "orchestrator.optical.workflows.optical_pipe.fiber_span.terminate": {
            "factory_reset_port_configuration": _fake_factory_reset_port_configuration,
        },
        "orchestrator.optical.workflows.optical_pipe.fiber_patch.terminate": {
            "factory_reset_port_configuration": _fake_factory_reset_port_configuration,
        },
        "orchestrator.optical.workflows.optical_pipe.leased_spectrum.terminate": {
            "factory_reset_port_configuration": _fake_factory_reset_port_configuration,
        },
    },
    "spectrum": {
        "orchestrator.optical.workflows.optical_spectrum_service.shared": {
            "get_device_client_ports_names": _get_device_client_ports_names,
            "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
        },
        "orchestrator.optical.workflows.optical_spectrum_service.create_optical_spectrum": {
            "set_port_description": _fake_set_port_description,
            "deploy_optical_circuit": _fake_deploy_optical_circuit,
        },
        "orchestrator.optical.workflows.optical_spectrum_service.modify_optical_spectrum": {
            "modify_optical_circuit": _fake_modify_optical_circuit,
        },
        "orchestrator.optical.workflows.optical_spectrum_service.terminate_optical_spectrum": {
            "delete_optical_circuit": _fake_delete_optical_circuit,
        },
        "orchestrator.optical.workflows.optical_spectrum_service.validate_optical_spectrum": {
            "validate_optical_circuit": _fake_validate_optical_circuit,
        },
    },
    "ods": {
        "orchestrator.optical.workflows.optical_spectrum_service.shared": {
            "get_device_client_ports_names": _get_device_client_ports_names,
            "retrieve_transceiver_modes": _retrieve_transceiver_modes,
            "retrieve_ports_spectral_occupations": _fake_retrieve_ports_spectral_occupations,
        },
        "orchestrator.optical.workflows.optical_digital_service.create_optical_digital_service": {
            "configure_line_transceivers": _fake_configure_line_transceivers,
            "configure_transceiver_client": _fake_configure_transceiver_client,
            "configure_transponder_crossconnect": _fake_configure_transponder_crossconnect,
            "get_signal_bandwidth": _fake_get_signal_bandwidth,
            "delta_rx_power_vs_target": _fake_delta_rx_power_vs_target,
            "align_tx_power_to_target": _fake_align_tx_power_to_target,
            "deploy_optical_circuit": _fake_deploy_optical_circuit,
            "sleep": _fake_sleep,
        },
        "orchestrator.optical.workflows.optical_digital_service.modify_optical_digital_service": {
            "get_signal_bandwidth": _fake_get_signal_bandwidth,
            "modify_optical_circuit": _fake_modify_optical_circuit,
            "sleep": _fake_sleep,
        },
        "orchestrator.optical.workflows.optical_digital_service.terminate_optical_digital_service": {
            "delete_transponder_crossconnect": _fake_delete_transponder_crossconnect,
            "factory_reset_transponder_client": _fake_factory_reset_transponder_client,
            "factory_reset_transponder_lines": _fake_factory_reset_transponder_lines,
            "delete_optical_circuit": _fake_delete_optical_circuit,
        },
        "orchestrator.optical.workflows.optical_digital_service.validate_optical_digital_service": {
            "get_signal_bandwidth": _fake_get_signal_bandwidth,
            "validate_trx_line": _fake_validate_trx_line,
            "validate_trx_client": _fake_validate_trx_client,
            "validate_trx_crossconnect": _fake_validate_trx_crossconnect,
            "validate_optical_circuit": _fake_validate_optical_circuit,
        },
    },
}


def install_device_stubs(families: list[str] | None = None) -> None:
    """Replace the HAL device entry points with the fakes of the given families.

    Args:
        families: Which families to stub; defaults to all of them. Unknown
            family names and missing stub targets fail loudly, so the fake
            device mode can never silently degrade to real device calls.
    """
    for family in families if families is not None else list(STUBS):
        if family not in STUBS:
            msg = f"Unknown device stub family {family!r}; expected one of {sorted(STUBS)}"
            raise ValueError(msg)
        for module_name, attributes in STUBS[family].items():
            module = importlib.import_module(module_name)
            for attribute, fake in attributes.items():
                if not hasattr(module, attribute):
                    msg = f"Device stub target {module_name}.{attribute} does not exist"
                    raise AttributeError(msg)
                setattr(module, attribute, fake)


def install_device_stubs_if_enabled() -> None:
    """Install the device stubs when ``FAKE_DEVICES`` is truthy; no-op otherwise."""
    if str(os.environ.get("FAKE_DEVICES", "")).lower() in ("1", "true", "yes"):
        install_device_stubs()
