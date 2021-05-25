#!/usr/bin/env python
# coding: utf-8

# In[1]:


import arcpy
import os
from os import path
import pandas as pd
import HelperScriptArcpy as helper
import tempfile


# In[2]:


connectionPath = tempfile.TemporaryDirectory()


# In[3]:


db_path = helper.createTempConnection(connectionPath.name, "csvrhds01.sde", "SQL_SERVER", "csvrhds01",
                                      "OPERATING_SYSTEM_AUTH", database="EGISDB")


# In[4]:


arcpy.env.workspace = str(db_path)


# In[8]:


data = {}
df = pd.DataFrame(data, columns=['Feature Dataset Name', 'Feature Class Name'])
counter = 0


# In[6]:


featureDataset = arcpy.ListDatasets()
if len(featureDataset) > 0:
    for i in range(len(featureDataset)):
        # Reset environment
        arcpy.env.workspace = str(db_path)
        featureDataset = arcpy.ListDatasets()
        dataset = featureDataset[i]
        # Set a new environment
        arcpy.env.workspace = str(dataset)
        featureClasses = arcpy.ListFeatureClasses()
        for j in range(len(featureClasses)):
            if j == 0:
                df.loc[counter+j] = dataset, featureClasses[j]
            else:
                df.loc[counter+j] = "", featureClasses[j]
        counter = counter + len(featureClasses)
        # add the space at the end of each dataset
        df.loc[counter] = "", ""
        counter += 1


# In[9]:


arcpy.env.workspace = str(db_path)


# In[10]:


featureClasses = arcpy.ListFeatureClasses()
if len(featureClasses) > 0:
    for i in range(len(featureClasses)):
        if i == 0:
            df.loc[counter+i] = "Root", featureClasses[i]
        else:
            df.loc[counter+i] = "", featureClasses[i]
    counter = counter + len(featureClasses)


# In[13]:


filePath = r"C:/Users/dangn/PycharmProjects/arcgisTest"
outFile = filePath + r"/database1.csv"
df.to_csv(outFile)


# In[ ]:




