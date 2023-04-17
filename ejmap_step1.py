# ---------------------------------------------------------------------------
# ejmap_step1.py
# Authors: Mariel Sorlien
# Last updated: 2023-04-12
# Python 3.7
#
# Description:
# Adds town, watershed, and study area data to census block groups.
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
gis_folder = base_folder + '/gis_data/int_gisdata/ejmap_intdata.gdb'
output_folder = base_folder + '/data'

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

# Set variables
gis_block_groups = gis_folder + '/source_data/block_groups'
keep_fields = ['GEOID', 'ALAND', 'AWATER']

# Set output
gis_output = gis_folder + '/block_groups_copy'

# Set metadata (block groups)
data_source = 'Census'
source_year = '2022'

# ------------------------------ STEP 2 -------------------------------------
# Add town names

# Set options
add_town_names = True

# Set inputs
gis_towns = gis_folder + '/source_data/towns'
town_columns = ['Town', 'State']

# Set metadata
town_data_source = 'MassGIS; RIGIS; CTDEEP'
town_source_year = '2013, 2014, 2020; 2016, 2014; 2005, 2006'

# ------------------------------ STEP 3 -------------------------------------
# Add watershed name

# Set options
add_watershed_names = True

# Set inputs
gis_watersheds = gis_folder + '/source_data/watersheds'
watershed_columns = ['huc10', 'name']

# Set metadata
watershed_data_source = 'USGS WBD'
watershed_source_year = '2023'

# ------------------------------ STEP 4 -------------------------------------
# Add study area

# Set options
add_study_area = True

# Set inputs
gis_study_area = gis_folder + '/source_data/NBEP_study_areas'
study_area_columns = ['Study_Area']

# Set metadata
study_area_data_source = 'NBEP'
study_area_source_year = '2017'

# ---------------------------- RUN SCRIPT -----------------------------------

# Set additional variable names
gis_temp = arcpy.env.scratchFolder + '/blockgroup_join.shp'

# Add towns
if add_town_names is True:
    print('Adding town names')
    print('\tAdding spatial join')
    arcpy.analysis.SpatialJoin(target_features=gis_block_groups,
                               join_features=gis_towns,
                               out_feature_class=gis_temp,
                               match_option='LARGEST_OVERLAP')
    print('\tUpdating lists (metadata, columns)')
    data_source += "; " + town_data_source
    source_year += "; " + town_source_year
    keep_fields.append(town_columns)
    print('\tSaving data')
    arcpy.management.CopyFeatures(in_features=gis_temp,
                                  out_feature_class=gis_output)
    gis_block_groups = gis_output

if add_watershed_names is True:
    print('Adding watershed names')
    print('\tAdding spatial join')
    arcpy.analysis.SpatialJoin(target_features=gis_block_groups,
                               join_features=gis_watersheds,
                               out_feature_class=gis_temp,
                               match_option='LARGEST_OVERLAP')
    print('\tUpdating lists (metadata, columns)')
    data_source += "; " + watershed_data_source
    source_year += "; " + watershed_source_year
    keep_fields.append(watershed_columns)
    print('\tSaving data')
    arcpy.management.CopyFeatures(in_features=gis_temp,
                                  out_feature_class=gis_output)
    gis_block_groups = gis_output

if add_study_area is True:
    print('Adding study area names')
    print('\tAdding spatial join')
    arcpy.analysis.SpatialJoin(target_features=gis_block_groups,
                               join_features=gis_study_area,
                               out_feature_class=gis_temp,
                               match_option='LARGEST_OVERLAP')
    print('\tUpdating lists (metadata, columns)')
    data_source += "; " + study_area_data_source
    source_year += "; " + study_area_source_year
    keep_fields.append(study_area_columns)
    print('\tSaving data')
    arcpy.management.CopyFeatures(in_features=gis_temp,
                                  out_feature_class=gis_output)
    gis_block_groups = gis_output

if gis_block_groups != gis_output:
    print('Saving data')
    arcpy.management.CopyFeatures(in_features=gis_block_groups,
                                  out_feature_class=gis_output)

print('Dropping extra columns')
arcpy.management.DeleteField(in_table=gis_output,
                             drop_field=keep_fields,
                             method='KEEP_FIELDS')

print('Adding columns (DataSource, SourceYear)')
arcpy.management.AddFields(gis_output,
                           [
                               # Field name, field type, field alias, field length, default value
                               ['DataSource', 'TEXT', 'DataSource', 50],
                               ['SourceYear', 'TEXT', 'SourceYear', 50]
                           ])
arcpy.management.CalculateFields(gis_output,
                                 "PYTHON3",
                                 [
                                     ['DataSource', '"' + data_source + '"'],
                                     ['SourceYear', '"' + source_year + '"']
                                 ])
