'''
Created on Apr 22, 2016

@author: David Stocker

Extracts data from a downloaded copy of the GHCN-Daily dataset


http://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
'''

import os
import re
import decimal
import codecs

#Preferences
global csvSeperator
global oldestYear
global youngestYear
global ghcnFolder

csvSeperator = ","
oldestYear = 1
youngestYear = 3000
ghcnFolder = None

class undefinedGHCNDatasetLocation(ValueError):
    pass


class Station(object):
    def __init__(self, stationID, latitude, longitude, countryCode, name, elevationStr, state):
        self.stationID = stationID
        self.latitude = latitude
        self.longitude = longitude
        self.countryCode = countryCode
        self.name = name
        self.elevationStr = elevationStr
        if state is not None:
            self.state = state
        else:
            self.state = ""
            

    
    def getCSVRow(self):
        global csvSeperator
        csvString = "%s"  %(self.stationID)
        csvString = "%s%s %s"  %(csvString, csvSeperator, self.stationID)
        csvString = "%s%s %s"  %(csvString, csvSeperator, self.name)
        csvString = "%s%s %s"  %(csvString, csvSeperator, self.countryCode)
        csvString = "%s%s %s"  %(csvString, csvSeperator, self.state)
        csvString = "%s%s %s"  %(csvString, csvSeperator, self.latitude)
        csvString = "%s%s %s"  %(csvString, csvSeperator, self.longitude)
        csvString = "%s%s %s"  %(csvString, csvSeperator, self.elevationStr)
        return csvString        
           
        
class DailyMeasurements(object):
    """
        The measurements of all five core elements (plus average cloudiness)  elements and metadata flags for a single day at a station.
        
        The average cloudiness measurements can be either manual (the ACMH and ACSH elements in the .dly files) or 30-second ceilometer data 
            (the ACMC and ACMC elements).  The preferManual option determines whether manual (xxxH) or automatic (xxxC) data is chosen
            when both types are available.
    """
    def __init__(self, preferManual = False):
        self.preferManual = preferManual  
        self.TMAX = []  #max daily temp
        self.TMIN = []  #min daily temp
        self.PRCP = []  #Precipitation (tenths of mm)
        self.SNOW = []  #Snowfall (mm)
        self.SNWD = []  #Snow depth (mm)
        self.ACMM = []  #Average cloudiness midnight to midnight (percent).  Either from  from 30-second ceilometer data or manual measurement
        self.ACSS = []  #Average cloudiness sunrise to sunset (percent).  Either from  from 30-second ceilometer data or manual measurement
        
    def convertToDecimal(self, value, tenths = 0):
        if value != "":
            splitVal = value.split('-')
            if len(splitVal) > 1:
                valTuple = tuple(splitVal[1])
            else:
                valTuple = tuple(splitVal[0])
            intList = []
            for valTupleEntry in valTuple:
                intList.append(int(valTupleEntry))
            intTuple = tuple(intList)
            sign = u'-' in value
            return decimal.Decimal((sign, intTuple, tenths))
        else:
            return None
            
    
        
    def addMeasurement(self, measureType, value, mFlag, qFlag, sFlag):
        if measureType == "TMAX":
            if value != u"-9999":
                try:
                    tempMax = self.convertToDecimal(value, -1) #.dly fiels is in tenths of a degree
                    if tempMax is not None:
                        self.TMAX = [tempMax, mFlag, qFlag, sFlag]
                    else:
                        self.TMAX = []
                except Exception:
                    self.TMAX = []
        elif measureType == "TMIN":
            if value != u"-9999":
                try:
                    tempMin = self.convertToDecimal(value, -1) #.dly fiels is in tenths of a degree
                    if tempMin is not None:
                        self.TMIN = [tempMin, mFlag, qFlag, sFlag]
                    else:
                        self.TMIN = []
                except Exception:
                    self.TMIN = []
        elif measureType == "PRCP":
            if value != u"-9999":
                try:
                    precip = self.convertToDecimal(value) #.dly fiels is in mm
                    if precip is not None:
                        self.PRCP = [precip, mFlag, qFlag, sFlag]
                    else:
                        self.PRCP = []
                except Exception:
                    self.PRCP = []
        elif measureType == "SNOW":
            if value != u"-9999":
                try:
                    snowFall = self.convertToDecimal(value) #.dly fiels is in mm
                    if snowFall is not None:
                        self.SNOW = [snowFall, mFlag, qFlag, sFlag]
                    else:
                        self.SNOW = []
                except Exception:
                    self.SNOW = []
        elif measureType == "SNWD":
            if value != u"-9999":
                try:
                    temp = self.convertToDecimal(value) #.dly fiels is in mm
                    if temp is not None:
                        self.SNWD = [temp, mFlag, qFlag, sFlag]
                    else:
                        self.SNWD = []
                except Exception:
                    self.SNWD = []
        elif measureType == "ACMH":
            if (self.preferManual == True) or (not self.ACMM):
                if value != u"-9999":
                    try:
                        acmh = self.convertToDecimal(value) #.dly fiels is in %
                        if acmh is not None:
                            self.ACMM = [acmh, mFlag, qFlag, sFlag]
                        else:
                            self.ACMM = []
                    except Exception:
                        self.ACMM = []
        elif measureType == "ACMC":
            if (self.preferManual == False) or (not self.ACMM):
                if value != u"-9999":
                    try:
                        acmc = self.convertToDecimal(value) #.dly fiels is in %
                        if acmc is not None:
                            self.ACMM = [acmc, mFlag, qFlag, sFlag]
                        else:
                            self.ACMM = []
                    except Exception:
                        self.ACMM = []
        elif measureType == "ACSH":
            if (self.preferManual == True) or (not self.ACSS):
                if value != u"-9999":
                    try:
                        acsh = self.convertToDecimal(value) #.dly fiels is in %
                        if acsh is not None:
                            self.ACSS = [acsh, mFlag, qFlag, sFlag]
                        else:
                            self.ACSS = []
                    except Exception:
                        self.ACSS = []
        elif measureType == "ACSC":
            if (self.preferManual == False) or (not self.ACSS):
                if value != u"-9999":
                    try:
                        acsc = self.convertToDecimal(value) #.dly fiels is in %
                        if acsc is not None:
                            self.ACSS = [acsc, mFlag, qFlag, sFlag]
                        else:
                            self.ACSS = []
                    except Exception:
                        self.ACSS = []               

        
        

