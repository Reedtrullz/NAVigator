from .contracts import ProtocolDefinition
from .protocol import ProtocolLoader
from runtime.discovery_v2.contracts import RunInput

EXPECTED_PROTOCOL_SHA: str
def run_discovery(protocol: ProtocolDefinition | ProtocolLoader, input_data: RunInput,
                  fixtures: object = None, mode: str = "replay") -> object: ...
