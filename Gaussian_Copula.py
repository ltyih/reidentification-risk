'''

Fxn Descriptions:
gaussian_copula:  implements a Gaussian copula for data transformation and sampling 
re_identification_risk: metric based on the frequency of records in the population data

'''

import pandas as pd
import numpy as np
from scipy.stats import norm 
#from statsmodels.distributions.empirical_distribution import ECDF  

#Apply a Gaussian Copula to the input data to create synthetic identification and medical data sets; calculate the re-identification risk of the medical set
def gaussian_copula(input_data,quasi_identifiers,quasi_identifiers_need_maps,num_samples_identification,num_samples_medical): 

    '''
    input_data: path to the .csv file
    quasi_identifiers: list of column names in the data that are quasi-identifiers
    quasi_identifiers_need_maps: list of quasi-identifiers that need an integer mapping (e.g. categorical variables)
    num_samples_identification: number of samples to generate for the synthetic identification data
    num_samples_medical: number of samples to generate for the synthetic medical data
    '''


    #read the data from the .csv file
    data = pd.read_csv(input_data, usecols=quasi_identifiers)
    #data=data.head(10000) #for testing--remove for final version

    #create list of integer (inverse) mappings for categorical variables that need them
    mappings = [] #create mappings to turn categorical/discrete variables into integers
    inverse_mappings = [] #create inverse mapping to get back to original values later
    for col in quasi_identifiers_need_maps:
        unique_values = data[col].unique()
        mapping = {value: i for i, value in enumerate(unique_values)}
        data[col] = data[col].map(mapping)
        mappings.append(mapping)
        inverse_mapping = {v: k for k, v in mapping.items()} 
        inverse_mappings.append(inverse_mapping)

    #Calculate the correlation matrix of the input data
    corr_matrix = np.corrcoef(data, rowvar=False) #size = num_quasi_identiers x num_quasi_identiers

    #Find the marginal distribution of each column of the data using the empirical CDF
    marg_dis_columns = data.rank(method='average') / (len(data)+.1) #maybe +1? Adding a small constant to avoid issues with 0 and 1 in the CDF
    #each of the above should sum to 1--add as safe guard
    #Transform the data to standard normal using the inverse CDF (probit function)
    transformed_data = norm.ppf(marg_dis_columns) #We are now in Gaussian space

    #Create multivariate normal distribution with the correlation matrix and sample from it to create synthetic population data
    synthetic_id_data = np.random.multivariate_normal(mean=np.zeros(corr_matrix.shape[0]), cov=corr_matrix, size=num_samples_identification) #size = num_samples_pop x num_quasi_identifiers

    #Apply the inverse CDF to synthetic_id_data to get back to the original data space
    for i in range(transformed_data.shape[1]):
        synthetic_id_data[:, i] = np.interp(synthetic_id_data[:, i], np.sort(transformed_data[:, i]), np.sort(data.iloc[:, i]))


    #Round the synthetic population data to the nearest integer (since the original data is discrete)
    synthetic_id_data = np.round(synthetic_id_data)

    #Take sub-sample of the synthetic population data to create the synthetic medical data
    synthetic_med_data = synthetic_id_data[:num_samples_medical]

    re_id_risk = re_identification_risk(synthetic_id_data, synthetic_med_data)

    #return to dataframes
    synthetic_id_data = pd.DataFrame(synthetic_id_data, columns=data.columns)
    synthetic_med_data = pd.DataFrame(synthetic_med_data, columns=data.columns)

    synthetic_id_data.columns = quasi_identifiers
    synthetic_med_data.columns= quasi_identifiers

    #apply inverse integer mappings to get back to original categorical values
    for i, col in enumerate(quasi_identifiers_need_maps):
        synthetic_id_data[col] = synthetic_id_data[col].map(inverse_mappings[i])
        synthetic_med_data[col] = synthetic_med_data[col].map(inverse_mappings[i])
    
    return synthetic_id_data, synthetic_med_data, re_id_risk

#Re-Identification Risk Metric B (Jiang 2022): B=1/n * sum(1/F_i) where F_i is the frequency of the i-th record in the population data and n is the total number of records in the sampled data.
def re_identification_risk(synthetic_id_data, synthetic_med_data):

    #Find the unique rows in synthetic_med_data
    unique_rows= np.unique(synthetic_med_data, axis=0)
    num_unique_records=len(unique_rows)

    #Find the frequency of each unique record in synthetic_id_data
    freqs = np.zeros(num_unique_records)
    for i in range(num_unique_records):
        count = np.sum(np.all(synthetic_id_data == unique_rows[i], axis=1))
        freqs[i] = count

    #Calculate the re-identification risk for each record in the sampled data
    re_id_risk = sum(1/f for f in freqs) / num_unique_records

    return re_id_risk


#Example usage:
quasi_identifiers=["age", "sex","zip_code","education_level"]
quasi_identifiers_need_maps=["sex","zip_code","education_level"] 
input_data = "synthetic_data.csv"
num_samples_identification=1000 #Number of samples to generate for the synthetic identification data
num_samples_medical=100 #Number of samples to generate for the synthetic medical data

#Run def
synthetic_id_data, synthetic_med_data, re_id_risk = gaussian_copula(input_data,quasi_identifiers,quasi_identifiers_need_maps,num_samples_identification,num_samples_medical)

#Print outputs
#print("Synthetic Identification Data:\n", synthetic_id_data)
#print("Synthetic Medical Data:\n", synthetic_med_data)
print("Re-Identification Risk:", re_id_risk)