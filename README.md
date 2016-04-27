# ghcndextractor
A simple extractor for the GHCN-Daily dataset .dly files into CSV or dict format.  It also enables filtering by  time period ranges (in years), country and state/province if they are relevant to the countries in question and individual observation stations.  This filtering is practical as the GHCND .dly dataset is very large (2 1/2 gb in compressed format as of early 2016).  

#Quickstart

If you just want to perform a quick extraction to CSV, then you should use **dailytocsv.py** or **monthlytocsv.py**.  These two command line utilities are feature a full suite of keyword arguments for refined usage.

Suppose you have downloaded the ghcnd_all archive and extracted it to a folder on your desktop.  Now you want to see the observations for Lakhurst, NJ, USA  on Christmas Day for as long as the US Weather Service has been taking measurements there.  The station ID is "USW00014780".   Note that the script will take a few minutes to run, even when filtering to a single station.  

`dailytocsv.py -c us -s nj -t USW00014780 -g /Users/davidstocker/Documents/Desktop -f LakehurstOnChristmas.csv`

Below is a full accounting of the arguments used by both utilities.

| Short Arg | Long Arg     | Single/Multiple   | Description                                |
| :--------:|:------------:|:-----------------:| ------------------------------------------ |
| -v        | --csv        | Single            | The csv seperator.  In the US, this is<br> |
|           |              |                   |     typically a comma and in Europe is<br> |
|           |              |                   |     is a semicolon.  Default is comma.     | 
| -o        | --oldyear    | Single            | The earliest possible dataset year that<br>|
|           |              |                   |     can be read (if data is available).    |
| -y        | --youngyear  | Single            | The latest possible dataset year that<br>  |
|           |              |                   |     can be read (if data is available).    |
| -g        | --ghcnfolder | Single            | The location of the ghcn_all folder, if<br>|
|           |              |                   |     it is not a sibling of this script.    | 
| -c        | --country    | Multiple          | One or more country codes, for country<br> | 
|           |              |                   |     data to be extracted.                  | 
| -s        | --state      | Multiple          | One or more state (or province) codes,<br> | 
|           |              |                   |     if individual states within a<br>      |
|           |              |                   |     country are to be filtered.            |
| -m        | --month      | Multiple          | One or more months (as numbers), if the<br>| 
|           |              |                   |     user wishes to restrict the results<br>|
|           |              |                   |     to particular months.                  | 
| -d        | --day        | Multiple          | One or more days (as numbers), if the<br>  |
|           |              |                   |     user wishes to restrict the results<br>| 
|           |              |                   |     to particular days of the month.       |
| -t        | --station    | Multiple          | One or more reporting stations, if the<br> | 
|           |              |                   |     user wishes to filter the results<br>  | 
|           |              |                   |     to particular stations.                |
| -f        | --fileloc    | Single            | Output filename.  Defaults to<br>          |
|           |              |                   |     dhcndData.csv if no argument supplied. |


#Using ghcndextractor

If you want to use the  ghcndextractor directly, so that you can use the results elsewhere, it is also fairly easy to use.  There are couple of concepts to understand first:

+Everything has a read stage and a get stage. 

+There is a method,  **readStationsFile()**,to read the stations from ghcnd-stations.txt into an internal data structure.  Its get counterpart is **getCSVStationMetaData()**.  This returns a list of strings in CSV format.

+The method to read the .dly files into memory is **readDailyFiles()**.  

+There are several get methods for the data, once it is memory.  They are **getDailyDataCSV()**, **getDailyData()**, **getMonthlyDataCSV()** and **getMonthlyCSV()**.

+Certain variables - some filter settings  and the location of the ghcnd_all folder -  keep getting re-used repeatedly.  These are stored as global variables in the ghcndextractor module itself.  You set them directly. 

+Some - such as the month, day and station name filters - are set directly at execution.  In general, if a filter is used during read, it is a module variable.  If the filter is used at get time, it uses method parameters.  This allows you to perform one read and then pull slices out of memory.


##Example Usage

To manually aquire the data from our example above, we'll do the following.

1. Import  the ghcndextractor module.
2. Set the country and state filters.  Both are lists of strings.
3. Set the location of the ghcnd_all  folder
4. Read the station metadata
5. Read the .dly files containing NJ.
6. Get all December 25 readings from  station USW00014780 (well'll do this as a CSV and as a list of dicts)

```python
from ghcndextractor import ghcndextractor

#set global filters (we will not filter by year)
ghcndextractor.countries = ["US"]
ghcndextractor.states = ["NJ"]     

ghcndextractor.ghcnFolder = "/Users/davidstocker/Documents/Desktop"   
 
ghcndextractor.readStationsFile()
ghcndextractor.readDailyFiles()
dayCSV = ghcndextractor.getDailyDataCSV(["12"], ["25"], ["USW00014780"])
dayDictList= ghcndextractor.getDailyData(["12"], ["25"], ["USW00014780"])
```
