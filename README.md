# EJmap_prep
Supplements [EJScreen](https://www.epa.gov/ejscreen) data with additional datasets and calculates state and study area 
level percentiles. Outputs shapefile and csv files that can be used for [EJMap](https://github.com/NBEP/EJmap).

# How To Use
Standard users should run ejmap_step1 and ejmap_step2. 

NBEP staff should run ejmap_step1, ejmap_step1b_NBEP, ejmap_step2, and ejmap_step2b_NBEP. 

## Prerequisites
These scripts use python 3.7, ArcGIS Pro 3.1.0, and ArcGIS Spatial Analyst.

# Scripts

## ejmap_step1.py
Adds town, watershed, and study area values to block group data. 

### Datasets
- [US Census TIGER/Line Shapefiles](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html)
- [USGS Watershed Boundary Dataset](https://www.usgs.gov/national-hydrography/access-national-hydrography-products)

## ejmap_step1b_NBEP.py
Adds metadata.

## ejmap_step2.py
Combines datasets and calculates state and study area level percentiles.

### Datasets
- [EPA EJScreen](https://gaftp.epa.gov/EJSCREEN/) 
  - Download csv of state percentiles that does NOT end in _tracts
- [CDC PLACES](https://www.cdc.gov/places/index.html)
- [NLCD Tree Canopy](https://www.mrlc.gov/data)
- [NLCD Urban Imperviousness](https://www.mrlc.gov/data)
- [NOAA Sea Level Rise](https://coast.noaa.gov/slrdata/) 
  - Download "Sea Level Rise", not "Sea Level Rise Depth" 
- [First Street](https://firststreet.org/)

## ejmap_step2b_NBEP.py
Clips data to NBEP towns, adds metadata, and generates a simplified map for display purposes. 

# Acknowledgements
This project was funded by agreements by the Environmental Protection Agency (EPA) to Roger Williams University (RWU) 
in partnership with the Narragansett Bay Estuary Program. Although the information in this document has been funded 
wholly or in part by EPA under the agreements CE00A00967 to RWU, it has not undergone the Agency’s publications review 
process and therefore, may not necessarily reflect the views of the Agency and no official endorsement should be 
inferred. The viewpoints expressed here do not necessarily represent those of the Narragansett Bay Estuary Program, 
RWU, or EPA nor does mention of trade names, commercial products, or causes constitute endorsement or recommendation 
for use.