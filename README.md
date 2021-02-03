# Protection Analyst
###Calculates Protected Areas coverage and percentage in Country and EEZ




##Method used to calculate national protected area coverage
This is a step by step guide on the method used to calculate national protected areas coverage and it is copliant with the process reported in www.protectedplanet.net. 

This methodology was originally designed to be run in ArcGIS, and has been converted here as a Python/Qgis script.

###What is included in the calculation
*Only sites with Status = designated, inscribed, adopted and established are included.*
*Only points with a Reported Area are included.*
*Sites with Status = Proposed, Not Reported; points with no reported area, and UNESCO Man and Biosphere Reserves (see reasons above in Section 2) are excluded.*

###Steps
- [x]Dowload World Database on Protected Areas (WDPA) from https://www.protectedplanet.net/ 
- [x]Donload GAUL and EEZ form this repository
- [x]Add layers to QGIS
![map](https://raw.githubusercontent.com/BIOPAMA/protection_analyst/main/WDPA.png)
- [x]It is suggested to create a spatial index on the WDPA Polygons to speed up the process
- [x]Run 'protection_levels.py' in Qgis

### What the algorithm does 
- [x]Filter out the above parameters
- [x]Fixes geometries
- [x]Create a buffer around protected areas reported as points. The area of the buffer is = Reported Area. 
- [x]Merge buffered point and polygons to combine them into one single feature dataset.
- [x]Calculates protected area coverage in GAUL or EEZ
- [x]Calculates protected area percentage in GAUL or EEZ
- [x]Load results in a postgres database


*The terrestrial protected area coverage is calculated for each country or territory by dividing the total area of terrestrial protected areas by total terrestrial area of that country.
The marine and coastal protected area coverage is calculated for each country or territory by dividing the total marine and coastal area of protected areas by total marine and coastal area of that country.*




