import numpy as np
import random
import pandas as pd

def bracket(low: int, high: int, interval: int) -> int:
    # Bracket defined by the lower bound for coding simplicity.
    # Example: If I'm looking at the brackets 0-4 and 5-9, then
    # these brackets are represented by 0 and 5, respectively.

    return np.random.uniform(low, high) // interval

# generates n random postal codes from csv file, if postal_list is not included in argument, 
# the postal codes will be generated from the full list of Canadian codes, otherwise they will be 
# generated from the postal_list
def postal_data(data_csv, n, postal_list= []):
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

# Generates n random ICD-10 Q codes/NA entries
def condition(n):
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
