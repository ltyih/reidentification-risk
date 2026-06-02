import numpy as np
import random

def bracket(low: int, high: int, interval: int) -> int:
    # Bracket defined by the lower bound for coding simplicity.
    # Example: If I'm looking at the brackets 0-4 and 5-9, then
    # these brackets are represented by 0 and 5, respectively.

    return np.random.uniform(low, high) // interval

# def generate_random_postcodes(n: int, )