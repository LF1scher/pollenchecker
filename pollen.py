import sys
from urllib import request
import requests
import json
from tabulate import tabulate
import argparse

# Strings

version = "1.0"

# Errors
errInfo = "A problem with the server occured"
invalidRegion = "Please specify a valid region"
regionIdorName = "Please provide either a region Id or a region name, but not both"
exiting = "Exiting..."

# Startup
readme = "https://opendata.dwd.de/README.txt"
dwdlicense = "By using this tool your device will contact the dwd servers. You therefore agree to their terms of service which can be found under"
proceed = "Proceed ? [Y/N]"

# Region Selection
regionInfo = "The following regions are available"
regionSelect = "Please choose a region by typing its corresponding name or the index number"

# Region data
regionNames = ["Inseln und Marschen", "Geest,Schleswig-Holstein und Hamburg", "Mecklenburg-Vorpommern", "Westl. Niedersachsen/Bremen", "Östl. Niedersachsen", "Rhein.-Westfäl. Tiefland", "Ostwestfalen", "Mittelgebirge NRW", "Brandenburg und Berlin", "Tiefland Sachsen-Anhalt", "Harz", "Tiefland Thüringen", "Mittelgebirge Thüringen", "Tiefland Sachsen",
               "Mittelgebirge Sachsen", "Nordhessen und hess. Mittelgebirge", "Rhein-Main", "Saarland", "Rhein, Pfalz, Nahe und Mosel", "Mittelgebirgsbereich Rheinland-Pfalz", "Oberrhein und unteres Neckartal", "Hohenlohe/mittlerer Neckar/Oberschwaben", "Mittelgebirge Baden-Württemberg", "Allgäu/Oberbayern/Bay. Wald", "Donauniederungen", "Bayern nördl. der Donau, o. Bayr. Wald, o. Mainfranken", "Mainfranken"]
loads = ["no load", "little or no load", "low load",
         "low to medium load", "medium load", "medium to high load", "high load"]
noData = "noData"


# Some strings to work with the dictionary
content = "content"
pollen = "Pollen"
ambrosia = "Ambrosia"
hasel = "Hasel"
graeser = "Graeser"
roggen = "Roggen"
esche = "Esche"
birke = "Birke"
erle = "Erle"
beifuss = "Beifuss"
dayafter = "dayafter_to"
today = "today"
tomorrow = "tomorrow"
pollenList = [ambrosia, hasel, graeser, roggen, esche, birke, erle, beifuss]

# Graphical Output
inRegion = "In the region"
pollenDataInRegion = "the following data was found"
days = ["Today", "Tomorrow", "The day after tomorrow"]


# Helper methods

def shutdown():
    """
    Ends program execution
    """
    print(exiting)
    sys.exit()


def promptYesNo():
    """
    Prompts the user for a yes or no. Exits program after 10 failed attempts
    :return: True if user entered Yes, False else
    """
    i = 0
    while i < 10:
        value = input(proceed)
        if(value == "Y" or value == "y"):
            return True
        if(value == "N" or value == "n"):
            return False
        i += 1
    shutdown()

def getLoadsForPollen(regionId, pollenToGet, jsonFile):
    """
    Returns all loads already as text for a specific pollen in a given region in a list
    :param regionId: corresponding regionId
    :param pollenToGet: type of pollen to get
    :param jsonFile: JSON file to read data from
    :return: list of loads like [today,tomorrow,day after tomorrow]
    """
    retVal = []
    retVal.append(pollenToGet)
    retVal.append(getLoadText(
        jsonFile[content][regionId][pollen][pollenToGet][today]))
    retVal.append(getLoadText(
        jsonFile[content][regionId][pollen][pollenToGet][tomorrow]))
    retVal.append(getLoadText(
        jsonFile[content][regionId][pollen][pollenToGet][dayafter]))
    return retVal


def getLoadsForRegion(regionId, jsonFile):
    """
    Returns all pollen loads for a specific region
    :param regionId: corresponding regionId
    :param jsonFile: JSON file to read data from
    """
    retVal = []
    for p in pollenList:
        retVal.append(getLoadsForPollen(regionId, p, jsonFile))
    return retVal


def printLoads(regionId, regionalLoad):
    """
    Prints out the pollen loads attained from @getLoadsForRegion to the user
    :param regionId: corresponding regionId
    :param regionalLoad: List of the regional loads from @getLoadsForRegion
    """
    print(inRegion + " " +
          regionNames[regionId] + " " + pollenDataInRegion + "\n")
    print(tabulate(regionalLoad, headers=[pollen] + days, tablefmt="rst"))


def getLoadText(value):
    """
    Returns the text representation of the given load id
    :param value: load id to convert to text
    :return: text representation of :param value
    """
    value = str(value)
    retVal = noData
    if(value == "0"):
        retVal = loads[0]
    elif(value == "0-1"):
        retVal = loads[1]
    elif(value == "1"):
        retVal = loads[2]
    elif(value == "1-2"):
        retVal = loads[3]
    elif(value == "2"):
        retVal = loads[4]
    elif(value == "2-3"):
        retVal = loads[5]
    elif(value == "3"):
        retVal = loads[6]
    return retVal


def printRegions():
    """
    Prints all given regions
    """
    print(regionInfo+"\n")
    for i in range(len(regionNames)):
        print(str(i) + " " + regionNames[i])


def selectRegion():
    """
    Prompt user selection for a region in interactive mode
    :return: Id of selected region
    """

    region = -2
    inputValid = False
    while not inputValid:
        regUser = input(regionSelect + " ")
        try:
            region = int(regUser)
            if(region < 0 or region > 26):
                print(invalidRegion)
            else:
                inputValid = True
        except ValueError:
            try:
                region = regionNames.index(regUser)
                inputValid = True
            except ValueError:
                print(invalidRegion)
    return region


def getServerData():
    """
    Contacts the DWD server and retrieves the JSON file.
    Ends program execution on error
    :return: JSON file of data
    """

    response = requests.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json")

    # Check for valid server response
    if(response.status_code != 200):
        print(errInfo)
        selectRegion
        sys.exit()

    return json.loads(response.text)
    

def main():
    parser = argparse.ArgumentParser(
        prog="pollen", description="a pollen load checker")
    parser.version = version
    parser.add_argument("-v", action="version")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--interactive",
                       help="Run in interactive mode, ignores all other parameters", action="store_true")
    group.add_argument("-r", type=int, help="Specify a region via id ")
    group.add_argument("-R", type=str, help="Specify a region via name")
    group.add_argument(
        "--regions", help="Displays all available regions", action="store_true")
    args = parser.parse_args()

    print(dwdlicense + " " + readme)
    if(not promptYesNo()):
        shutdown()

    if(args.interactive):
        # Run interactive

        jsonFile = getServerData()
        printRegions()
        region = selectRegion()
        regionalLoads = getLoadsForRegion(region, jsonFile)
        printLoads(region, regionalLoads)

    elif(args.regions):
        # Displays all available regions

        printRegions()

    else:
        # Run normal

        region = -2
        if(args.R):
            try:
                region = regionNames.index(args.R)
            except ValueError:
                print(invalidRegion)
                sys.exit()
        if(args.r):
            region = args.r
        if(region < 0 or region > 26):
            print(invalidRegion)
            sys.exit()
        jsonFile = getServerData()
        regionalLoads = getLoadsForRegion(region, jsonFile)
        printLoads(region, regionalLoads)


if __name__ == "__main__":
    main()
