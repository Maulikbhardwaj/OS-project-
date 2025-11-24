from dataclasses import dataclass
from typing import Optional


@dataclass
class Process:
    name: str
    size: int


@dataclass
class Block:
    start: int  
    size: int  
    free: bool = True   
    tag: Optional[str] = None  

    @property
    def end(self) -> int:
        return self.start + self.size
