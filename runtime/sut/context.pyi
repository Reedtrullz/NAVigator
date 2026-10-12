import enum
from .phase2.contracts import Context

class StageState(enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    RECOVERABLE = "RECOVERABLE"
    TERMINAL = "TERMINAL"

STAGE_NAMES: tuple[str, ...]
def normalize_input(sut_input: object) -> object: ...
def make_context(sut_input: object) -> Context: ...
def mark_stage(ctx: Context, stage: str, state: StageState | str, message: str = "") -> None: ...
