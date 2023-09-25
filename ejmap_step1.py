# ---------------------------------------------------------------------------
# ejmap_step1.py
# Authors: Mariel Sorlien
# Last updated: 2023-08-30
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
from functions.replace_null_gis import replace_null_in_field

arcpy.env.overwriteOutput = True

# ------------------------------ STEP 1 -------------------------------------
# Set workspace, projection, initial variables (MANDATORY)

# Set workspace
base_folder = os.getcwd()
scratch_folder = arcpy.env.scratchFolder
gis_folder = base_folder + '/gis_data/int_gisdata/ejmap_intdata.gdb'

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('NAD 1983 UTM Zone 19N')

# Set inputs
gis_block_groups = gis_folder + '/source_data/block_groups'
keep_fields = ['GEOID', 'ALAND', 'AWATER']

# Set output
gis_output = gis_folder + '/RICTMA_BlockGroups_2020_NBEP2023'

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

# Change column names --- old columns: new column
new_column_names = {
    'huc10': 'HUC10',
    'name': 'HUC10_Name'
}

# ------------------------------ STEP 3 -------------------------------------
# Add metadata (mandatory)

data_source = 'US Census; MassGIS; RIGIS; CTDEEP; USGS WBD; NBEP'
source_year = '2020; 2021; 2001; 2005; 2023; 2017'

# ---------------------------- RUN SCRIPT -----------------------------------

# Add towns
if add_town_names is True:
    print('Adding town names')
    # Add spatial join
    block_group_spatial_join(gis_block_groups, gis_towns, '', gis_output)
    # Replace null/blank values
    replace_null_in_field(
        in_table=gis_output,
        fields=town_columns,
        new_text='No Data')
    # Update gis_block_groups
    gis_block_groups = gis_output
    print('Updating column list')
    keep_fields += town_columns

if add_watershed_names is True:
    print('\nAdding watershed names')
    # Add spatial join
    block_group_spatial_join(gis_block_groups, gis_watersheds, watershed_columns, gis_output)
    # Update gis_block_groups
    gis_block_groups = gis_output
    print('Updating column list')
    keep_fields += watershed_columns

if add_study_area is True:
    print('\nAdding study area names')
    # Add spatial join
    block_group_spatial_join(gis_block_groups, gis_study_area, study_area_columns, gis_output)
    # Replace null/blank values
    replace_null_in_field(
        in_table=gis_output,
        fields=study_area_columns,
        new_text='Outside Study Area')
    # Update gis_block_groups
    gis_block_groups = gis_output
    print('Updating column list')
    keep_fields += study_area_columns

if gis_block_groups != gis_output:
    print('\nSaving output')
    arcpy.management.CopyFeatures(gis_block_groups, gis_output)

print('\nDropping extra columns')
arcpy.management.DeleteField(gis_output, keep_fields, 'KEEP_FIELDS')

if len(new_column_names) > 0:
    print('Renaming columns')
    for old_name, new_name in new_column_names.items():
        # Check if old and new name match, ignoring case
        # If yes - replace old name with 'temp_name'
        if old_name.lower() == new_name.lower():
            arcpy.management.AlterField(
                in_table=gis_output,
                field=old_name,
                new_field_name='temp_name')
            old_name = 'temp_name'
        # Replace old name with new name
        arcpy.management.AlterField(
            in_table=gis_output,
            field=old_name,
            new_field_name=new_name,
            new_field_alias=new_name)

print('Adding columns (DataSource, SourceYear)')
add_metadata_fields(gis_output, data_source, source_year)

print('\nDeleting scratch folder')
arcpy.Delete_management(scratch_folder)
