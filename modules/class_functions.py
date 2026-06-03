import numpy as np
import random
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_POSTAL_ADDRESS = ROOT / 'data' / 'postal_data.csv'


def uniform(n: int, low: int, high: int) -> list[int]:
    return np.floor(np.random.uniform(low, high, n)).astype(int)


def bracket(low: int, high: int, interval: int, n: int) -> int:
    # Bracket defined by the lower bound for coding simplicity.
    # Example: If I'm looking at the brackets 0-4 and 5-9, then
    # these brackets are represented by 0 and 5, respectively.

    return [np.random.uniform(low, high) // interval for _ in range(n)]


def sample_postcode(
        n: int, 
        postal_list: list[str] = [],
        data_csv: str = DEFAULT_POSTAL_ADDRESS
) -> list[str]:
    # generates n random postal codes from csv file, if postal_list is not included in argument, 
    # the postal codes will be generated from the full list of Canadian codes, otherwise they will be 
    # generated from the postal_list

    df = pd.read_csv(data_csv)
    if len(postal_list) != 0: 
        selected_df=df[df['GEO'].isin(postal_list)]
    else:
        selected_df = df
        
    postal_list = selected_df['GEO'].tolist()
    pop_list = selected_df['VALUE'].tolist()
    tot_pop = sum(pop_list)
    weight_list = [x / tot_pop for x in pop_list]
    results = random.choices(postal_list, weights=weight_list, k=n)

    return(results)


def sample_province(n):
    provinces = ["ON","QB","BC", "AB" , "MB", "SK", "NS", "NB", "NL", "PEI", "NWT", "YK", "NV"]
    weights = [0.3845, 0.2298, 0.1352, 0.1152, 0.0363, 0.0306,0.0262, 0.0209, 0.0138, 0.0042, 0.0011, 0.0011, 0.0010]
    results = random.choices(provinces, weights=weights, k=n)
    return(results)


def sample_country():
    return


def sample_icd10():
    return


def sample_random_condition(n:int) -> list[str]:
    # Generates n random ICD-10 Q codes/NA entries
    cond_list = ["Q00", "Q01","Q02","Q03","Q04","Q05","Q06","Q07",
            "Q10","Q11","Q12","Q13","Q14","Q15","Q16","Q17","Q18",
            "Q20","Q21","Q22","Q23","Q24","Q25","Q26","Q27","Q28",
            "Q30","Q31","Q32","Q33","Q34","Q35","Q36","Q37","Q38","Q39",
            "Q40","Q41","Q42","Q43","Q44","Q45",
            "Q50","Q51","Q52","Q53","Q54","Q55","Q56",
            "Q60","Q61","Q62","Q63","Q64","Q65","Q66","Q67","Q68","Q69",
            "Q70","Q71","Q72","Q73","Q74","Q75","Q76","Q77","Q78","Q79",
            "Q80","Q81","Q82","Q83","Q84","Q85","Q86","Q87","Q88","Q89",
            "Q90","Q91","Q92","Q93","Q94","Q95","Q96","Q97","Q98","Q99",
            "QA0"]
    num = len(cond_list)
    weight_list = [0.001]*num
    weight_list.append(1-0.001*90)
    cond_list.append("N/A")
    results = random.choices(cond_list, weights=weight_list, k=n)
    return(results)


def distribute_sex(n: int, probability_female: float = 0.5) -> list[str]:
    return ['female' if np.random.uniform() < probability_female else 'male' 
            for _ in range(n)]

# def generate_random_postcodes(n: int, )
