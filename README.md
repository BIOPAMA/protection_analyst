# Protection Analyst
### Calculates Protected Areas coverage and protection percentage in Country and EEZ




## Method used to calculate national protected area coverage
This is a step by step guide on how to calculate national protected areas coverage.

### 1. What is included in the calculation
- Only sites with Status = designated, inscribed, adopted and established are included.
- Only points with a Reported Area are included.
- Sites with Status = Proposed, Not Reported; points with no reported area, and UNESCO Man and Biosphere Reserves are excluded as specified in protectedplanet.net
___________________________________________________________________________
*The statistics are computed using **Mollweide projection**, witch is an equal area projection, particularly known for its accuracy of proportions in area.*
___________________________________________________________________________
### 2. Steps
- [x] Dowload World Database on Protected Areas (WDPA) from https://www.protectedplanet.net/ 
- [x] Donload GAUL and EEZ form this repository
- [x] Add layers to QGIS
![map](https://raw.githubusercontent.com/BIOPAMA/protection_analyst/main/img/WDPA.png)
- [x] It is suggested to create a spatial index on the WDPA Polygons to speed up the process
- [x] Run 'protection_levels.py' in Qgis

### 3. What the algorithm does 
- [x] Filter out the above parameters
- [x] Fix geometries
- [x] Create a buffer around protected areas reported as points. The area of the buffer is = Reported Area. 
- [x] Merge buffered point and polygons to combine them into one single feature dataset.
- [x] Calculate protected area coverage in GAUL or EEZ
- [x] Calculate protected area percentage in GAUL or EEZ
- [x] Load results in a postgres database

___________________________________________________________________________

**The script produces a spatial vector layer based on your input choice containg the results of the spatial statistic performed including protected area coverage and protected area coverage percentage**

*The terrestrial protected area coverage is calculated for each country or territory by dividing the total area of terrestrial protected areas by total terrestrial area of that country.
The marine and coastal protected area coverage is calculated for each country or territory by dividing the total marine and coastal area of protected areas by total marine and coastal area of that country.*
___________________________________________________________________________

Author: Luca Battistella (EC-JRC)


