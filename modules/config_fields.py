from dataclasses import dataclass
from functools import partial
import numpy.random as rand
import class_functions as cf

@dataclass
class Field:
    name = str
    options: list[str]
    functions: list
    choice: str | None = None
    distribution: str | None = None
    mean: float | None = None
    std: float | None = None

fields = [
    Field(
        name = "address",
        options = ["country", "province", "postcode"],
        functions = [cf.sample_country, cf.sample_province, cf.sample_postcode],
        choice = "postcode"
    ),

    Field(
        name = "age",
        options = ["bracket", "year", "month"],
        functions = [
            partial(cf.bracket, low = 0, high = 25, interval = 5),
            partial(rand.uniform, 0, 25),
            partial(rand.uniform, 0, 24 * 12)
        ],
        choice = "year"
    ),

    Field(
        name = "conditions",
        options = ["binary", "ICD-10"],
        functions = [partial(rand.uniform, probability = 0.5), cf.sample_icd10],
        choice = "binary"
    )
]
