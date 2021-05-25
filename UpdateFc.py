#!/usr/bin/env python
# coding: utf-8

import arcpy
import HelperScript as helper
import os
from os import path
import time

start_time = time.time()

############ Change this to reuse this script
filePath = path.abspath(os.getcwd())
needed_class = "LRS_RINV_Divided"

source_db_path = path.join(filePath, "webgisuser@csvgisds24s.sde")  # read only file
dest_db_path = path.join(filePath, "EGIS@GISDBcsvegisds1t.sde")  # write and read file
source_feature = path.join(source_db_path, "EGISDB.LRS.{}".format(needed_class))
target_feature = path.join(dest_db_path, "GISDB.EGIS.{}".format(needed_class))
GIS_TEMP_FILE = path.join(dest_db_path, "Dest_temp_file")
# Log handler
errorLog = path.join(filePath, "logs", "log.txt")

QUERYDEF = "(FromDate is null or FromDate<=CURRENT_TIMESTAMP) and (ToDate is null or ToDate>CURRENT_TIMESTAMP)"

sender = "CSVGISICS03@dot.state.al.us"
receiver = ["kohnkek@dot.state.al.us", "dangn@dot.state.al.us"]
subject = "{} Update".format(needed_class)
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
        helper.send_email(sender, receiver, subject, "{} Update was successful.".format(needed_class))
    else:
        helper.send_email(sender, receiver, subject, "No update needed because count was 0")
except:
    # Check if any error occurred
    arcpy.AddMessage(arcpy.GetMessages(0))

    try:
        with open(errorLog, 'a') as errorMsg:
            errorMsg.write("{0}\n{1}\n".format(errorLog, arcpy.GetMessages(0)))
    except RuntimeError:
        arcpy.AddMessage("Unable to log")
        arcpy.AddMessage(RuntimeError.message)

    helper.send_email(sender, receiver, "{} Update Error".format(needed_class),
                      "Script couldn't be executed.\n{}".format(arcpy.GetMessages(0)))
finally:
    print("Deleting temp file")
    arcpy.Delete_management(GIS_TEMP_FILE)
    print("{} seconds".format(time.time() - start_time))
