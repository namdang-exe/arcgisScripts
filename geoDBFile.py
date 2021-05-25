from HelperScriptArcpy import *
from os import path

filePath = r"C:/Users/dangn/PycharmProjects/arcgisTest"
# accountFilePath = "account"
# Get the credential from the account file
# cred = getCredential(accountFilePath)

# Establish a connection to CSVEGISDS01
db_file = "csvegisds1t.sde"
db_path = filePath + r"/" + db_file
if not path.exists(db_path):
    try:
        db_path = arcpy.CreateDatabaseConnection_management(filePath, db_file,
                                                           "SQL_SERVER", "csvegisds1t",
                                                            account_authentication=False, database="GISDB")
        print("Connects to the database successfully!")
    except Exception as genErr:
        print("General Error: {}".format(genErr))
        raise Exception(genErr)
# Set the environment to the database
arcpy.env.workspace = str(db_path)
# Get all feature classes from the database
featureClasses = arcpy.ListFeatureClasses()
fc = featureClasses[0]

# Create a new local geodatabase file if it's not existed
# Set file path and name for geodatabase
db_filePath = path.join(filePath, "gdbs")
out_name = "mygdb.gdb"
geodb = r"gdbs/mygdb.gdb"
if not path.exists(geodb):
    try:
        geodb = arcpy.CreateFileGDB_management(db_filePath, out_name)
        print("A geodatabase file created successfully!")
    except Exception as genErr:
        print("General Error: {}".format(genErr))
        raise Exception(genErr)
else:
    print("A File Geodatabase already existed.")

# Check if feature classes already existed and delete it
# Set the environment to the FileGDB
arcpy.env.workspace = str(geodb)
fc_name = fc.split(".")[1]

if arcpy.Exists(fc_name):
    print("The Feature class exists")
    arcpy.Delete_management(fc_name)
else:
    print("No Feature Classes in FileGDB, moving on...")
print("FileGDB clean up complete.")

# Copy a feature class to the local geodatabase
# Set the environment to the database
arcpy.env.workspace = str(db_file)
out_featureClass = str(geodb) + r"/" + fc_name
try:
    arcpy.CopyFeatures_management(fc, out_featureClass)
    print("{} feature class was created!".format(fc_name))
except Exception as genErr:
    print("General Error: {}".format(genErr))
    raise Exception(genErr)

# Disconnect with the database
os.remove(str(db_path))
