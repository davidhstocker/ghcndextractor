'''
Created on Mar 24, 2016

@author: David Stocker
'''

import argparse
import os
import codecs

from ghcndextractor import ghcndextractor as ghcndextractor

    
    
if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description="GHCND to CSV extractor (daily version)")
    parser.add_argument("-v", "--csv", type=str, help="|String| The csv seperator.  In the US, this is typically a comma and in Europe is is a semicolon.  Default is comma.")
    parser.add_argument("-o", "--oldyear", type=str, help="|String| The earliest possible dataset year that can be read (if data is available)")
    parser.add_argument("-y", "--youngyear", type=str, help="|Int| The latest possible dataset year that can be read (if data is available)")
    parser.add_argument("-g", "--ghcnfolder", type=str, help="|String| The location of the ghcn_all folder, if it is not a sibling of this script")
    parser.add_argument("-c", "--country", nargs='*', type=str, help="|String| One or more country codes, for country data to be extracted")
    parser.add_argument("-s", "--state", nargs='*', type=str, help="|String| One or more state (or province) codes, if individual states within a country is to be extracted")
    parser.add_argument("-m", "--month", nargs='*', type=str, help="|Int| One or more months (as numbers), if the user wishes to restrict the results to particular months")
    parser.add_argument("-d", "--day", nargs='*', type=str, help="|Int| One or more days (as numbers), if the user wishes to restrict the results to particular days of the month")
    parser.add_argument("-t", "--station", nargs='*', type=str, help="|String| One or more reporting stations, if the user wishes to filter the results to particular stations")
    parser.add_argument("-f", "--fileloc", type=str, help="|String| Output filename.  Defaults to 'dhcndData.csv' if no argument supplied")
    args = parser.parse_args()
    
    if args.csv:
        ghcndextractor.csvSeperator = args.csv
        
    if args.oldyear:
        ghcndextractor.oldestYear = args.oldyear
        
    if args.youngyear:
        ghcndextractor.youngestYear = args.youngyear
    
    if args.ghcnfolder:
        ghcndextractor.ghcnFolder = args.ghcnfolder
    else:
        filePath = os.path.realpath(__file__)
        selfDir = os.path.dirname(filePath)
        ghcndextractor.ghcnFolder = selfDir
     
        
    countries = []
    if args.country:
        for country in args.country:
            country = country.upper()
            countries.append(country)
        ghcndextractor.countries = countries
            
    states = []
    if args.state:
        for state in args.state:
            state = state.upper()
            states.append(state)
        ghcndextractor.states = states
        
    months = []
    if args.month:
        for month in args.month:
            months.append(month)
            
    days = []
    if args.day:
        for day in args.day:
            days.append(day)
            
    stationFilter = []
    if args.station:
        for filteredStation in args.station:
            stationFilter.append(filteredStation)
            
    dataLocation = "dhcndData.csv"
    if args.fileloc:
        dataLocation = args.fileloc


            
    ghcndextractor.readStationsFile()
    stations = ghcndextractor.getCSVStationMetaData()
    ghcndextractor.readDailyFiles()
    dayCSV = ghcndextractor.getDailyDataCSV(months, days, stationFilter)
    
    
    f = codecs.open( dataLocation, 'w', 'utf-8' )
    for l in dayCSV:
        f.write("%s\n" % l)
    f.close
    
    stationCount = len(ghcndextractor.stationIDCodes)
    print ("Done!  Measurements from %s stations written to %s" %(stationCount, dataLocation))