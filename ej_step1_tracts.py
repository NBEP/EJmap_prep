# ---------------------------------------------------------------------------
# ej_step1_tracts
# Created on: 2022-10-24
# Last edited: 2022-12-08
# Authors: Mariel Sorlien
#
# Description:
# Reformat EPA EJscreen data for use in NBEP EJscreen
# Output: 1) csv lists of RI/CT/MA, NBEP census block groups 2) shapefiles of RI/CT/MA, NBEP census block groups
# ---------------------------------------------------------------------------

import arcpy
import os
import pandas as pd

arcpy.env.overwriteOutput = True  # lets you overwrite existing files; does NOT work if files open elsewhere (eg GIS)

# -----------------------
# Set variables ---

# Set default workspace
baseFolder = r"C:\Users\msorlien\OneDrive - NBEP - RWU\Documents\GIS_PROJECTS\INTERNAL_PROJECTS\EJ_map_v2"
gdb_path = baseFolder + r'\Data\INT_GISDATA\ejtools_intdata.gdb'
csv_path = baseFolder + r'\Methods\Data'

# Set folder names
scratchFolder = 'scratch'
outputFolder = 'clipped_data'

# Set input files
epa_tracts = 'source_copy/EJSCREEN_StatePct'
CT_towns = 'source_copy/CT_towns'
MA_towns = 'source_copy/MA_towns'
RI_towns = 'source_copy/RI_towns'
NBEP_boundaries = 'source_copy/NBEP_study_areas'
NBEP_states = 'source_copy/StateLines_Polygon'
NBEP_states_buffer = 'new_data/states_buffer'

# Keep scratch folder?
# True = keep scratch folder, False = delete scratch folder
keep_temp_files = True

# ---------------------------------------------------------------------------
# Additional variables ---
arcpy.env.workspace = gdb_path
csv_scratch = os.path.join(csv_path, scratchFolder)
csv_int = os.path.join(csv_path, 'int_data')

CT_towns_2 = scratchFolder + '/CT_towns_2'

state_tracts = os.path.join(scratchFolder, 'state_tracts')
state_buffer = os.path.join(scratchFolder, 'state_buffer')
state_dissolve = os.path.join(scratchFolder, 'state_dissolve')
state_intersect = os.path.join(scratchFolder, 'state_intersect')

state_boundaries = os.path.join(scratchFolder, 'state_boundaries')
state_tracts_clip = os.path.join(scratchFolder, 'state_tracts_clip')
state_tracts_point = os.path.join(scratchFolder, 'state_tracts_point')
state_tracts_join = os.path.join(scratchFolder, 'state_tracts_join')
state_tracts_towns = os.path.join(scratchFolder, 'state_tracts_towns')
state_tracts_final = os.path.join(outputFolder, 'EJSCREEN_tracts_state')
state_tracts_excel = os.path.join(csv_scratch, 'state_tracts.xls')
state_tracts_csv = os.path.join(csv_int, 'state_tracts.csv')

state_tracts_copy = os.path.join(scratchFolder, 'state_tracts_copy')

nbep_tracts = os.path.join(outputFolder, 'EJSCREEN_tracts_NBEP')
nbep_tracts_excel = os.path.join(csv_scratch, 'nbep_tracts.xls')
nbep_tracts_csv = os.path.join(csv_int, 'nbep_tracts.csv')

# Check for/add missing folders ---
print("Checking file paths")
new_folders = (scratchFolder, outputFolder)

for folder in new_folders:
    if not arcpy.Exists(os.path.join(gdb_path, folder)):
        arcpy.CreateFeatureDataset_management(gdb_path, folder)
        print("\tAdded gdb " + folder + " folder")
if not os.path.exists(csv_scratch):
    os.mkdir(csv_scratch)
    print("\tAdded csv scratch folder")

# ---------------------------------------------------------------------------
# Define functions ---

# ---------------------------------------------------------------------------
# Run Script ---