class StationMonth(object):
    """The GHCN-Daily data is organized such that a single data row has StationMonth data for a single element and there are five
        elements in the standard dataset.  The data is organized in the Hana system on a per day basis for all five elements
        
        Our goal is to collect all five measurements for all days of the month into a single object.  We can then iterate over 
        this object to pull out the data on a per day basis.
        
        stationMonthCode - Is the hash Country-StationID-Year-Month, made up of first 17 characters of the row
            Variable   Columns   Type
            ------------------------------
            ID            1-11   Character
            YEAR         12-15   Integer
            MONTH        16-17   Integer
        
        http://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
    """
    
    def __init__(self, stationMonthCode, stationID, countryCode, year, month):
        self.stationMonthCode = stationMonthCode
        self.stationID = stationID
        self.countryCode = countryCode
        self.year = year
        self.month = month
        self.days = {}
        
        for x in range(1, 31):
            day = DailyMeasurements()
            xKey = str(x)
            self.days[xKey] = day      
            
            
    def getDaily(self, day):    
        dailyMeasurement = self.days[day]
        
        tmax = ''
        try:
            tmax = str(dailyMeasurement.TMAX[0])
        except: pass

        tmin = ''
        try:
            tmin = str(dailyMeasurement.TMIN[0])
        except: pass

        prcp = ''
        try:
            prcp = str(dailyMeasurement.PRCP[0])
        except: pass

        snow = ''
        try:
            snow = str(dailyMeasurement.SNOW[0])
        except: pass

        snwd = ''
        try:
            snwd = str(dailyMeasurement.SNWD[0])
        except: pass

        acss = ''
        try:
            acss = str(dailyMeasurement.ACSS[0])
        except: pass

        acmm = ''
        try:
            acmm = str(dailyMeasurement.ACMM[0])
        except: pass

        return tmax, tmin, prcp, snow, snwd, acmm, acss


            
    def addMeasurement(self, dayStr, measureType, measurement):
        day = str(dayStr)
        dailyMeasurements = self.days[day]
        dailyMeasurements.addMeasurement(measureType.strip(), measurement[0:5].strip(), measurement[5:6].strip(), measurement[6:7].strip(), measurement[7:8].strip())
        self.days[day] = dailyMeasurements
        
        
    def getMonthlyAverages(self):
        sumTmax = decimal.Decimal('0.0')
        sumTmin = decimal.Decimal('0.0')
        sumSnwd = decimal.Decimal('0.0')
        sumAcmm = decimal.Decimal('0.0')
        sumAcss= decimal.Decimal('0.0')
        countTmax = 0
        countTmin = 0
        countSnwd = 0
        countAcmm = 0
        countAcss = 0
        hasTmax = False
        hasTmin = False
        hasSnwd = False
        hasAcmm = False
        hasAcss = False
        
        for dayKey in self.days.keys():
            day = self.days[dayKey]
            if len(day.TMAX) > 0:
                countTmax = countTmax + 1
                sumTmax = sumTmax + day.TMAX[0]
                hasTmax = True
                
            if len(day.TMIN) > 0:
                countTmin = countTmin + 1
                sumTmin = sumTmin + day.TMIN[0]
                hasTmin = True  
                
            if len(day.SNWD) > 0:
                countSnwd = countSnwd + 1
                sumSnwd = sumSnwd + day.SNWD[0]
                hasSnwd = True 
                
            if len(day.ACMM) > 0:
                countAcmm = countAcmm + 1
                sumAcmm = sumAcmm + day.ACMM[0]
                hasAcmm = True 
                
            if len(day.ACSS) > 0:
                countAcss = countAcss + 1
                sumAcss = sumAcss + day.ACSS[0]
                hasAcmm = True
                
        if hasTmax is True:
            avgTmax = sumTmax/decimal.Decimal(countTmax)
        else:
            avgTmax = None
            
        if hasTmin is True:
            avgTmin = sumTmin/decimal.Decimal(countTmin)
        else:
            avgTmin = None  
                     
        if hasSnwd is True:
            avgSnwd = sumSnwd/decimal.Decimal(countSnwd)
        else:
            avgSnwd = None
            
        if hasAcmm is True:
            avgAcmm = sumAcmm/decimal.Decimal(countAcmm)
        else:
            avgAcmm = None
            
        if hasAcss is True:
            avgAcss = sumAcss/decimal.Decimal(countAcss)
        else:
            avgAcss = None
            
        return avgTmax, avgTmin, avgSnwd, avgAcmm, avgAcss
    
    
    def getMonthlySums(self):
        sumPrcp = decimal.Decimal('0.0')
        sumSnow = decimal.Decimal('0.0')
        hasPrcp = False
        hasSnow = False
 
        for dayKey in self.days.keys():
            day = self.days[dayKey]
            if day.PRCP:
                sumPrcp = sumPrcp + day.PRCP[0]
                hasPrcp = True
            if day.SNOW:
                sumSnow = sumSnow + day.SNOW[0]
                hasSnow = True
                
                
        if hasPrcp is False:
            sumPrcp = None 
        if hasSnow is False:
            sumSnow = None 
            
        return sumPrcp, sumSnow



