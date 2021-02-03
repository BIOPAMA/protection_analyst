# Protection Analyst
Calculates Protected Areas coverage and percentage in Country and EEZ
1. Dowload World Database on Protected Areas (WDPA) from https://www.protectedplanet.net/ 
2. Donload GAUL and EEZ form this repository
3. Add layers to QGIS
![map](https://raw.githubusercontent.com/BIOPAMA/protection_analyst/main/WDPA.png)
4. It is suggested to create a spatial index on the WDPA Polygons to speed up the process
![map](https://raw.githubusercontent.com/BIOPAMA/protection_analyst/main/spatial_index.png)
5. Run 'protection_levels.py' in Qgis
6. If you need to load the results in your database, please provide the connection parameters to the script.
