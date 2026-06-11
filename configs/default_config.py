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
        [
            cf.sample_country, 
            cf.sample_province, 
            partial(
                cf.sample_postcode,
                postal_list = ["T1Y", "T2A", "T2E", "T3J","T2K", "T2L", "T2M", "T2N", "T3A", "T3B",
                                "T3G", "T3L", "T3M", "T3N", "T2B", "T2C", "T2G", "T2H", "T2J", "T2M", 
                                "T2Z", "T3S", "T2P", "T2R", "T2S", "T2T", "T2V", "T2W", "T2X", "T3C", 
                                "T3E", "T3H", "T3K", "T4A", "T4B", "T1S", "T4C", "T1X", "T1P", "T1V", 
                                "T1W", "T1V"]
            )
        ],
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
        ["binary", "quadruple"],
        [
            partial(cf.distribute_sex, probability_female=0.5),
            partial(cf.sample_sex, weights = [0.45, 0.45, 0.09, 0.01])  # male, female, prefer not, non-binary
        ],
        "quadruple"
    ),

    Field(
        "conditions",
        ["binary", "ICD-10", "random_condition"],
        [
            partial(rand.uniform, probability = 0.5), 
            cf.sample_icd10, 
            partial(cf.sample_random_condition, prob_cond=0.5)
        ],
        "random_condition"
    ),

    Field(
        "smoker",
        ['binary'],
        [partial(cf.TrueFalse, probability = 0.12)],
        "binary"
    ),

    Field(
        "hbp",
        ["binary"],
        [partial(cf.TrueFalse, probability = 0.054)],
        "binary"
    )
]
