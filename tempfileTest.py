import os
from os import path
import arcpy
import tempfile
import HelperScriptArcpy as helper

filePath = r"C:/Users/dangn/PycharmProjects/arcgisTest"

connectionPath = tempfile.TemporaryDirectory()
db_path = helper.createTempConnection(connectionPath.name, "csvgisds24s.sde", "SQL_SERVER", "csvgisds24s",
                                      "OPERATING_SYSTEM_AUTH")
arcpy.env.workspace = str(db_path)
featureClasses = arcpy.ListFeatureClasses()
for fc in featureClasses:
    print(fc)

