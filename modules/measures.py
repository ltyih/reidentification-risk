#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd



def entropy(dataframe, columns = []):
# Computes information entropy on one dataset, only includes the specified columns 
  df = dataframe
  if len(columns) != 0:
        df_subset = df[columns]
  else:
        df_subset = df
  array = df_subset.to_numpy()
  arr = array.astype('U21')
  _, counts = np.unique(arr, axis = 0,return_counts=True)    
  probabilities = counts / len(arr)
  dataset_entropy = -np.sum(probabilities * np.log2(probabilities))
  return(dataset_entropy)


def cross_entropy(data_p, data_q):
     #Drop all non-shared columns
     for col_name in data_p.columns:
         if col_name in data_q.columns:
             data_p = data_p
         else:
             data_p = data_p.drop(columns = col_name)
     for col_name in data_q.columns:
         if col_name in data_p.columns:
             data_q = data_q
         else: 
             data_q = data_q.drop(columns = col_name)
     #Convert to arrays
     arr1 = data_p.to_numpy()
     arr2 = data_q.to_numpy()
     arr1 = arr1.astype('U21')
     arr2 = arr2.astype('U21')
     # Compute entropy if p is the true distribution and q is the estimated distribution
     counts1, counts2 = data_counts(arr1,arr2) 
     prob1 = [x / len(arr1) for x in counts1]
     prob2 = [x / len(arr2) for x in counts2]
     entropy1 =0
     for i in range(len(prob1)):
         if prob2[i] == 0:
             # Ignore entries that clearly aren't in both datasets
             entropy1 = entropy1
         else:
             entropy1 = entropy1 - prob1[i]*np.log2(prob2[i])
     # Compute entropy if q is the true distribution and p is the estimated distribution
     counts1a, counts2a = data_counts(arr2,arr1) 
     prob1a = [x / len(arr2) for x in counts1a]
     prob2a = [x / len(arr1) for x in counts2a]
     entropy2 = 0 
     j = 0
     for i in range(len(prob1a)):
          if prob2a[i] == 0:
              # Ignore entries that clearly aren't in both datasets
              entropy2 = entropy2
          elif prob1a[i] == 0:
              entropy2 = entropy2
          else: 
              entropy2 = entropy2 - prob1a[i]*np.log2(prob2a[i])
              j = j + 1
     return(entropy1, entropy2, j)


def data_counts(data_array1, data_array2):
    entries1, counts1 = np.unique(data_array1, axis = 0, return_counts = True)
    ent1 = entries1.tolist()
    co1 = counts1.tolist()
    entries2, counts2 = np.unique(data_array2, axis = 0, return_counts = True)
    ent2 = entries2.tolist()
    co2 = counts2.tolist()
    co2_sorted = [None]*len(co1)
    for i in range(len(ent1)):
        if (ent1[i] in ent2) == True:
            j = ent2.index(ent1[i])
            co2_sorted[i] = co2[j]
        else:
            co2_sorted[i] = 0    
    return(co1, co2_sorted)


def discrimination_rate(dataframe, identify_cols):
    #Currently only works if all the entries in the sensitive column are unique 
    df_iden = dataframe[identify_cols]
    arr2 = df_iden.to_numpy()
    arr2 = arr2.astype('U21')
    _, counts = np.unique(arr2, axis = 0, return_counts = True)
    co = counts.tolist()
    H_X = - np.log2(1/len(arr2))
    H_XY = 0
    for i in range(len(co)):
        H_XY = H_XY - co[i]/len(arr2)*np.log2(1/co[i])
    rate = 1 - H_XY/H_X
    return(rate)



def DR_all_columns(dataframe):
    rates = []
    for col_name in dataframe.columns:
        rate = discrimination_rate(dataframe, col_name)
        rates.append(rate)
    df = pd.DataFrame([rates], columns = dataframe.columns)
    return(df)



def jiang(population_data, input_data):

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



