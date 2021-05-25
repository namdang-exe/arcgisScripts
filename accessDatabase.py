#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a script that gets all feature datasets from a database and their feature classes and exports them into
a .csv file
Version 1.0
Publication Date: 02/18/2021
Author: Nam Dang, Intern - GIS/ Programming Support - Computer Services - ALDOT
"""

import arcpy
import pandas as pd
import os

# Set path to the database
filePath = r"C:/Users/dangn/PycharmProjects/arcgisTest"
out_db1 = "csvegisds1t.sde"
# Set .csv output file
outfile = filePath + r"/database.csv"
# Set the environment to the database
arcpy.env.workspace = str(out_db1)
# Create a data frame to store feature datasets and its feature classes
data = {}
df = pd.DataFrame(data, columns=['Feature Dataset Name', 'Feature Class Name'])
counter = 0  # this counter will keep track of the position of the last dataset
# Get the datasets
featureDataset1 = arcpy.ListDatasets()
for i in range(len(featureDataset1)):
    # Reset the current environment
    arcpy.env.workspace = str(out_db1)
    featureDataset1 = arcpy.ListDatasets()
    dataset = featureDataset1[i]
    # Set a new environment
    arcpy.env.workspace = str(dataset)
    featureClasses = arcpy.ListFeatureClasses()
    for j in range(len(featureClasses)):
        if j == 0:
            df.loc[counter + j] = dataset, featureClasses[j]
        else:
            df.loc[counter + j] = "", featureClasses[j]
    counter = counter + len(featureClasses)
    if i != len(featureDataset1) - 1:
        df.loc[counter] = "", ""
        counter += 1

df.to_csv(outfile)
# remove the database connection
# os.remove(str(out_db1))
# os.remove(str(out_db2))
