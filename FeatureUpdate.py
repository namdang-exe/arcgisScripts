#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
from os import path

import arcpy

import HelperScript as Helper


def feature_update():
    ############ Change this to reuse this script
    filePath = path.abspath(os.getcwd())
    needed_class = str(sys.argv[1])

    source_db_path = path.join(filePath, "webgisuser@csvgisds24s.sde")  # read only file
    dest_db_path = path.join(filePath, "EGIS@GISDBcsvegisds1t.sde")  # write and read file
    GIS_TEMP_FILE = path.join(dest_db_path, "Dest_temp_file")
    # Log handler
    errorLog = path.join(filePath, "logs", "log.txt")

    QUERYDEF = "(FromDate is null or FromDate<=CURRENT_TIMESTAMP) and (ToDate is null or ToDate>CURRENT_TIMESTAMP)"

    sender = "CSVGISICS03@dot.state.al.us"
    receiver = ["kohnkek@dot.state.al.us", "dangn@dot.state.al.us"]
    subject = "{} Update".format(needed_class)

    arcpy.env.workspace = dest_db_path
    # Check if the feature class exists in the destination database
    # If it does, then update it
    # Else create a new one
    featureClasses = arcpy.ListFeatureClasses()
    print(len(featureClasses))
    target_feature = None
    for fc in featureClasses:
        if needed_class in fc:
            print("Found the feature class in the destination database")
            target_feature = path.join(dest_db_path, fc)
            break

    if target_feature is None:
        with open(errorLog, 'a') as errorMsg:
            errorMsg.write("No feature class in the destination database")
        raise Exception("No feature class in the destination database")

    arcpy.env.workspace = source_db_path
    # Check if the feature class exists in the source database
    featureClasses = arcpy.ListFeatureClasses()
    print(len(featureClasses))
    source_feature = None
    for fc in featureClasses:
        if needed_class in fc:
            print("Found the feature class in the source database")
            source_feature = path.join(source_db_path, fc)
            break

    if source_feature is None:
        with open(errorLog, 'a') as errorMsg:
            errorMsg.write("No feature class in the source database")
        raise Exception("No feature class in the source database")
    try:
        print("Deleting temp table")
        arcpy.Delete_management(GIS_TEMP_FILE)
        # Selection with query
        # Don't need to set up a new environment
        # Since it's currently at the source database
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
            Helper.send_email(sender, receiver, subject, "{} Update was successful.".format(needed_class))
        else:
            Helper.send_email(sender, receiver, subject, "No update needed because count was 0")
    except:
        # Check if any error occurred
        arcpy.AddMessage(arcpy.GetMessages(0))

        try:
            with open(errorLog, 'a') as errorMsg:
                errorMsg.write("%s\n%s\n" % (errorLog, arcpy.GetMessages(0)))
        except RuntimeError:
            arcpy.AddMessage("Unable to log")
            arcpy.AddMessage(RuntimeError.message)

        Helper.send_email(sender, receiver, "{} Update Error".format(needed_class),
                          "Script couldn't be executed.\n{}".format(arcpy.GetMessages(0)))
    finally:
        print("Deleting temp file")
        arcpy.Delete_management(GIS_TEMP_FILE)


def main():
    feature_update()


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("{} seconds".format(time.time() - start_time))
