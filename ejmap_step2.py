# ---------------------------------------------------------------------------
# ejmap_step1.py
# Authors: Mariel Sorlien
# Last updated: 2023-04-19
# Python 3.7
#
# Description:
# Combines multiple datasets and calculates state and study area percentiles
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

import arcpy
import os
import pandas as pd

from functions.add_metadata import add_metadata_fields

arcpy.env.overwriteOutput = True

# ------------------------------ STEP 1 -------------------------------------
# Set workspace, projection, initial variables (MANDATORY)

# Set workspace
base_folder = os.getcwd()
gis_folder = base_folder + '/gis_data/int_gisdata/ejmap_prep.gdb'
csv_folder = base_folder + '/tabular_data'

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

# Set variables
state_list = ['Rhode Island', 'Connecticut', 'Massachusetts']
gis_block_groups = gis_folder + '/MACTRI_block_groups'

# ------------------------------ STEP 2 -------------------------------------
# Add EPA data (MANDATORY)

# Set variables
epa_csv = csv_folder + "/source_data/EJSCREEN_2022_StatePct_with_AS_CNMI_GU_VI.csv"

# List metrics
epa_metrics = ['MINORPCT', 'LOWINCPCT', 'UNEMPPCT', 'LINGISOPCT', 'LESSHSPCT',
               'UNDER5PCT', 'OVER64PCT', 'PM25', 'OZONE', 'DLPM', 'PTRAF',
               'PRE1960PCT', 'PNPL', 'PRMP', 'PTSDF', 'UST', 'PWDIS']
# Set new variable names. Must be 8 characters max.
# old name: new name
rename_epa_columns = {'LOWINCPCT': 'LWINCPCT',
                      'LESSHSPCT': 'LESHSPCT',
                      'LINGISOPCT': 'LNGISPCT',
                      'UNDER5PCT': 'UNDR5PCT',
                      'OVER64PCT': 'OVR64PCT',
                      'PRE1960PCT': 'LDPNT'
                      }

# ------------------------------ STEP 3 -------------------------------------
# Add supplemental datasets

# Indicate which datasets to include
add_cdc = True
add_nlcd_tree = True
add_nlcd_impervious_surface = True
add_noaa_sea_level_rise_raster = True
add_first_street_flood = True
add_first_street_heat = True
add_first_street_fire = False

# Indicate whether raster datasets have already been processed
# If false will use csv output instead
process_raster_trees = True
process_raster_impervious = True
process_raster_sea = True

# List inputs
cdc_csv = csv_folder + '/source_data/PLACES__Census_Tract_Data__GIS_Friendly_Format___2022_release.csv'
tree_raster = ''
impervious_surface_raster = ''
sea_level_rise_raster = ''
first_street_flood = ''
first_stree_heat = ''
first_street_fire = ''

# List outputs
tree_csv = ''
impervious_surface_csv = ''
sea_level_rise_csv = ''

# List metrics
cdc_metrics = ['CASTHMA_CrudePrev', 'BPHIGH_CrudePrev', 'CANCER_CrudePrev',
               'DIABETES_CrudePrev', 'MHLTH_CrudePrev']
# Set new variable names. Must be 8 characters max.
# old name: new name
rename_cdc_columns = {'CASTHMA_CrudePrev': 'ASTHMA',
                      'BPHIGH_CrudePrev': 'BPHIGH',
                      'CANCER_CrudePrev': 'CANCER',
                      'DIABETES_CrudePrev': 'DIABE',
                      'MHLTH_CrudePrev': 'MHEALTH'
                      }

# ------------------------------ STEP 4 -------------------------------------
# Calculate percentiles, add metadata

calculate_state_percentiles = True
calculate_study_area_percentiles = True

study_area_column = 'Study_Area'
study_area_values = ['Narragansett Bay Watershed', 'Little Narragansett Bay Watershed',
                     'Southwest Coastal Ponds Watershed']

data_source = ''
source_year = ''

# ---------------------------- RUN SCRIPT -----------------------------------

# Step 2 ----

# Step 3 ----

# Step 4 ----
