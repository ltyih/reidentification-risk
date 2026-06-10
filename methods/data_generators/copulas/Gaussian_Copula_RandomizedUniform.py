'''

Fxn Descriptions:
gaussian_copula: implements a Gaussian copula for data transformation and sampling 
categorical_to_gaussian_random: applies a Gaussian copula transformation to a dataframe of categorical variables to transform it to Gaussian space
gaussian_to_category: applies the inverse Gaussian copula transformation to transform data from Gaussian space back to categorical space
re_identification_risk: metric based on the frequency of records in the population data (Jiang 2022, Eq 2)

'''

import pandas as pd
import numpy as np
from scipy.stats import norm 

#Apply a Gaussian Copula to the input data to create synthetic identification and medical data sets; calculate the re-identification risk of the medical set
def gaussian_copula(input_data,quasi_identifiers_numeric,quasi_identifiers_categorical,num_samples_population): 

    '''
    input_data: path to the .csv file (assumption that this is medical data)
    quasi_identifiers_numeric: list of column names in the data that are numeric quasi-identifiers
    quasi_identifiers_categorical: list of column names in the data that are categorical quasi-identifiers
    num_samples_identification: number of samples to generate for the synthetic identification data
    num_samples_medical: number of samples to generate for the synthetic medical data
    '''


    #read the data from the .csv file
    input_data = pd.read_csv(input_data, usecols=quasi_identifiers_numeric + quasi_identifiers_categorical)
    input_data=input_data.head(10) #for testing--remove for final version
    print("Input Data:\n", input_data)

    #Separate numeric and categorical data
    data_numeric = input_data[quasi_identifiers_numeric]
    num_numeric_columns=len(quasi_identifiers_numeric)
    data_categorical = input_data[quasi_identifiers_categorical]
    num_category_columns=len(quasi_identifiers_categorical)
    

    #1: address numeric data
    numeric_info = {} #save rankings in a dictionary, as they will be used again
    for col in quasi_identifiers_numeric:
        numeric_info[col] = {"sorted_values": np.sort(data_numeric[col].values)}
    #Find the marginal distribution of each quasi_identifier_numeric column of the data using the empirical CDF
    marg_dis_numeric_quasi_identifiers = data_numeric.rank(method='average') / (len(data_numeric)+1) #Adding 1 in denom to avoid issues with 0 and 1 in the CDF (for large datasets this should not make much of a difference); so we won't have issues with  \pm inf when we apply the inverse CDF (probit function)

    #Transform numeric data to standard normal using the inverse CDF (probit function)
    transformed_data_numeric = norm.ppf(marg_dis_numeric_quasi_identifiers) #We are now in Gaussian space

    #2: address categorical data
    category_info = {} #Extract statistical info about each category and save in dictionary
    for col in quasi_identifiers_categorical:
        probs = (data_categorical[col].value_counts(normalize=True).sort_index()) #weighted probabilities of each item
        cumulative = probs.cumsum() #upper bd for Gaussian interval
        lower = cumulative.shift(fill_value=0) #lower bd for Gaussian interval
        category_info[col] = {"probs": probs,"lower": lower,"upper": cumulative}

    #Transform categorical data to Gaussian space using dictionary
    transformed_data_categorical=categorical_to_gaussian_random(quasi_identifiers_categorical, data_categorical, category_info, seed=None)

    #3: Combine transformed numeric and categorical data
    transformed_data = np.concatenate([transformed_data_numeric, transformed_data_categorical.values], axis=1)
    #print("Transformed Data:\n", transformed_data)

    #4: Calculate the correlation matrix of the transformed data
    corr_matrix = np.corrcoef(transformed_data, rowvar=False) #size = num_quasi_identiers x num_quasi_identiers
    #print("Correlation Matrix:\n", corr_matrix)

    #5: Create multivariate normal distribution with the correlation matrix and sample from it to create synthetic population data
    synthetic_population_data = np.random.multivariate_normal(mean=np.zeros(corr_matrix.shape[0]), cov=corr_matrix, size=num_samples_population) #size = num_samples_pop x num_quasi_identifiers

    #6: Apply the inverse CDF to convert the synthetic population data (now in Gaussian space) back to the original data space
    
    #numeric columns in synthetic_population_data to get back to the original data space
    numeric_synthetic_population_data=synthetic_population_data[:,0:num_numeric_columns]
    for i, col in enumerate(quasi_identifiers_numeric):
        u = norm.cdf(numeric_synthetic_population_data[:, i])
        numeric_synthetic_population_data[:, i] = np.quantile(numeric_info[col]["sorted_values"],u)
    numeric_synthetic_population_data=np.floor(numeric_synthetic_population_data) #THIS ROUNDING IS SPECIFIC FOR AGE, IDK GOOD GENERIC WAY TO DO THIS
    numeric_synthetic_population_data=pd.DataFrame(numeric_synthetic_population_data)
    #print("Numeric Synthetic Data:\n", numeric_synthetic_population_data)
        
    #categorical columns in synthetic_population_data to get back to the original data space
    categorical_synthetic_population_data=[]
    for j, col in enumerate(quasi_identifiers_categorical):
        categorical_synthetic_population_data.append(gaussian_to_category(synthetic_population_data[:, num_numeric_columns + j],category_info[col]))
    categorical_synthetic_population_data=pd.DataFrame(categorical_synthetic_population_data).T
    #print("Categorical Synthetic Data:\n", categorical_synthetic_population_data)

    #return to dataframes w proper column names
    synthetic_population_data = pd.concat([numeric_synthetic_population_data, categorical_synthetic_population_data], axis=1)
    synthetic_population_data.columns = quasi_identifiers_numeric + quasi_identifiers_categorical
    #print("All Synthetic Data:\n", synthetic_population_data)
    

    #7: Calculate re-identification risk of input data compared to syntheric population data
    re_id_risk = re_identification_risk(synthetic_population_data, input_data)

    return synthetic_population_data, re_id_risk