class Measurments(object):
    fileMeasurements = {}
    
    def getMonthlyData(self, months = [], stations = []):
        """
            Return monthly data in a 'CSV' style format
        """
        dataRows = []
        for stationMonthCode in self.fileMeasurements.keys():
            try:
                stationMonth = self.fileMeasurements[stationMonthCode]
                if ((not months) or (stationMonth.month in months)) and ((not stations) or (stationMonth.stationID in stations)):
                    avgTmax, avgTmin, avgSnwd, avgAcmm, avgAcss = stationMonth.getMonthlyAverages()
                    sumPrcp, sumSnow = stationMonth.getMonthlySums()
                    
                    dataRow = { 'stationID': stationMonth.stationID,
                                'year': stationMonth.year,
                                'month': stationMonth.month,
                                'avgTmax': avgTmax,
                                'avgTmin': avgTmin,
                                'avgSnwd': avgSnwd,
                                'avgAcmm': avgAcmm,
                                'avgAcss': avgAcss,
                                'sumPrcp': sumPrcp,
                                'sumSnow': sumSnow
                                }
                    dataRows.append(dataRow)
            except Exception as e:
                raise e 
        return dataRows
    
    
    def getMonthlyDataCSV(self, months = [], stations = []):
        """
            Return monthly data in a 'CSV' style format
        """
        global csvSeperator
        csvRows = []
        for stationMonthCode in self.fileMeasurements.keys():
            try:
                stationMonth = self.fileMeasurements[stationMonthCode]
                if ((not months) or (stationMonth.month in months)) and ((not stations) or (stationMonth.stationID in stations)):
                    avgTmax, avgTmin, avgSnwd, avgAcmm, avgAcss = stationMonth.getMonthlyAverages()
                    sumPrcp, sumSnow = stationMonth.getMonthlySums()
                    
                    csvString = "%s"  %(stationMonth.stationID)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, stationMonth.year)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, stationMonth.month)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, avgTmax)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, avgTmin)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, sumPrcp)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, sumSnow)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, avgSnwd)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, avgAcmm)
                    csvString = "%s%s %s"  %(csvString, csvSeperator, avgAcss)
                    csvRows.append(csvString)
            except Exception as e:
                raise e 
        return csvRows

    
