# ---------------------------------------------------------------------------
# ej_step2_EPA
# Created on: 2022-11-16
# Last edited: 2022-12-13
# Authors: Mariel Sorlien
#
# Description:
# Step 2 to prep data for EJ tool. Combines multiple data sources, calculates state & NBEP percentiles.
# ---------------------------------------------------------------------------

import arcpy
import os
from arcpy.sa import *
import pandas as pd
import numpy as np

arcpy.env.overwriteOutput = True  # lets you overwrite existing files; does NOT work if files open elsewhere (eg GIS)

# -----------------------
# Set variables ---

# Set default workspace
baseFolder = r"C:\Users\msorlien\OneDrive - NBEP - RWU\Documents\GIS_PROJECTS\INTERNAL_PROJECTS\EJ_map_v2"
gdb_path = baseFolder + r'\Data\INT_GISDATA\ejtools_intdata.gdb'
csv_path = baseFolder + r'\Methods\Data'

# Set projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

# Set folder names
scratchFolder = 'scratch'
outputFolder = csv_path + '/final_data'

# Set variable names
# For blockgroup data
tracts_csv = csv_path + '/int_data/state_tracts.csv'
tracts_state = 'clipped_data/EJSCREEN_tracts_state'
tracts_NBEP = 'clipped_data/EJSCREEN_tracts_NBEP'

# Coastal boundaries
state_polygon = 'source_copy/StateLines_Polygon'

# EPA, CDC data
epa_csv = csv_path + "/raw_data/EJSCREEN_2022_StatePct_with_AS_CNMI_GU_VI.csv"
cdc_csv = csv_path + '/raw_data/PLACES__Census_Tract_Data__GIS_Friendly_Format___2022_release.csv'

# NLCD data
# NOTE: clip raster data and remove null data before running script!
nlcd_trees_raster = 'nlcd_2016_treecanopy_clip'
nlcd_trees = csv_path + '/int_data/trees.xls'
nlcd_impervious_raster = 'nlcd_2019_impervious_clip'
nlcd_impervious = csv_path + '/int_data/impervious.xls'

# Heat, flood data
flood_csv = csv_path + '/raw_data/flood_v2.1_summary_fsf_flood_tract_summary.csv'
heat_csv = csv_path + '/raw_data/heat_v1.1_summary_fsf_heat_tract_summary.csv'

# Sea level rise data
slr_1ft_RI = 'source_copy/RI_low_1ft'
slr_2ft_RI = 'source_copy/RI_low_2ft'
slr_1ft_MA = 'source_copy/MA_low_1ft'
slr_2ft_MA = 'source_copy/MA_low_2ft'
slr_1ft_CT = 'source_copy/CT_low_1ft'
slr_2ft_CT = 'source_copy/CT_low_2ft'

# Other
output_csv_all = csv_path + '/final_data/regional_EJdata.csv'
output_csv_NBEP = csv_path + '/final_data/NBEP_EJdata.csv'

# Toggle options
# True = calculate tree cover from raster, False = skip step and use nlcd_trees
process_raster_trees = False
# True = calculate impervious cover from raster, False = skip step and use nlcd_impervious
process_raster_impervious = False
# True = keep scratch folder, False = delete scratch folder
keep_temp_files = False

# ---------------------------------------------------------------------------
# Additional variables ---
arcpy.env.workspace = gdb_path
csv_scratch = os.path.join(csv_path, scratchFolder)
column_list = []

epa_csv_temp = os.path.join(csv_scratch, 'EPA_temp.csv')
cdc_csv_temp = os.path.join(csv_scratch, 'CDC_temp.csv')

nlcd_table_trees = 'nlcd_table_trees'
nlcd_table_impervious = 'nlcd_table_impervious'

parks_local_public = os.path.join(scratchFolder, 'parks_local_public')
parks_state_public = os.path.join(scratchFolder, 'parks_state_public')
parks_all = os.path.join(scratchFolder, 'parks_all')
parks_dissolve = os.path.join(scratchFolder, 'parks_dissolve')
parks_intersect = os.path.join(scratchFolder, 'parks_intersect')
parks_excel = os.path.join(csv_scratch, 'parks.xls')

