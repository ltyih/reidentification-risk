# K-Anonymity Version 1 Script Documentation

## Features
- Compute k-anonymity for a CSV dataset
- Calculate the minimum frequency of each quasi-identifier combination

## Usage
```bash
python k_anonymity.py --csv data.csv --columns age,gender,zipcode,etc.
```

## Advantages
- Column order in the CSV file does not matter
- If a column name is misspelled, the script will report: "Column XX not found"
- Supports UTF-8 encoded languages

## Limitations and Future Improvements
- Continuous variables require pre-processing (e.g., binning)
- Currently only supports CSV files
- Missing values are not handled properly; they are currently treated as a distinct category
- The script runs on the entire CSV dataset and cannot select a subset of rows for computation
- Only outputs the minimum k-value for each identifier combination, not the full frequency distribution across multiple combinations(changed in version 2)
- take up some GPU if applied to large dataset (eg. 30 million rows, 1000 columns).(faster calculation in version 3)
- need specify column names. if I have many variables, this is inconvenient. (can read all the columns automaticly in version 3)
