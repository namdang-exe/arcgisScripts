from arcgis.gis import GIS
import arcgis.features as features
import ast

filePath = r"account"

def getCredential(file):
    # read account credential file
    f = open(file, "r")
    cred = f.read()
    # convert from str to dict
    cred = ast.literal_eval(cred)
    f.close()
    return cred

if __name__ == '__main__':
    cred = getCredential(filePath)
    gis = GIS(username=cred['username'], password=cred['password'])
    user = gis.users.get(cred["username"])
    # search_results = gis.content.search(query="id", 752e3069336f40008cab8edf85d92c08)
    search_results = gis.content.advanced_search(query="752e3069336f40008cab8edf85d92c08")
    search_results = gis.content.search('Feature Layer')
    print(search_results)