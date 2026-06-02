from dataclasses import dataclass
from functools import partial
import numpy.random as rand
import class_functions as cf

@dataclass
class Field:
    name: str
    options: list[str]
    functions: list
    choice: str | None = None
    distribution: str | None = None
    mean: float | None = None
    std: float | None = None

fields = [
    Field(
        "address",
        ["country", "province", "postcode"],
        [cf.sample_country, cf.sample_province, cf.sample_postcode],
        "postcode"
    ),

    Field(
        "age",
        ["bracket", "year", "month"],
        [
            partial(cf.bracket, low = 0, high = 25, interval = 5),
            partial(rand.uniform, 0, 25),
            partial(rand.uniform, 0, 24 * 12)
        ],
        "year"
    ),

    Field(
        "sex",
        ["binary"],
        [partial(cf.distribute_sex, probability_female=0.5)],
        "binary"
    ),

    Field(
        "conditions",
        ["binary", "ICD-10", "random_condition"],
        [
            partial(rand.uniform, probability = 0.5), 
            cf.sample_icd10, 
            cf.sample_random_condition
        ],
        "random_condition"
    )
]
