# BIOPAMA Protection Analyst
### Calculates Protected Areas coverage and protection percentage in Country and EEZ

**The script produces a vector layer, based on your input, containg the results of the spatial statistic performed, including protected area coverage and protected area coverage percentage**

If you have a postgres database connected to your Qgis environment, the script will also load your output in it.

### 1. What is included and not included in the calculation
- Only sites with Status = designated, inscribed, adopted and established are included.
- Only points with a Reported Area are included.
- Sites with Status = Proposed, Not Reported; points with no reported area, and UNESCO Man and Biosphere Reserves are excluded as specified in protectedplanet.net

## Method used to calculate national protected area coverage
This is a step by step guide on how to calculate national protected areas coverage.
*The statistics are computed using **Mollweide projection**, witch is an equal area projection, particularly known for its accuracy of proportions in area.*
___________________________________________________________________________
### 2. Steps
- [x] Dowload World Database on Protected Areas (WDPA) from https://www.protectedplanet.net/ .
- [x] Donload GAUL and EEZ form this repository.
- [x] Add layers to QGIS.
- [x] Fix the WDPA polygon geometries.
- [x] It is suggested to create a spatial index on the WDPA Polygons to speed up the process.
- [x] Run 'protection_levels.py' in Qgis.
- [x] Explore results!
![map](https://raw.githubusercontent.com/BIOPAMA/protection_analyst/main/img/WDPA.png)
___________________________________________________________________________
### 3. What the algorithm does 
- [x] Filter out the parameters specified in point 1.
- [x] Fix geometries.
- [x] Create a buffer around protected areas reported as points. The area of the buffer is = Reported Area. 
- [x] Merge buffered WDPA point and WDPA polygons to combine them into one single feature dataset.
- [x] Calculates protected area coverage in GAUL or EEZ and regional levels.
- [x] Calculates protected area percentage in GAUL or EEZ and regional levels.
- [x] Calculates number of protected areas by category in GAUL or EEZ and regional levels.
- [x] Calculates number of protected areas by IUCN category at regional level
- [x] Calculates number of protected areas by Governance Type at regional level
- [x] Calculates number of protected areas by Designation at regional level
___________________________________________________________________________


*The terrestrial protected area coverage is calculated for each country or territory by dividing the total area of terrestrial protected areas by total terrestrial area of that country.
The marine and coastal protected area coverage is calculated for each country or territory by dividing the total marine and coastal area of protected areas by total marine and coastal area of that country.*




