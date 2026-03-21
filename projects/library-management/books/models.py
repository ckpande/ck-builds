from dataclasses import dataclass


@dataclass
class Book:
    bno:   int
    bname: str
    price: float
    pub:   str