print('Selecting RI, MA, CT tracts')
arcpy.analysis.Select(in_features=epa_tracts,
                      out_feature_class=state_tracts,
                      where_clause="STATE_NAME = 'Rhode Island' Or "
                                   "STATE_NAME = 'Connecticut' Or "
                                   "STATE_NAME = 'Massachusetts'")

print('Calculating acres')
print('\tAdding column')
arcpy.management.AddField(in_table=state_tracts,
                          field_name='Acres',
                          field_type='FLOAT')
print('\tCalculating geometry')
arcpy.management.CalculateGeometryAttributes(in_features=state_tracts,
                                             geometry_property=[['Acres', 'AREA']],
                                             area_unit='ACRES')

print('Calculating acres land')
print('\tBuffering state boundaries')
# Merge state boundaries with special 'buffer' polygon to catch
# differences in state boundaries between NBEP_states & epa_tracts
arcpy.management.Merge(inputs=[NBEP_states, NBEP_states_buffer],
                       output=state_buffer)
# Dissolve to create single polygon
arcpy.management.Dissolve(in_features=state_buffer,
                          out_feature_class=state_dissolve)
print('\tJoining state boundaries, census tracts')
# Intersect land polygon & tract polygon to clip datat and find land per tract
arcpy.analysis.Intersect(in_features=[state_dissolve, state_tracts],
                         out_feature_class=state_intersect)
print('\tAdding column')
arcpy.management.AddField(in_table=state_intersect,
                          field_name='Acres_Land',
                          field_type='FLOAT')
print('\tCalculating geometry')
arcpy.management.CalculateGeometryAttributes(in_features=state_intersect,
                                             geometry_property=[['Acres_Land', 'AREA']],
                                             area_unit='ACRES')
print('\tJoining fields')
# Match ID fields to attach 'Acres_Land' field to unclipped state_tracts
arcpy.management.JoinField(in_data=state_tracts,
                           in_field='ID',
                           join_table=state_intersect,
                           join_field='ID',
                           fields='Acres_Land')

print('Dropping extra fields')
arcpy.management.DeleteField(in_table=state_tracts,
                             drop_field=['ID', 'STATE_NAME', 'Acres', 'Acres_Land'],
                             method='KEEP_FIELDS')

print('Building RI/CT/MA dataset')
print('\tDropping CT ocean polygon')
arcpy.analysis.Select(in_features=CT_towns,
                      out_feature_class=CT_towns_2,
                      where_clause="TOWN_POLY <> 'Connecticut Waters'")
print('\tJoining RI, CT, MA data')
arcpy.analysis.Union(in_features=[RI_towns, CT_towns_2, MA_towns],
                     out_feature_class=state_boundaries)
print('\tDropping extra fields')
arcpy.management.DeleteField(in_table=state_boundaries,
                             drop_field=['NAME', 'TOWN', 'TOWN_1'],
                             method='KEEP_FIELDS')

print('Adding town data to tracts')
print('\tClipping tracts to state boundaries')
arcpy.analysis.Clip(in_features=state_tracts,
                    clip_features=state_boundaries,
                    out_feature_class=state_tracts_clip)

print('\tConverting to points')
# Spatial Join won't match polygon-to-polygon correctly for this dataset... hence point-to-polygon workaround
arcpy.management.FeatureToPoint(in_features=state_tracts_clip,
                                out_feature_class=state_tracts_point,
                                point_location='INSIDE')

print('\tAdding town data')
arcpy.analysis.SpatialJoin(target_features=state_tracts_point,
                           join_features=state_boundaries,
                           out_feature_class=state_tracts_join)

print('\tMerging point data with tracts')
arcpy.analysis.SpatialJoin(target_features=state_tracts,
                           join_features=state_tracts_join,
                           out_feature_class=state_tracts_towns)


print('Adding NBEP study areas')
arcpy.analysis.SpatialJoin(target_features=state_tracts_towns,
                           join_features=NBEP_boundaries,
                           out_feature_class=state_tracts_final,
                           match_option='LARGEST_OVERLAP')