slr_merge = os.path.join(scratchFolder, 'slr_merge')
slr_clip = os.path.join(scratchFolder, 'slr_clip')
slr_intersect = os.path.join(scratchFolder, 'slr_intersect')
slr_dissolve = os.path.join(scratchFolder, 'slr_dissolve')
slr_1ft_excel = os.path.join(csv_scratch, 'slr_1ft.xls')
slr_2ft_excel = os.path.join(csv_scratch, 'slr_2ft.xls')

nbep_excel = os.path.join(csv_scratch, 'nbep_excel.xls')

# ---------------------------------------------------------------------------
# Define functions ---

# ---------------------------------------------------------------------------
# Run Script ---

# Check for/add missing folders ---
print("CHECKING FILE PATHS")
new_folders = [scratchFolder]
for folder in new_folders:
    if not arcpy.Exists(folder):
        arcpy.CreateFeatureDataset_management(gdb_path, folder)
        print("Added gdb " + folder + " folder")
if not os.path.exists(csv_scratch):
    os.mkdir(csv_scratch)
    print("Added csv scratch folder")

print('\nPROCESSING BLOCK GROUP DATA')
print('Reading in csv')
df_tracts = pd.read_csv(tracts_csv,
                        sep=",")
print('Adding column for tract ID')
df_tracts['tract_ID'] = df_tracts['ID'].astype(str)
df_tracts['tract_ID'] = df_tracts.tract_ID.str[:-1]
df_tracts['tract_ID'] = df_tracts['tract_ID'].astype(float)

print('\nPROCESSING EPA DATA')
print('Reading in csv')
epa_columns = ['ID', 'STATE_NAME', 'ACSTOTPOP',
               'MINORPCT', 'LOWINCPCT', 'LESSHSPCT', 'LINGISOPCT', 'UNDER5PCT',
               'OVER64PCT', 'PRE1960PCT', 'UNEMPPCT', 'DSLPM',
               'PTRAF', 'PWDIS', 'PNPL', 'PRMP',
               'PTSDF', 'OZONE', 'PM25', 'UST']
# read in csv
df_epa = pd.read_csv(epa_csv,
                     sep=",",
                     usecols=epa_columns
                     )
print("Dropping extra rows")
df_epa = df_epa[(df_epa.STATE_NAME == "Rhode Island") |
                (df_epa.STATE_NAME == "Connecticut") |
                (df_epa.STATE_NAME == "Massachusetts")]
print('Renaming columns')
df_epa.rename(columns={'LOWINCPCT': 'LWINCPCT',
                       'LESSHSPCT': 'LESHSPCT',
                       'LINGISOPCT': 'LNGISPCT',
                       'UNDER5PCT': 'UNDR5PCT',
                       'OVER64PCT': 'OVR64PCT',
                       'PRE1960PCT': 'LDPNT'
                       },
              inplace=True)
print('Adding variable names to list')
column_list.extend(['MINORPCT', 'LWINCPCT', 'LESHSPCT', 'LNGISPCT', 'UNDR5PCT',
                    'OVR64PCT', 'LDPNT', 'UNEMPPCT', 'DSLPM',
                    'PTRAF', 'PWDIS', 'PNPL', 'PRMP',
                    'PTSDF', 'OZONE', 'PM25', 'UST'])
print('Saving, rereading file')
df_epa.to_csv(epa_csv_temp, index=False)
df_epa = pd.read_csv(epa_csv_temp, sep=",")

print('\nPROCESSING CDC DATA')
print('Reading in csv')
df_cdc = pd.read_csv(cdc_csv,
                     sep=",",
                     usecols=['StateDesc', 'TractFIPS',
                              'CASTHMA_CrudePrev', 'BPHIGH_CrudePrev',
                              'CANCER_CrudePrev', 'DIABETES_CrudePrev',
                              'MHLTH_CrudePrev']
                     )
print("Dropping extra rows")
df_cdc = df_cdc[(df_cdc.StateDesc == "Rhode Island") |
                (df_cdc.StateDesc == "Connecticut") |
                (df_cdc.StateDesc == "Massachusetts")]
