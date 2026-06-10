#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# In[6]:


def cross_entropy(data_p, data_q): 
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
     arr1 = data_p.to_numpy()
     arr2 = data_q.to_numpy()
     arr1 = arr1.astype('U21')
     arr2 = arr2.astype('U21')
     counts1, counts2 = data_counts(arr1,arr2) 
     prob1 = [x / len(arr1) for x in counts1]
     prob2 = [x / len(arr2) for x in counts2]
     entropy =0
     for i in range(len(prob1)):
         if prob2[i] == 0:
             entropy = entropy
         else:
             entropy = entropy - prob1[i]*np.log2(prob2[i])
     return(entropy)


# In[7]:


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

