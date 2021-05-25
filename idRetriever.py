from arcgis.gis import GIS
import argparse


def parseArgument():
    """Parse username and password from the user"""
    parser = argparse.ArgumentParser(description="Parser command")
    parser.add_argument("-u", "--username", required=True, help="enter arcgis username")
    parser.add_argument("-p", "--password", required=True, help="enter arcgis password")
    args = vars(parser.parse_args())
    return args


def printFeatLayer(args):
    """ Access arcgis online using argument from the parser """
    portal = GIS(username=args["username"], password=args["password"])
    features = portal.content.search(args["id"])
    if len(features) != 0:
        for feat in features:
            print(feat)
            # Length of the layers list = 0 (not None) when a Feature Layers doesn't have any layer
            if len(feat.layers) != 0:
                print(f'layers of this Feature Layer: {feat.layers}')
                print("Layers name: ", end='')
                for lyr in feat.layers:
                    print(lyr.properties.name)
            else:
                print("This Feature Layer doesn't have any layers")
            # Length of tables = 0 (not None) when a Feature Layers doesn't have any table
            if len(feat.tables) != 0:
                print(f'Table of this Feature Layer: {feat.tables}')
            else:
                print("This Feature Layer doesn't have any tables")


def main():
    args = parseArgument()
    args["id"] = input("Enter feature layer id: ")
    printFeatLayer(args)


if __name__ == '__main__':
    main()
