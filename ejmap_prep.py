# ---------------------------------------------------------------------------
# ejmap_prep.py
# Authors: Mariel Sorlien
# Last updated: 2023-04-12
# Python 3.7
#
# Description:
# Combines multiple datasets and calculates state and study area percentiles
# Preps data for NBEP/EJmap
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

import arcpy
import os
import pandas as pd

from functions.block_groups import refine_block_groups

arcpy.env.overwriteOutput = True

# ------------------------------ STEP 1 -------------------------------------
# Set workspace, projection, initial variables (MANDATORY)

# Set workspace
base_folder = os.getcwd()
gis_folder = os.path.join(base_folder, 'gis', 'ejmap_prep.gdb')
csv_folder = os.path.join(base_folder, 'data-raw')
output_folder = os.path.join(base_folder, 'data')

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

# Set variables
state_list = ['Rhode Island', 'Connecticut', 'Massachusetts']
gis_block_groups = os.path.join(gis_folder, 'block_groups')
clip_output_to_study_area = True

# Set metadata (block groups)
data_source = 'Census'
source_year = '2022'


# ------------------------------ STEP 2 -------------------------------------
# Refine block group data

# Set options
add_town_names = True
add_watershed_names = True
add_study_area = True
clip_to_land = True

# Set inputs
gis_towns = ''
gis_watersheds = os.path.join(gis_folder, 'watersheds')
gis_study_area = ''

# Set output
gis_block_groups_2 = os.path.join(gis_folder, 'block_groups_copy')

# Set metadata
step2_data_source = 'USGS'
step2_source_year = '2023'

# ------------------------------ STEP 3 -------------------------------------
# Add EPA data (MANDATORY)

# ------------------------------ STEP 4 -------------------------------------
# Add supplemental datasets

# ------------------------------ STEP 5 -------------------------------------
# Calculate percentiles, add metadata

calculate_state_percentiles = True
calculate_study_area_percentiles = True

# ---------------------------- RUN SCRIPT -----------------------------------

# Step 2 ----
if add_town_names is True or add_watershed_names is True or add_study_area is True or clip_to_land is True:
    print('REFINING BLOCK GROUPS')
    # Update block group data
    refine_block_groups(add_town_names, add_watershed_names, add_study_area, clip_to_land,
                        gis_block_groups, gis_towns, gis_watersheds, gis_study_area)
    gis_block_groups = gis_block_groups_2
    # Update metadata
    data_source += "; " + step2_data_source
    source_year += "; " + step2_source_year

# Step 3 ----

# Step 4 ----

# Step 5 ----
