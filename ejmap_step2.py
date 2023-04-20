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

from functions.add_csv_dataset import add_csv_dataset
from functions.add_csv_dataset import add_first_street_data
from functions.add_raster_dataset import add_raster_dataset
from functions.add_raster_dataset import process_raster_csv
from functions.add_metadata import add_metadata_fields

arcpy.env.overwriteOutput = True

# ------------------------------ STEP 1 -------------------------------------
# Set workspace, projection, initial variables (MANDATORY)

# Set workspace
base_folder = os.getcwd()
gis_folder = base_folder + '/gis_data/int_gisdata/ejmap_intdata.gdb'
csv_folder = base_folder + '/tabular_data'

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

# Set variables
state_list = ['Rhode Island', 'Connecticut', 'Massachusetts']
gis_block_groups = gis_folder + '/MACTRI_block_groups'
keep_fields = ['ID', 'Town', 'State', 'Study_Area', 'ALAND', 'AWATER']

# Set outputs
tsv_output = csv_folder + '/block_groups_final.tsv'
gis_output = gis_folder + '/block_groups_final'

# ------------------------------ STEP 2 -------------------------------------
# Add EPA data (MANDATORY)

# Set variables
epa_csv = csv_folder + "/source_data/EJSCREEN_2022_StatePct_with_AS_CNMI_GU_VI.csv"

# List metrics
epa_metrics = ['MINORPCT', 'LOWINCPCT', 'UNEMPPCT', 'LINGISOPCT', 'LESSHSPCT',
               'UNDER5PCT', 'OVER64PCT', 'PM25', 'OZONE', 'DSLPM', 'PTRAF',
               'PRE1960PCT', 'PNPL', 'PRMP', 'PTSDF', 'UST', 'PWDIS']

