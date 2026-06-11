'''

Fxn Description:
re_identification_risk: metric based on the frequency of records in the population data (Jiang 2022, Eq 2)

'''


import pandas as pd
import numpy as np
from scipy.stats import norm 

#Re-Identification Risk Metric B (Jiang 2022): B=1/n * sum(1/F_i) where F_i is the frequency of the i-th record in the population data and n is the total number of records in the input data (i.e. number of rows/ppl)
def re_identification_risk(population_data, input_data):

    population_data = population_data[input_data.columns]

    num_records=len(input_data)
    risks = []

    # Count frequency of each medical data record in synthetic population
    for _, row in input_data.iterrows():

        mask = (population_data == row).all(axis=1)
        freq = mask.sum()

        # Avoid division by zero
        if freq > 0:
            risks.append(1 / freq)

    if len(risks) == 0:
        return 0.0
    
    re_id_risk=np.sum(risks)/num_records #using this instead of np.mean bc a unique record in input might not exist in population (ie when freq=0)

    return re_id_risk