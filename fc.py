#!/usr/bin/env python
# coding: utf-8

import arcpy
import HelperScript as helper

filePath = r"C:\Users\dangn\PycharmProjects\arcgisTest"
source_db_path = filePath + r"\webgisuser@csvgisds24s.sde"  # read only file
dest_db_path = filePath + r"\EGIS@GISDBcsvegisds1t.sde"  # write and read file
GIS_TEMP_FILE = dest_db_path + r"\Dest_temp_file"
# Log handler
errorLog = "log.txt"
needed_class = "LRS_RINV_Divided"
QUERYDEF = "(FromDate is null or FromDate<=CURRENT_TIMESTAMP) and (ToDate is null or ToDate>CURRENT_TIMESTAMP)"

sender = "CSVGISICS03@dot.state.al.us"
receiver = ["kohnkek@dot.state.al.us", "dangn@dot.state.al.us"]
subject = needed_class + " Update"

arcpy.env.workspace = dest_db_path
# Check if the feature class exists in the destination database
# If it does, then update it
# Else create a new one
featureClasses = arcpy.ListFeatureClasses()
dest_feature = None
for fc in featureClasses:
    if needed_class in fc:
        print("Found the feature class in the destination database")
        dest_feature = fc
        break

if dest_feature is None:
    with open(errorLog, 'a') as errorMsg:
        errorMsg.write("No feature class in the destination database")
    raise Exception("No feature class in the destination database")

target_feature = dest_db_path + r"/" + dest_feature

arcpy.env.workspace = source_db_path
# Check if the feature class exists in the source database
featureClasses = arcpy.ListFeatureClasses()
source_feature = None
for fc in featureClasses:
    if needed_class in fc:
        print("Found the feature class in the source database")
        source_feature = fc
        break

if source_feature is None:
    with open(errorLog, 'a') as errorMsg:
        errorMsg.write("No feature class in the source database")
    raise Exception("No feature class in the source database")

try:
    print("Deleting temp table")
    arcpy.Delete_management(GIS_TEMP_FILE)
    # Selection with query
    print("Selecting table attributes")
    arcpy.Select_analysis(source_feature, GIS_TEMP_FILE, QUERYDEF)
    print("Counting the selection")
    tempCount = arcpy.GetCount_management(GIS_TEMP_FILE)
    count = int(tempCount.getOutput(0))
    if count > 0:
        # Truncate the table of the destination feature class
        print("Truncating tables")
        arcpy.TruncateTable_management(target_feature)
        # Append the selection to the table at target database
        print("Appending the selection")
        arcpy.Append_management(GIS_TEMP_FILE, target_feature, "TEST")
        print("Deleting temp file")
        arcpy.Delete_management(GIS_TEMP_FILE)
        helper.send_email(sender, receiver, subject, needed_class + " Update was successful.")
    else:
        helper.send_email(sender, receiver, subject, "No update needed because count was 0")
except:
    # Check if any error occurred
    arcpy.AddMessage(arcpy.GetMessages(2))
    try:
        with open(errorLog, 'a') as errorMsg:
            errorMsg.write("%s,%s\n" % (errorLog, arcpy.GetMessages(2)))
    except RuntimeError:
        arcpy.AddMessage("Unable to log")
        arcpy.AddMessage(RuntimeError.message)
