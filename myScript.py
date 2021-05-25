#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
from os import path
import argparse
from argparse import RawTextHelpFormatter

import arcpy

import HelperScript as Helper


def parse_argument():
    """Parse arguments"""
    parser = argparse.ArgumentParser(description="Parser command", formatter_class=RawTextHelpFormatter)
    parser.add_argument("-o", "--option", required=False, default=1, type=int,
                        help="1. copy data \n"
                             "2. Create a new geospatial data")
    # parser.add_argument("-n", "--name", required=False, help="enter the name of feature class")
    parser.add_argument("-s", "--source", required=False, help="enter source database name")
    parser.add_argument("-t", "--target", required=False, help="enter target database name")
    parser.add_argument("-q", "--query", required=False, help="enter the query definition")
    args = vars(parser.parse_args())
    return args


def feature_update(args):
    # Convert all arguments from parser
    source = args["source"]
    target = args["target"]
    QUERYDEF = args["query"]

    class_name = os.path.splitext(source)[1][1:]
    # Paths
    filePath = path.abspath(os.getcwd())
    source_db_path = path.join(filePath, "webgisuser@csvgisds24s.sde")  # read only file
    dest_db_path = path.join(filePath, "EGIS@GISDBcsvegisds1t.sde")  # write and read file
    GIS_TEMP_FILE = path.join(dest_db_path, "Dest_temp_file")
    source_feature = path.join(source_db_path, source)
    target_feature = path.join(dest_db_path, target)
    # Log handler
    errorLog = path.join(filePath, "logs", "log.txt")

    # QUERYDEF = "(FromDate is null or FromDate<=CURRENT_TIMESTAMP) and (ToDate is null or ToDate>CURRENT_TIMESTAMP)"

    sender = "CSVGISICS03@dot.state.al.us"
    receiver = ["kohnkek@dot.state.al.us", "dangn@dot.state.al.us"]
    # sender = "dangn@dot.state.al.us"
    # receiver = ["dangn@dot.state.al.us"]
    subject = "{} Update".format(class_name)
    try:
        arcpy.env.workspace = source_db_path
        print("Deleting temp table")
        arcpy.Delete_management(GIS_TEMP_FILE)
        # Selection with query
        # Don't need to set up a new environment
        # Since it's currently at the source database
        print("Selecting table attributes")
        arcpy.Select_analysis(source_feature, GIS_TEMP_FILE, QUERYDEF)
        print("Counting the selection")
        temp_count = arcpy.GetCount_management(GIS_TEMP_FILE)
        count = int(temp_count.getOutput(0))
        if count > 0:
            # Truncate the table of the destination feature class
            print("Truncating tables")
            arcpy.TruncateTable_management(target_feature)
            # Append the selection to the table at target database
            print("Appending the selection")
            arcpy.Append_management(GIS_TEMP_FILE, target_feature, "TEST")
            print("Deleting temp file")
            arcpy.Delete_management(GIS_TEMP_FILE)
            Helper.send_email(sender, receiver, subject, "{} Update was successful.".format(class_name))
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

        Helper.send_email(sender, receiver, "{} Update Error".format(class_name),
                          "Script couldn't be executed.\n{}".format(arcpy.GetMessages(0)))
    finally:
        print("Deleting temp file")
        arcpy.Delete_management(GIS_TEMP_FILE)


def main():
    args = parse_argument()
    if args["option"] == 1:
        feature_update(args)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("{} seconds".format(time.time() - start_time))
