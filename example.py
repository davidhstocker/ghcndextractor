'''
Created on Apr 27, 2016

@author: David Stocker
'''
from ghcndextractor import ghcndextractor

    
    
if __name__ == "__main__":    

    ghcndextractor.countries = ["US"]
    ghcndextractor.states = ["NJ"]     
    ghcndextractor.ghcnFolder = "/Users/d035331/Documents/Demo/DemoData_Weather/ghcnd_all"   
    
     
    ghcndextractor.getStationsFromFiles()
    stations = ghcndextractor.getCSVStationMetaData()
    ghcndextractor.readDailyFiles()
    dayCSV = ghcndextractor.getDailyDataCSV(["12"], ["25"], ["USW00014780"])
    print(dayCSV)

