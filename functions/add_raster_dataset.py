# ---------------------------------------------------------------------------
# add_raster_dataset
# Last updated: 2022-04-20
# Authors: Mariel Sorlien
#
# Description:
# Helper functions to import and process raster datasets for ejmap_step2
# ---------------------------------------------------------------------------

import arcpy
from arcpy.sa import *
import pandas as pd
import numpy as np

# Set variables
temp_raster = arcpy.env.scratchFolder + '/temp_raster.tif'
temp_table = arcpy.env.scratchFolder + '/temp_table.dbf'
temp_excel = arcpy.env.scratchFolder + '/temp_excel.xls'

# --------------------- add_raster_dataset -----------------------------
# Calculate zonal statistics, save as csv


def add_raster_dataset(gis_block_groups, raster_input, csv_output):
    print('Removing null data')
    raster_extract = ExtractByAttributes(raster_input, "VALUE < 101")
    raster_extract.save(temp_raster)
    print('Calculating zonal statistics')
    ZonalStatisticsAsTable(in_zone_data=gis_block_groups,
                           zone_field='GEOID',
                           in_value_raster=temp_raster,
                           out_table=temp_table,
                           statistics_type='MEAN')

    print('Exporting to excel')
    arcpy.conversion.TableToExcel(Input_Table=temp_table,
                                  Output_Excel_File=temp_excel)
    print('Converting to csv')
    # Read in excel as dataframe
    df = pd.read_excel(temp_excel)
    # Save as csv
    df.to_csv(csv_output, index=False)

# ----------------------- process_raster_csv -----------------------------
# Calculate average value per unit land


def process_raster_csv(csv_input, block_groups, metric, csv_output):
    print('Opening csv file')
    df = pd.read_csv(csv_input, sep=",")
    print('Merging with block group data to add ALAND, AWATER columns')
    # Drop extra columns
    block_groups = block_groups[['GEOID', 'ALAND', 'AWATER']]
    # Merge
    df_merge = pd.merge(df, block_groups, how="left", on='GEOID')
    print('Adding column "' + metric + '", setting to average value per unit land')
    # MEAN/100 * LAND/(LAND+WATER) --- normalizes data as value from 0 to 1
    df_merge[metric] = (df_merge['MEAN'] / 100) * (df_merge['ALAND'] / (df_merge['ALAND'] + df_merge['AWATER']))
    print('Dropping extra columns')
    df_merge = df_merge[['GEOID', metric]]
    print('Saving csv')
    df_merge.to_csv(csv_output, index=False)
