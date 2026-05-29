**Quantifying Re-Identification Risk in Child Health Data**

**Proposed by:** The One Child Every Child (OCEC) Data Accelerator

Project Summary
===============

This project examines how re-identification risk varies within datasets, particularly for individuals with unique or complex diagnostic profiles, and identifies factors beyond average sample-level risk that contribute to vulnerability. It aims to assess how data type, dataset structure, and existing safeguards influence re-identification risk, with a focus on informing responsible data sharing practices for research involving children with complex diagnoses.

Introduction
------------

Re-identification risk is disproportionately shouldered by individuals with unique data profiles (i.e., outliers), including children with complex diagnostic profiles. There is also limited literature on the factors that might influence re-identification risk beyond the risk to the whole sample on average.

With the increase in requirements for data sharing, it is important to understand re-identification risk within a sample, but also the re-identification risk of individuals who are unique. Considerations should be made that there are some risks that are not within the control of researchers (e.g., knowing whether someone is in a study or not; a family might willingly share this information). Thus, extra consideration should be made for those things that can be controlled by the research team while appreciating the importance of data sharing and utilization of research data.

GOAL
----

The goal of this study is to determine factors contributing to re-identification risk in large datasets and their impact on children with complex diagnostic profiles.

Aim 1
-----

What kind of data is at risk for re-identification and what recommendations have been made within the literature?

With the utilization of publicly available data to train AI models, it is becoming increasingly important for researchers to clearly communicate to research participants how their data will be used and the risk associated with data sharing. The first aim of this study will look at the existing literature and assess the recommendations that have been made to limit re-identification risk in research data. This aim will also address the existing literature that has evaluated re-identification risk in specific types of data and the differences in recommendations based on data type (i.e., MRI, genetic, behavioural, etc.).

Aim 2
-----

How does the shape of the data influence re-identification risk within a randomly generated sample and is this comparable to a sample generated based on known variable relationships?

### Aim 2.1

What factors contribute to greater re-identification risk in a sample of randomly generated data Assuming that re-identification risk is influenced by several factors including

1.  the number of possible combinations of variables (# of possible unique ‘profiles’)
2.  the size of the sample
3.  the variability of each of the variables (i.e., how likely are there to be outliers, especially ’extreme’ outliers), and
4.  the number of shared variables which could be considered identifiable.

The shape of the dataset could influence re-identification risk and by understanding the relationship between the shape of the dataset and re-identification risk we can determine the risk level of data sharing. Particularly for individuals who might have ‘unique’ data profiles which might be more likely to be re-identified.

### Aim 2.2

Does a sample that is based on known variable relationships (co-occurrence between neurodevelopmental disorders) behave the same way as a fully synthetic dataset?

One use case where re-identification risk is of particular concern in within populations of children with unique diagnostic profiles (unique combinations of diagnoses). Given the high rate of co-occurrence in these disorders, it is common for a child to present with multiple diagnoses. Determine the co-occurrence rates for several neurodevelopmental disorders (Autism, ADHD, OCD, CD, ODD, etc.)

Project Folder
==============

Folder Structure
----------------

M2PI/

|---README.docx

|----code/

| |---generate\_dataset.py

|---data/

| |---synthetic\_data.csv

|---literature/

File/Folder Descriptions
------------------------

**File/Folder Name**

**Description**

README.docx

This file which includes information about the project and any supporting information on how to interpret the data within the dataset. This document should be updated when new datasets, folders, or files are added to the project folder.

Code/

This folder contains any code generated for the project, if there is additional code generated that exists elsewhere (i.e., git) the link should be included here.

generate\_dataset.py

Python code block to create the fake dataset

Data/

Folder where all the datasets will be stored

Synthetic\_data.csv

Output from generate\_dataset.py

Literature/

Folder containing some seminal literature for context around the project – I have provided a summary within this folder on the papers that are included within the folder (literature/summary.docx)

Summary.docx

Summary on the papers that were selected for context