#Global variables using classes
global measurements
global stationlist
global stationIDCodes
global countries
global states
states = []
countries = []
measurements = Measurments() 
stationlist = []
stationIDCodes = []



def readStationsFile():
    """
        countries is a list of strings, containing the ISO codes of the desired countries in the extraction.  The first two characters of a station row
            in ghcnd-stations.txt contain the country code.  Leaving this list empty sets no filtering (all countries)
            
        states is a list of states (or provinces) within the countries list.  This comes at positions 38 and 39 in the ghcnd-stations.txt record.  If there
            is a state filter and if that state abbreviation shows up in a valid country, the record will be read.  It is not required to bind specific states
            to specific countries.
            E.g. if countries = ["US", "CA"] and states = ["ON", "OH"], then stations in the US state of Ohio and the neighboring Canadian Province of Ontario 
            will be read.
    """
    global stationlist
    global ghcnFolder
    global countries
    global states
    
    if ghcnFolder is None:
        errorMessage = "Undefined  location for ghcn dataset.  Please add it's location"
        raise undefinedGHCNDatasetLocation(errorMessage)
    
    #filePath = os.path.realpath(__file__)
    #selfDir = os.path.dirname(filePath)
    #dataLocation = os.path.join(selfDir, "ghcnd_all", "ghcnd-stations.txt")
    dataLocation = os.path.join(ghcnFolder, "ghcnd_all", "ghcnd-stations.txt")
    readLoc = codecs.open(dataLocation, "r", "utf-8")
    allLines = readLoc.readlines()
    readLoc.close
    
    print("%s Stations to be loaded" %len(allLines))
    
    for eachReadLine in allLines:
        #the stationmonth metadata
        countryCode = eachReadLine[0:2].strip()
        stationID = eachReadLine[0:11].strip()
        latitude= decimal.Decimal(eachReadLine[13:20].strip())
        longitude = decimal.Decimal(eachReadLine[22:30].strip())
        elevationStr= eachReadLine[32:37]
        state = eachReadLine[38:40].strip()
        name = eachReadLine[42:71].strip()
        
        if ((not countries) or (countryCode in countries)):
            if ((not states) or (state in states)):
                newStation = Station(stationID, latitude, longitude, countryCode, name, elevationStr, state)
                stationlist.append(newStation)
                stationIDCodes.append(stationID)



def readRow(lineOfData):
    global measurements
    global stationlist
    global oldestYear
    global youngestYear
    
    #the stationmonth metadata
    countryCode = lineOfData[0:2]
    stationID = lineOfData[0:11]
    stationMonthCode = lineOfData[0:17]
    year = lineOfData[11:15]
    month = lineOfData[15:17]
    
    yearInt = int(year)
    oldestYear = int(oldestYear)  #gotta luv duck typing!
    youngestYear = int(youngestYear)
    if (yearInt >= oldestYear) and (yearInt <= youngestYear):
        #Either get ahold of stationMonth, or create a new one
        if stationMonthCode in measurements.fileMeasurements:
            stationMonth = measurements.fileMeasurements[stationMonthCode]
        else:
            stationMonth = StationMonth(stationMonthCode, stationID, countryCode, year, month)
        
        #the actual data from the 
        element = lineOfData[17:21]
        for x in range(0, 30):
            dayOM = x + 1
            offsetStart = (x*8)+21
            offsetEnd = offsetStart + 8
            stationMonth.addMeasurement(dayOM, element, lineOfData[offsetStart:offsetEnd])
            
        measurements.fileMeasurements[stationMonthCode] = stationMonth
        
 
                