print('Renaming columns')
df_cdc.rename(columns={'TractFIPS': 'fips',
                       'CASTHMA_CrudePrev': 'ASTHMA',
                       'BPHIGH_CrudePrev': 'BPHIGH',
                       'CANCER_CrudePrev': 'CANCER',
                       'DIABETES_CrudePrev': 'DIABE',
                       'MHLTH_CrudePrev': 'MHEALTH'
                       },
              inplace=True)
print('Adding variable names to list')
column_list.extend(['ASTHMA', 'BPHIGH', 'CANCER', 'DIABE', 'MHEALTH'])
print('Saving, rereading file')
df_cdc.to_csv(cdc_csv_temp, index=False)
df_cdc = pd.read_csv(cdc_csv_temp, sep=",")

print('\nPROCESSING TREE DATA')
if process_raster_trees is True:
    print('Calculating zonal statistics')
    ZonalStatisticsAsTable(in_zone_data=tracts_state,
                           zone_field='ID',
                           in_value_raster=nlcd_trees_raster,
                           out_table=nlcd_table_trees,
                           statistics_type='MEAN')

    print('Exporting to excel')
    arcpy.conversion.TableToExcel(Input_Table=nlcd_table_trees,
                                  Output_Excel_File=nlcd_trees)
print('Opening excel file')
df_trees = pd.read_excel(nlcd_trees)
print('Adding, adjusting columns')
print('\tAdding column "TREES", setting to MEAN/100')
df_trees['TREES'] = df_trees['MEAN']/100
print('\tDropping extra columns')
df_trees = df_trees[['ID', 'TREES']]
print('Adding variable names to list')
column_list.append('TREES')

print('\nPROCESSING IMPERVIOUS DATA')
if process_raster_impervious is True:
    print('Calculating zonal statistics')
    ZonalStatisticsAsTable(in_zone_data=tracts_state,
                           zone_field='ID',
                           in_value_raster=nlcd_impervious_raster,
                           out_table=nlcd_table_impervious,
                           statistics_type='MEAN')

    print('Exporting to excel')
    arcpy.conversion.TableToExcel(Input_Table=nlcd_table_impervious,
                                  Output_Excel_File=nlcd_impervious)
print('Opening excel file')
df_imper = pd.read_excel(nlcd_impervious)
print('Adding, adjusting columns')
print('\tAdding column "IMPER", setting to MEAN/100')
df_imper['IMPER'] = df_imper['MEAN']/100
print('\tDropping extra columns')
df_imper = df_imper[['ID', 'IMPER']]
print('Adding variable names to list')
column_list.append('IMPER')

print('\nPROCESSING FLOOD DATA')
print('Reading in csv')
df_flood = pd.read_csv(flood_csv, sep=',')
print('Calculating average flood risk')
df_flood['FLOOD'] = (df_flood.count_floodfactor1 + 2*df_flood.count_floodfactor2 +
                     3*df_flood.count_floodfactor3 + 4*df_flood.count_floodfactor4 +
                     5*df_flood.count_floodfactor5 + 6*df_flood.count_floodfactor6 +
                     7*df_flood.count_floodfactor7 + 8*df_flood.count_floodfactor8 +
                     9*df_flood.count_floodfactor9 + 10*df_flood.count_floodfactor10
                     )/df_flood.count_property
print('Dropping extra columns')
df_flood = df_flood[['fips', 'FLOOD']]
print('Adding variable names to list')
column_list.append('FLOOD')

print('\nPROCESSING HEAT DATA')
print('Reading in csv')
df_heat = pd.read_csv(heat_csv, sep=',')
print('Calculating average heat risk')
df_heat['HEAT'] = (df_heat.count_heatfactor1 + 2*df_heat.count_heatfactor2 +
                   3*df_heat.count_heatfactor3 + 4*df_heat.count_heatfactor4 +
                   5*df_heat.count_heatfactor5 + 6*df_heat.count_heatfactor6 +
                   7*df_heat.count_heatfactor7 + 8*df_heat.count_heatfactor8 +
                   9*df_heat.count_heatfactor9 + 10*df_heat.count_heatfactor10
                   )/df_heat.count_property
