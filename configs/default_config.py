from dataclasses import dataclass
from functools import partial
import numpy.random as rand
import modules.class_functions as cf

@dataclass
class Field:
    name: str           # Name of the column/information type
    options: list[str]  # Options for level of detail of information
    functions: list     # Functions associated with each options, in same order (should I make it a dictionary?)
    choice: str         # Choice of detail level from `options`

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
            partial(cf.uniform, low = 0, high = 25),
            partial(cf.uniform, low = 0, high = 24 * 12)
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