def readDailyFiles():
    global measurements
    global ghcnFolder
    global stationlist
    global stationIDCodes
    global countries
    global states
   
    #Go through the condition repository directory and load the files up
    dataLocation = os.path.join(ghcnFolder, "ghcnd_all")
    fileList = os.listdir(dataLocation)
    
    #Count the files to provide feedback
    fileCount = 0
    for fileName in fileList:
        if (fileName[0:11] in stationIDCodes):
            filePath = os.path.join(dataLocation, fileName)
            if re.search( '.dly', fileName) is not None:
                fileCount = fileCount + 1
            
    print("Loading data from %s .dly files" %fileCount)
               
    for fileName in fileList:
        #Graph.logQ.put( [logType , logLevel.DEBUG , method , 'Examining %s' % package])
        if (fileName[0:11] in stationIDCodes):
            filePath = os.path.join(dataLocation, fileName)
            if re.search( '.dly', fileName) is not None:
                readLoc = codecs.open(filePath, "r", "utf-8")
                allLines = readLoc.readlines()
                readLoc.close
                
                for eachReadLine in allLines:
                    readRow(eachReadLine)
                
                

def getCSVStationMetaData():
    global csvSeperator
    csvData = []
    csvString = "%s"  %("StationID")
    
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Name")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Country")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "State")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Lat")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Lon")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Elevation")
    csvData.append(csvString)
    for station in stationlist:
        nextRow = station.getCSVRow()
        csvData.append(nextRow)
        
    return csvData
    

def getMonthlyData(months = [], stations = []):
    dataDict = measurements.getMonthlyData(months, stations)
    return dataDict    
    

def getMonthlyDataCSV(months = [], stations = []):
    global csvSeperator
    global measurements
    csvData = []
    csvString = "%s"  %("StationID")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Year")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Month")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "TempMax")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "TempMin")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Precipitation")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Snowfall")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "SnowDepth")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "CloudCover(24hour)")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "CloudCover(day)")
    csvData.append(csvString)   
    
    monthlyData = measurements.getMonthlyDataCSV(months, stations)
    csvData.extend(monthlyData)
    return csvData



def getDailyData(months = [], days = [], stations = []):
    dataRows = []
    for stationMonthCode in measurements.fileMeasurements.keys():
        try:
            stationMonth = measurements.fileMeasurements[stationMonthCode]
            if ((not months) or (stationMonth.month in months)) and ((not stations) or (stationMonth.stationID in stations)):
                if (not days):
                    for x in range(1, 31):
                        days.append(str(x))
                for day in days:
                    try:
                        avgTmax, avgTmin, sumPrcp, sumSnow, avgSnwd, avgAcmm, avgAcss = stationMonth.getDaily(day)
                        dataRow = { 'stationID': stationMonth.stationID,
                                    'year': stationMonth.year,
                                    'month': stationMonth.month,
                                    'day': day,
                                    'tmax': avgTmax,
                                    'tmin': avgTmin,
                                    'snwd': avgSnwd,
                                    'acmm': avgAcmm,
                                    'acss': avgAcss,
                                    'prcp': sumPrcp,
                                    'snow': sumSnow
                                    }
                        dataRows.append(dataRow)
                    except Exception as e:
                        pass
        except Exception as e:
            raise e 
    return dataRows


def getDailyDataCSV(months = [], days = [], stations = []):
    global csvSeperator
    global measurements
    csvRows = []
    csvString = "%s"  %("StationID")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Year")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Month")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Day")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "TempMax")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "TempMin")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Precipitation")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "Snowfall")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "SnowDepth")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "CloudCover(24hour)")
    csvString = "%s%s %s"  %(csvString, csvSeperator, "CloudCover(day)")
    csvRows.append(csvString)   

    for stationMonthCode in measurements.fileMeasurements.keys():
        try:
            stationMonth = measurements.fileMeasurements[stationMonthCode]
            if ((not months) or (stationMonth.month in months)) and ((not stations) or (stationMonth.stationID in stations)):
                if (not days):
                    for x in range(1, 31):
                        days.append(str(x))
                for day in days:
                    try:
                        avgTmax, avgTmin, sumPrcp, sumSnow, avgSnwd, avgAcmm, avgAcss = stationMonth.getDaily(day)
                        csvString = "%s"  %(stationMonth.stationID)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, stationMonth.year)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, stationMonth.month)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, day)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, avgTmax)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, avgTmin)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, sumPrcp)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, sumSnow)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, avgSnwd)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, avgAcmm)
                        csvString = "%s%s %s"  %(csvString, csvSeperator, avgAcss)
                    except Exception as e:
                        pass
                csvRows.append(csvString)
        except Exception as e:
            raise e 
    return csvRows