print('Dropping extra columns')
df_heat = df_heat[['fips', 'HEAT']]
print('Adding variable names to list')
column_list.append('HEAT')

print('\nPROCESSING SEA LEVEL DATA')
for depth in ['1ft', '2ft']:
    if depth == '1ft':
        slr_RI = slr_1ft_RI
        slr_MA = slr_1ft_MA
        slr_CT = slr_1ft_CT
        slr_excel = slr_1ft_excel
    else:
        slr_RI = slr_2ft_RI
        slr_MA = slr_2ft_MA
        slr_CT = slr_2ft_CT
        slr_excel = slr_2ft_excel
    print('Processing data for ' + depth + ' sea level rise')
    print('\tMerging RI, MA, CT data')
    arcpy.management.Merge(inputs=[slr_RI, slr_MA, slr_CT],
                           output=slr_merge)
    print('\tClipping to shoreline')
    arcpy.analysis.Clip(in_features=slr_merge,
                        clip_features=state_polygon,
                        out_feature_class=slr_clip)
    print('\tDissolving data')
    # Ensure one multipart polygon
    arcpy.management.Dissolve(in_features=slr_clip,
                              out_feature_class=slr_dissolve)
    print('\tIntersecting SLR, tracts')
    arcpy.analysis.Intersect(in_features=[tracts_state, slr_dissolve],
                             out_feature_class=slr_intersect)
    print('\tCalculating acres')
    print('\t\tAdding column')
    arcpy.management.AddField(in_table=slr_intersect,
                              field_name='SLR',
                              field_type='FLOAT')
    print('\t\tCalculating geometry')
    arcpy.management.CalculateGeometryAttributes(in_features=slr_intersect,
                                                 geometry_property=[['SLR', 'AREA']],
                                                 area_unit='ACRES')
    print('\tDropping extra fields')
    arcpy.management.DeleteField(in_table=slr_intersect,
                                 drop_field=['ID', 'Acres_Land', 'SLR'],
                                 method='KEEP_FIELDS')
    print('\tExporting data to excel')
    arcpy.conversion.TableToExcel(Input_Table=slr_intersect,
                                  Output_Excel_File=slr_excel)
print('Reading in excel files')
df_slr_1ft = pd.read_excel(slr_1ft_excel)
df_slr_2ft = pd.read_excel(slr_2ft_excel)
print('Adding new temp columns')
df_slr_1ft['SLR_1ft'] = df_slr_1ft['SLR']
df_slr_2ft['SLR_2ft'] = df_slr_2ft['SLR']
print('Merging dataframes')
df_slr = pd.merge(left=df_slr_1ft,
                  right=df_slr_2ft,
                  how='outer',
                  on=['ID', 'Acres_Land'])
print('Setting blank values to 0')
df_slr["SLR_1ft"].fillna(0, inplace=True)
df_slr["SLR_2ft"].fillna(0, inplace=True)
print('Calculating acres inundated for 1.6 ft sea level rise')
df_slr['SLR'] = df_slr['SLR_1ft'] + (df_slr['SLR_2ft']-df_slr['SLR_1ft'])*0.6
print('Converting "acres inundated" to "% land area is inundated"')
df_slr['SLR'] = df_slr['SLR']/df_slr['Acres_Land']
print('Adding variable names to list')
column_list.append('SLR')

print('\nCOMBINING DATA')
print('Merging tables')
# Combine all datasets with baseline tract data
# For regular datasets...
print('\tAdding EPA, tree, impervious, coastal inundation data')
for dataframe in [df_epa, df_trees, df_imper, df_slr]:
    df_tracts = pd.merge(df_tracts, dataframe, on=['ID'], how='left')
# For tract level datasets
print('\tAdding CDC, flood, heat data')
for dataframe in [df_cdc, df_flood, df_heat]:
    df_tracts = pd.merge(df_tracts, dataframe, left_on='tract_ID', right_on='fips', how='left')

print('\nADJUSTING DATA')
print('Setting blank values to 0')
# Due to the way this is calculated earlier, all census blocks where metric=0 have null value
# Null values need to replaced AFTER data is merged with tract data
for metric in ['SLR']:
    print('\tFor ' + metric)
    df_tracts[metric].fillna(0, inplace=True)

