from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EnvParams:

    load_model: Optional[str] = None
    grid_resolution: float = 0.5