# Rename metrics. Must be 8 characters max.
# old name: new name
rename_epa_metrics = {'LOWINCPCT': 'LWINCPCT',
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
add_noaa_sea_level_rise = True
add_first_street_flood = True
add_first_street_heat = True

# Indicate whether to process raster datasets OR use csv summary file instead
process_raster_trees = True
process_raster_impervious = True

# List inputs
cdc_csv = csv_folder + '/source_data/PLACES__Census_Tract_Data__GIS_Friendly_Format___2022_release.csv'
tree_raster = gis_folder + '/nlcd_2016_treecanopy'
impervious_surface_raster = gis_folder + '/nlcd_2019_impervious'
noaa_sea_level_rise_0ft = gis_folder + '/source_data/noaa_slr_depth_0ft'
noaa_sea_level_rise_low = gis_folder + '/source_data/noaa_slr_depth_1ft'  # Target sea level rise rounded down
noaa_sea_level_rise_high = gis_folder + '/source_data/noaa_slr_depth_2ft'  # Target sea level rise rounded up
first_street_flood = csv_folder + '/source_data/flood_v2.1_summary_fsf_flood_tract_summary.csv'
first_street_heat = csv_folder + '/source_data/heat_v1.1_summary_fsf_heat_tract_summary.csv'

# List outputs
tree_csv = csv_folder + '/int_data/nlcd_tree.csv'
impervious_surface_csv = '/int_data/nlcd_impervious.csv'

# Set variables
sea_level_rise_depth_ft = 1.6
cdc_metrics = ['CASTHMA_CrudePrev', 'BPHIGH_CrudePrev', 'CANCER_CrudePrev',
               'DIABETES_CrudePrev', 'MHLTH_CrudePrev']

# Set new variable names. Must be 8 characters max.
# old name: new name
rename_cdc_metrics = {'CASTHMA_CrudePrev': 'ASTHMA',
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

data_source = 'EPA; CDC; NLCD; NLCD, USFS; RIGIS; First Street; NOAA'
source_year = '2016-2020, 2022; 2019, 2020; 2019; 2016; 2021; 2022; 2019'

# ---------------------------- RUN SCRIPT -----------------------------------

# Step 1 ----
# Define extra variables
block_groups_xls = arcpy.env.scratchFolder + '/block_groups.xls'
temp_csv = arcpy.env.scratchFolder + '/rewrite.csv'
dataset_list = []

print('Processing block group data')
print('Exporting table to excel')
arcpy.conversion.TableToExcel(gis_block_groups, block_groups_xls)
print('Converting to dataframe')
df_bg = pd.read_excel(block_groups_xls)
print('Dropping extra columns')
df_bg = df_bg[keep_fields]
print('Adding column for tract ID')
df_bg['Tract_ID'] = df_bg['Block_Group'].astype(str)
df_bg['Tract_ID'] = df_bg.Tract_ID.str[:-1]
df_bg['Tract_ID'] = df_bg['Tract_ID'].astype(float)

# Step 2 ----
print('\nProcessing EPA data')
# Import csv, drop extra data, rename columns, save as temp  csv
add_csv_dataset(epa_csv, epa_metrics, rename_epa_metrics,
                ['ID', 'STATE_NAME', 'ACSTOTPOP'],
                state_list, 'STATE_NAME', temp_csv)
print('Rereading file')
df_epa = pd.read_csv(temp_csv, sep=",")
print('Adding variable names to list')
all_metrics = list(map(rename_epa_metrics.get, epa_metrics, epa_metrics))

# Step 3 ----
if add_cdc is True:
    print('\nProcessing CDC data')
    # Import csv, drop extra data, rename columns, save as temp  csv
    add_csv_dataset(cdc_csv, cdc_metrics, rename_cdc_metrics,
                    ['TractFIPS', 'StateDesc'],
                    state_list, 'StateDesc', temp_csv)
    print('Rereading file')
    df_cdc = pd.read_csv(temp_csv, sep=",")
    print('Adding variable names to list')
    all_metrics += list(map(rename_cdc_metrics.get, cdc_metrics, cdc_metrics))
    dataset_list += ['df_cdc']

if add_nlcd_tree is True:
    print('\nProcessing NLCD tree data')
    if process_raster_trees is True:
        # Process raster, save output as csv
        add_raster_dataset(gis_block_groups, tree_raster, tree_csv)
    # Process csv data
    process_raster_csv(tree_csv, 'TREE', temp_csv)
    print('Rereading file')
    df_tree = pd.read_csv(temp_csv, sep=",")
    print('Adding variable names to list')
    all_metrics += ['TREE']
    dataset_list += ['df_tree']

if add_nlcd_impervious_surface is True:
    print('\nProcessing NLCD impervious data')
    if process_raster_impervious is True:
        # Process raster, save output as csv
        add_raster_dataset(gis_block_groups, impervious_surface_raster, impervious_surface_csv)
    # Process csv data
    process_raster_csv(impervious_surface_csv, 'IMPER', temp_csv)
    print('Rereading file')
    df_imper = pd.read_csv(temp_csv, sep=",")
    print('Adding variable names to list')
    all_metrics += ['IMPER']
    dataset_list += ['df_imper']

# if add_noaa_sea_level_rise is True:
#     print('\nProcessing NOAA sea level data')

if add_first_street_flood is True:
    print('\nProcessing First Street flood data')
    add_first_street_data(first_street_flood, 'flood', temp_csv)
    print('Rereading file')
    df_flood = pd.read_csv(temp_csv, sep=",")
    print('Adding variable names to list')
    all_metrics += ['FLOOD']
    dataset_list += ['df_flood']

if add_first_street_heat is True:
    print('\nProcessing first street heat data')
    add_first_street_data(first_street_heat, 'heat', temp_csv)
    print('Rereading file')
    df_heat = pd.read_csv(temp_csv, sep=",")
    print('Adding variable names to list')
    all_metrics += ['HEAT']
    dataset_list += ['df_heat']

# Step 4 ----