print('\nCALCULATING PERCENTILES')
print('Selecting RI tracts')
df_RI = df_tracts.loc[df_tracts['State'] == 'Rhode Island']
print('Selecting CT tracts')
df_CT = df_tracts.loc[df_tracts['State'] == 'Connecticut']
print('Selecting MA tracts')
df_MA = df_tracts.loc[df_tracts['State'] == 'Massachusetts']


print('Selecting NBEP tracts')
df_nbep = df_tracts.loc[df_tracts['Study_Area'].str.contains("Narragansett Bay|"
                                                             "Little Narragansett Bay|"
                                                             "Southwest Coastal Ponds")]

# Calc percentile for each variable
for col in column_list:
    print('Calculating percentiles for ' + col)
    # Set variables
    n_col = 'N_' + col
    p_col = 'P_' + col

    if col == 'TREES':
        pct_ascending = False
    else:
        pct_ascending = True

    print('\tAdding columns')
    df_tracts[['p_temp', p_col, n_col]] = [0, 0, 0]

    # Calc state percentiles...
    state_list = ['Rhode Island', 'Connecticut', 'Massachusetts']
    for state in state_list:
        if state == 'Rhode Island':
            df_temp = df_RI
        elif state == 'Connecticut':
            df_temp = df_CT
        elif state == 'Massachusetts':
            df_temp = df_MA

        print('\tCalculating ' + state + ' percentiles')
        # Calc percentile, assign to p_temp
        df_tracts['p_temp'] = df_temp[col].rank(pct=True,
                                                ascending=pct_ascending)
        # Replace null values
        df_tracts['p_temp'].fillna(0, inplace=True)
        # Multiply by 100, truncate
        df_tracts['p_temp'] = np.trunc(100 * df_tracts['p_temp'])
        # Add to p_col
        df_tracts[p_col] += df_tracts['p_temp']
    print('\tSetting percentile for rows with no data to null')
    df_tracts[p_col] = np.where(df_tracts[col].isnull(), np.nan, df_tracts[p_col])

    print('\tCalculating NBEP percentiles')
    # Add column
    df_tracts[n_col] = 0
    # Calc percentile
    df_tracts[n_col] = df_nbep[col].rank(pct=True,
                                         ascending=pct_ascending)
    # Multiply by 100, truncate
    df_tracts[n_col] = np.trunc(100*df_tracts[n_col])

print('Dropping extra columns')
p_columns = ['P_' + x for x in column_list]
n_columns = ['N_' + x for x in column_list]
# Build list of col
col_list = ['ID', 'State', 'Town', 'ACSTOTPOP'] + column_list + p_columns + n_columns + ['Study_Area']
# Drop all unlisted columns
df_tracts = df_tracts[col_list]

print('Adding new columns')
df_tracts['DataSource'] = 'EPA; CDC; NLCD; NLCD, USFS; RIGIS; First Street; NOAA'
df_tracts['SourceYear'] = '2016-2020, 2022; 2019, 2020; 2019; 2016; 2021; 2022; 2019'
df_tracts['NBEPYear'] = 2022

print("Saving file")
df_tracts.to_csv(output_csv_all,
                 index=False,
                 na_rep='NoData')

print('\nCreating list of NBEP tracts')
print('Exporting NBEP tracts to excel')
arcpy.conversion.TableToExcel(Input_Table=tracts_NBEP,
                              Output_Excel_File=nbep_excel)
print('Opening excel file')
df_clip = pd.read_excel(nbep_excel)
print('Generating list of NBEP tracts')
tract_list = df_clip.ID.tolist()
print('Clipping dataframe to NBEP boundaries')
df_tracts = df_tracts[df_tracts.ID.isin(tract_list)]
print('Saving file')
df_tracts.to_csv(output_csv_NBEP,
                 index=False,
                 na_rep='NoData')

# ---------------------------------------------------------------------------
# Delete extra files
if keep_temp_files is False:
    print("\nDeleting temporary files")
    arcpy.Delete_management(scratchFolder)
    arcpy.Delete_management(nlcd_table_trees)
    arcpy.Delete_management(nlcd_table_impervious)
    print("\tFiles deleted")
