#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This python script includes many helpful defs that can be utilized in other arcpy scripts in order
to cut down on redundant coding.
Version 1.0
Publication Date: 02/11/2021
Author Nam Dang, Intern - GIS Support - Computer Services - ALDOT
"""

import os
from os import path
import arcpy
import ast


def getCredential(file):
    # read account credential file
    f = open(file, "r")
    cred = f.read()
    # convert from str to dict
    cred = ast.literal_eval(cred)
    f.close()
    return cred


def createTempConnection(out_path: str, db_file: str, db_platform: str, instance: str, acc_auth: str,
                             username: str = None, password: str = None, database: str = None):
    # Establish a connection to CSVEGISDS01
    try:
        db_path = arcpy.CreateDatabaseConnection_management(out_path, db_file,
                                                           db_platform, instance,
                                                           acc_auth, database=database)
        print("Connects to the database successfully!")
    except Exception as genErr:
        print("General Error: {}".format(genErr))
        raise Exception(genErr)

    return db_path


def createFileGDB(out_path: str, out_name: str):
    # Create a new local geodatabase file if it's not existed
    try:
        geodb = arcpy.CreateFileGDB_management(out_path, out_name)
    except Exception as genErr:
        print("General Error: {}".format(genErr))
        raise Exception(genErr)

    return geodb


def copyFCtoFileGDB(geodb_path: str, fc_name: str, db_path: str, feature_class, out_feature_class: str):
    # Check if feature classes already existed and delete it
    # Set the environment to the FileGDB
    arcpy.env.workspace = str(geodb_path)

    if arcpy.Exists(fc_name):
        print("The Feature class exists")
        arcpy.Delete_management(fc_name)
    else:
        print("No Feature Classes in FileGDB, moving on...")
    print("FileGDB clean up complete.")

    # Copy a feature class to the local geodatabase
    # Set the environment to the database
    arcpy.env.workspace = str(db_path)
    try:
        arcpy.CopyFeatures_management(feature_class, out_feature_class)
        print("{} feature class was created!".format(fc_name))
    except Exception as genErr:
        print("General Error: {}".format(genErr))
        raise Exception(genErr)
