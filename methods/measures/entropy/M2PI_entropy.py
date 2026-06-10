#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# In[2]:


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

