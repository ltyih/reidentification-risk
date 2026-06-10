#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd


# In[2]:


def discrimination_rate(dataframe, sensitive_col, identify_cols):
    #Currently only works if all the entries in the sensitive column are unique 
    df_sens = dataframe[sensitive_col]
    arr1 = df_sens.to_numpy()
    arr1 = arr1.astype('U21')
    df_iden = dataframe[identify_cols]
    arr2 = df_iden.to_numpy()
    arr2 = arr2.astype('U21')
    _, counts = np.unique(arr2, axis = 0, return_counts = True)
    co = counts.tolist()
    H_X = - np.log2(1/len(arr1))
    H_XY = 0
    for i in range(len(co)):
        H_XY = H_XY - co[i]/len(arr2)*np.log2(1/co[i])
    rate = 1 - H_XY/H_X
    return(rate)


# In[3]:


data = [
    ["Subject 1", 22,"4K", "Cancer", "35000", "M"],
    ["Subject 2", 35,"5K", "Diabetes", "35000", "M"],
    ["Subject 3", 63,"3K", "Malaria", "35000", "M"],
    ["Subject 4", 22,"13K", "Cancer", "35000", "F"],
    ["Subject 5", 22,"8K", "Cancer", "35000", "M"],
    ["Subject 6", 35,"15K", "Malaria", "35000", "F"],
    ["Subject 7", 45,"9K", "Malaria", "35000", "M"],
    ["Subject 8", 35,"7K", "Diabetes", "35000", "F"],
    ["Subject 9", 40,"11K", "Diabetes", "35000", "F"]
]


df = pd.DataFrame(data, columns=["Subject", "Age", "Salary", "Disease", "Zip_code", "Sex"])


# In[4]:


def DR_all_columns(dataframe, sensitive_column):
    temp = dataframe.drop(columns = sensitive_column)
    rates = []
    for col_name in temp.columns:
        rate = discrimination_rate(dataframe, sensitive_column, col_name)
        rates.append(rate)
    df = pd.DataFrame([rates], columns = temp.columns)
    return(df)


# In[5]:


DR_all_columns(df, ["Subject"])