#Transform data_categorical to Gaussian space using statistical information saved in category_info
def categorical_to_gaussian_random(categories, data_categorical, category_info, seed=None):
    rng = np.random.default_rng(seed)

    #initialize
    transformed_data = pd.DataFrame(index=data_categorical.index,columns=categories,dtype=float)

    for col in categories: #for each category...
        stats = category_info[col] #extract stats
        for item in stats["probs"].index: #for each item in the category

            mask = data_categorical[col] == item

            lower = stats["lower"][item] #extract lower bd
            upper = stats["upper"][item] #extract upper bd

            u = rng.uniform(lower,upper,size=mask.sum()) #randomly generate values within bds

            transformed_data.loc[mask, col] = norm.ppf(u)

    return transformed_data


#Apply the inverse Gaussian copula transformation to transform data from Gaussian space back to categorical space
def gaussian_to_category(z, stats):

    u = norm.cdf(z) #convert to uniform interval [0,1]

    categories = [] #initialize column of categorical data

    for val in u: #for each value in u...
        for item, cutoff in stats["upper"].items():
            if val <= cutoff: #if the value is <= upper bound of item..
                categories.append(item) #record item
                break

    return np.array(categories)

#Re-Identification Risk Metric B (Jiang 2022): B=1/n * sum(1/F_i) where F_i is the frequency of the i-th record in the population data and n is the total number of unique records in the input data
def re_identification_risk(synthetic_population_data, input_data):

    # Get unique records from the original data
    unique_records = input_data.drop_duplicates()
    num_unique_records=len(unique_records)

    risks = []

    # Count frequency of each unique record in synthetic population
    for _, row in unique_records.iterrows():

        mask = (synthetic_population_data == row).all(axis=1)
        freq = mask.sum()

        # Avoid division by zero
        if freq > 0:
            risks.append(1 / freq)

    if len(risks) == 0:
        return 0.0
    
    re_id_risk=np.sum(risks)/num_unique_records #using this instead of np.mean bc a unique record in input might not exist in population (ie when freq=0)

    return re_id_risk


#Example usage:
quasi_identifiers_numeric=["age"]
#NUMERIC DATA IS ADDRESSED CONTINUOUSLY, THOUGH YOU MIGHT NOT WANT FINAL SYNTHETIC DATA TO BE 'CONTINUOUS'--will likely need to include additional rounding commands specific to data
quasi_identifiers_categorical=["sex","zip_code","education_level"]
input_data = "synthetic_data.csv"
num_samples_population=50 #Number of samples to generate for the synthetic identification data

#Run def
synthetic_population_data, re_id_risk= gaussian_copula(input_data,quasi_identifiers_numeric,quasi_identifiers_categorical,num_samples_population)

#Print outputs and other relevant info
# print("Medical Data:\n", input_data)
print("Synthetic Population Data:\n", synthetic_population_data)
print("Re-Identification Risk:", re_id_risk)