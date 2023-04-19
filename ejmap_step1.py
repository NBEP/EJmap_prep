# ---------------------------------------------------------------------------
# ejmap_step1.py
# Authors: Mariel Sorlien
# Last updated: 2023-04-19
# Python 3.7
#
# Description:
# Adds town, watershed, and study area data to census block groups.
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

import arcpy
import os

from functions.add_metadata import add_metadata_fields
from functions.refine_block_groups import block_group_spatial_join

arcpy.env.overwriteOutput = True

# ------------------------------ STEP 1 -------------------------------------
# Set workspace, projection, initial variables (MANDATORY)

# Set workspace
base_folder = os.getcwd()
gis_folder = base_folder + '/gis_data/int_gisdata/ejmap_intdata.gdb'
output_folder = base_folder + '/data'

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

# Set inputs
gis_block_groups = gis_folder + '/source_data/block_groups'
keep_fields = ['GEOID', 'ALAND', 'AWATER']

# Set output
gis_output = gis_folder + '/block_groups_copy'

# ------------------------------ STEP 2 -------------------------------------
# Add towns, watersheds, study area (optional)

# Set options
add_town_names = True
add_watershed_names = True
add_study_area = True

# Set inputs
gis_towns = gis_folder + '/source_data/towns'
town_columns = ['Town', 'State']
gis_watersheds = gis_folder + '/source_data/watersheds'
watershed_columns = ['huc10', 'name']
gis_study_area = gis_folder + '/source_data/NBEP_study_areas'
study_area_columns = ['Study_Area']

# ------------------------------ STEP 3 -------------------------------------
# Add metadata (mandatory)

data_source = 'Census; MassGIS; RIGIS; CTDEEP; USGS WBD; NBEP'
source_year = '2022; 2013, 2014, 2020; 2016, 2014; 2005, 2006; 2023; 2017'

# ---------------------------- RUN SCRIPT -----------------------------------

# Add towns
if add_town_names is True:
    print('\nAdding town names')
    # Add spatial join
    block_group_spatial_join(gis_block_groups, gis_towns, gis_output)
    gis_block_groups = gis_output
    print('Updating column list')
    keep_fields += town_columns

if add_watershed_names is True:
    print('\nAdding watershed names')
    # Add spatial join
    block_group_spatial_join(gis_block_groups, gis_watersheds, gis_output)
    gis_block_groups = gis_output
    print('Updating column list')
    keep_fields += watershed_columns

if add_study_area is True:
    print('\nAdding study area names')
    # Add spatial join
    block_group_spatial_join(gis_block_groups, gis_study_area, gis_output)
    gis_block_groups = gis_output
    print('Updating column list')
    keep_fields += study_area_columns

if gis_block_groups != gis_output:
    print('\nSaving output')
    arcpy.management.CopyFeatures(gis_block_groups, gis_output)

print('\nDropping extra columns')
arcpy.management.DeleteField(gis_output, keep_fields, 'KEEP_FIELDS')

print('Adding columns (DataSource, SourceYear)')
add_metadata_fields(gis_output, data_source, source_year)