print('Adding new field (Town_Name)')
arcpy.management.AddField(in_table=state_tracts_final,
                          field_name='Town_Name',
                          field_type='Text',
                          field_length=50)
print('\tAdding data')
codeblock_town = """def townName(state, ct, ma, ri):
    if state == 'Rhode Island':
        return ri.title()
    elif state == 'Massachusetts':
        return ma.title()
    elif state == 'Connecticut':
        return ct"""

arcpy.management.CalculateField(in_table=state_tracts_final,
                                field='Town_Name',
                                expression='townName(!STATE_NAME!, !TOWN_1!, !TOWN!, !NAME!)',
                                code_block=codeblock_town)

print('Dropping extra fields')
arcpy.management.DeleteField(in_table=state_tracts_final,
                             drop_field=['ID', 'STATE_NAME', 'Town_Name',
                                         'Acres', 'Acres_Land', 'Study_Area'],
                             method='KEEP_FIELDS')

print('Exporting data to excel')
arcpy.conversion.TableToExcel(Input_Table=state_tracts_final,
                              Output_Excel_File=state_tracts_excel)

print('\nCreating list of towns in watershed')
print('\tImporting excel file')
df = pd.read_excel(state_tracts_excel)
print('\tDropping extra columns, rows')
# only keep selected rows
df = df[['STATE_NAME', 'Town_Name', 'Study_Area']]
# drop rows that aren't in Study_Area (and therefor have NaN value)
df = df.dropna()
# drop duplicate rows
df = df.drop_duplicates()
print('\tAdding column')
df['Town_Code'] = df['STATE_NAME'] + df['Town_Name']
print('\tConcatenating list')
town_list = df['Town_Code'].tolist()

print('\nSelecting NBEP tracts')
print('\tCreating copy of State_Tracts')
arcpy.management.CopyFeatures(state_tracts_final,
                              state_tracts_copy)
print('\tAdding new field (Town_Code)')
arcpy.management.AddField(in_table=state_tracts_copy,
                          field_name='Town_Code',
                          field_type='Text',
                          field_length=70)
arcpy.management.CalculateField(in_table=state_tracts_copy,
                                field='Town_Code',
                                expression='!STATE_NAME! + !Town_Name!')
print('\tSelecting tracts')
arcpy.analysis.Select(in_features=state_tracts_copy,
                      out_feature_class=nbep_tracts,
                      where_clause="Town_Code IN {0} And ID <> '440059900000'".format(str(tuple(town_list)))
                      )
print('\tDropping extra column (Town_Code)')
arcpy.management.DeleteField(in_table=nbep_tracts,
                             drop_field=['Town_Code'])
print('Exporting data to excel')
arcpy.conversion.TableToExcel(Input_Table=nbep_tracts,
                              Output_Excel_File=nbep_tracts_excel)

print('\nConverting excel files to csv')
excel_list = [state_tracts_excel, nbep_tracts_excel]
for excel in excel_list:
    if excel == state_tracts_excel:
        file_type = 'state tracts'
        csv_output = state_tracts_csv
    else:
        file_type = 'NBEP tracts'
        csv_output = nbep_tracts_csv
    print('Opening ' + file_type + ' as dataframe')
    df_tracts = pd.read_excel(excel)

    print('\tReplacing null values')
    df_tracts['Study_Area'].fillna('Outside Study Area', inplace=True)

    print('\tDropping extra columns')
    df_tracts = df_tracts[['ID', 'STATE_NAME', 'Town_Name', 'Acres', 'Acres_Land', 'Study_Area']]

    print('\tRenaming columns')
    df_tracts.rename(columns={'STATE_NAME': 'State',
                              'Town_Name': 'Town'},
                     inplace=True)

    print('\tSaving as csv')
    df_tracts.to_csv(csv_output, index=False)

# ---------------------------------------------------------------------------
# Delete extra files
if keep_temp_files is False:
    print("\nDeleting temporary files")
    arcpy.Delete_management(scratchFolder)
    print("\tFiles deleted")
