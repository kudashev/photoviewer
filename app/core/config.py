from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    input_root: Path
    cache_root: Path

