# ---------------------------------------------------------------------------
# add_raster_dataset
# Last updated: 2022-04-19
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
temp_raster = arcpy.env.scratchGDB + '/temp_raster'
temp_table = arcpy.env.scratchGDB + '/temp_table'
temp_excel = arcpy.env.scratchFolder + '/temp_excel'

# --------------------- add_raster_dataset -----------------------------
# Calculate zonal statistics, save as csv


def add_raster_dataset(gis_block_groups, raster_input, csv_output):
    print('Removing null data')
    raster_extract = ExtractByAttributes(raster_input, "VALUE < 101")
    raster_extract.save(temp_raster)
    print('Calculating zonal statistics')
    ZonalStatisticsAsTable(in_zone_data=gis_block_groups,
                           zone_field='ID',
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


def process_raster_csv(csv_input, metric, csv_output):
    print('Opening csv file')
    df = pd.read_csv(csv_input, sep=",")
    print('Adding column "' + metric + '", setting to average value per unit land')
    # MEAN/100 * LAND/(LAND+WATER) --- normalizes data as value from 0 to 1
    df[metric] = (df['MEAN'] / 100) * (df['ALAND'] / (df['ALAND'] + df['AWATER']))
    print('Dropping extra columns')
    df = df[['ID', metric]]
    print('Saving csv')
    df.to_csv(csv_output, index=False)
