# ---------------------------------------------------------------------------
# calculate_sea_level_rise
# Last updated: 2022-04-20
# Authors: Mariel Sorlien
#
# Description:
# Helper functions to process NOAA sea level rise data for ejmap_step2
# ---------------------------------------------------------------------------

import arcpy
import pandas as pd

# Temp values
temp_shp = arcpy.env.scratchFolder + '/temp_shapefile.shp'
temp_shp2 = arcpy.env.scratchFolder + '/temp_shapefile2.shp'

# --------------------- add_csv_dataset -----------------------------


def intersect_slr_block_groups(slr_input, slr_erase, bg_input, excel_output):
    print('Erasing areas that overlap next lowest flood level')
    # Avoid double count from overlapping areas
    arcpy.analysis.Erase(in_features=slr_input,
                         erase_features=slr_erase,
                         out_feature_class=temp_shp)
    print('Intersecting SLR, block groups')
    arcpy.analysis.Intersect(in_features=[temp_shp, bg_input],
                             out_feature_class=temp_shp2)
    print('Dissolving data')
    # Ensure one multipart feature per block group -- prevents big problems later
    arcpy.management.Dissolve(in_features=temp_shp2,
                              out_feature_class=temp_shp,
                              dissolve_field=['GEOID', 'ALAND'])
    print('Calculating area (square meters)')
    arcpy.management.AddField(in_table=temp_shp,
                              field_name='ASLR',
                              field_type='FLOAT')
    arcpy.management.CalculateGeometryAttributes(in_features=temp_shp,
                                                 geometry_property=[['ASLR', 'AREA']],
                                                 area_unit='SQUARE_METERS')
    print('Dropping extra fields')
    arcpy.management.DeleteField(in_table=temp_shp,
                                 drop_field=['GEOID', 'ALAND', 'ASLR'],
                                 method='KEEP_FIELDS')
    print('Exporting data to excel')
    arcpy.conversion.TableToExcel(Input_Table=temp_shp,
                                  Output_Excel_File=excel_output)
