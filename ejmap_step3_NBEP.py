# ---------------------------------------------------------------------------
# ejmap_step3_NBEP.py
# Authors: Mariel Sorlien
# Last updated: 2023-04-21
# Python 3.7
#
# Description:
# Clips data to NBEP towns, adds metadata
# ---------------------------------------------------------------------------

import arcpy
from arcpy import metadata as md
import os
import pandas as pd

arcpy.env.overwriteOutput = True

# ------------------------------ VARIABLES -------------------------------------
# Set workspace, projection, initial variables (MANDATORY)

# Set workspace
base_folder = os.getcwd()
scratch_folder = arcpy.env.scratchFolder
gis_folder = base_folder + '/gis_data/int_gisdata/ejmap_intdata.gdb'
csv_folder = base_folder + '/tabular_data'

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("NAD 1983 UTM Zone 19N")

# Set inputs
gis_block_groups = gis_folder + '/block_groups_fixed'
csv_block_groups = csv_folder + '/block_groups_final.csv'

# Set outputs
gis_output = gis_folder + '/EJMETRICS_2022_NBEP2023'

# Set variables
NBEP_year = 2023
EPA_year = 2022
ACS_year = 2018
EPA_agreements = 'CE00A00967'

# ------------------------------ SCRIPT -------------------------------------
# Define additional variables
gis_temp = arcpy.env.scratchFolder + '/temp_file.shp'

# Run script
print('Listing NBEP towns')
print('Opening csv')
df = pd.read_csv(csv_block_groups, sep=",")
print('Dropping extra columns, rows')
# only keep selected rows
df = df[['State', 'Town', 'Study_Area']]
# drop rows that aren't in Study_Area (and therefor have NaN value)
df_NBEP = df.loc[df['Study_Area'].isin(['Narragansett Bay Watershed', 'Little Narragansett Bay Watershed',
                                        'Southwest Coastal Ponds Watershed'])]
# drop duplicate rows
df_NBEP = df_NBEP.drop_duplicates()
print('Adding column (Town_Code)')
df_NBEP['Town_Code'] = df_NBEP['State'] + df_NBEP['Town']
print('Concatenating list of NBEP towns')
town_list = df_NBEP['Town_Code'].tolist()

print('Copying shapefile')
arcpy.management.CopyFeatures(in_features=gis_block_groups,
                              out_feature_class=gis_temp)
print('Adding fields (Town_Code, NBEPYear)')
arcpy.management.AddFields(gis_temp,
                           [
                               # Field name, field type, field alias, field length, default value
                               ['Town_Code', 'TEXT', 'DataSource', 100],
                               ['NBEPYear', 'SHORT']
                           ])

print('\tCalculating fields')
arcpy.management.CalculateFields(gis_temp,
                                 "PYTHON3",
                                 [
                                     ['Town_Code', '!State! + !Town!'],
                                     ['NBEPYear', NBEP_year]
                                 ])
print('Filtering data for NBEP towns')
arcpy.analysis.Select(in_features=gis_temp,
                      out_feature_class=gis_output,
                      where_clause="Town_Code IN {0}".format(str(tuple(town_list)))
                      )
print('Dropping extra field (Town_Code)')
arcpy.management.DeleteField(in_table=gis_output,
                             drop_field=['Town_Code'])

print('Adding metadata')
# Create a new Metadata object and add some content to it
new_md = md.Metadata()
# Set title
new_md.title = 'EJMETRICS_' + str(EPA_year) + '_NBEP' + str(NBEP_year)
# Set tags
new_md.tags = 'environmental justice, underserved areas, population vulnerability, social vulnerability, ' \
              'environmental risk susceptibility, EJSCREEN, population demographics, people'
# Set summary
new_md.summary = 'Environmental justice metrics in the Narragansett Bay region derived from the ' \
                 'U.S. EPA (EPA) EJSCREEN dataset (EPA 2022). This dataset is intended for general planning, ' \
                 'graphic display, and GIS analysis.'
# Set description
new_md.description = 'Environmental justice metrics in the Narragansett Bay region derived from the ' \
                     'U.S. EPA (EPA) EJSCREEN dataset (EPA ' + str(EPA_year) + \
                     '). EJSCREEN provides population demographics and other information at the U.S. Census ' \
                     '"block group" scale (American Community Survey ' + str(ACS_year) + \
                     '). EJSCREEN data was supplemented with data from the U.S. Center for Disease Control and ' \
                     'Prevention PLACES estimate, the National Landcover Database, the First Street Foundation, ' \
                     'and the National Oceanic and Atmospheric Administration. This data is intended for general ' \
                     'planning, graphic display, and GIS analysis.'
# Set credits
new_md.credits = 'U.S. Environmental Protection Agency Environmental Justice Screening and Mapping Tool (EJSCREEN); ' \
                 'U.S. Center for Disease Control and Prevention PLACES estimate; National Land Cover Database; ' \
                 'First Street Foundation; NOAA; Narragansett Bay Estuary Program'
# Set constraints
new_md.accessConstraints = 'This dataset is provided "as is". The producer(s) of this dataset, contributors ' \
                           'to this dataset, and the Narragansett Bay Estuary Program (NBEP) do not make any ' \
                           'warranties of any kind for this dataset, and are not liable for any loss or damage ' \
                           'however and whenever caused by any use of this dataset. This data is provided under the ' \
                           'Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license. ' \
                           'Once acquired, any modification made to the data must be noted in the metadata. ' \
                           'Please acknowledge both NBEP and the primary producer(s) of this dataset or any ' \
                           'derived products. These data are intended for use as a tool for reference, display, ' \
                           'and general GIS analysis purposes only. It is the responsibility of the data user ' \
                           'to use the data appropriately and consistent with the limitations of geospatial data ' \
                           'in general and these data in particular. The information contained in these data may ' \
                           'be dynamic and could change over time. The data accuracy is checked against best ' \
                           'available sources which may be dated. The data are not better than the original sources ' \
                           'from which they are derived. These data are not designed for use as a primary regulatory ' \
                           'tool in permitting or siting decisions and are not a legally authoritative source for ' \
                           'the location of natural or manmade features. The depicted boundaries, interpretations, ' \
                           'and analysis derived from have not been verified at the site level them and do not ' \
                           'eliminate the need for onsite sampling, testing, and detailed study of specific sites. ' \
                           'This project was funded by agreements by the Environmental Protection Agency (EPA) to ' \
                           'Roger Williams University (RWU) in partnership with the Narragansett Bay Estuary ' \
                           'Program. Although the information in this document has been funded wholly or in part by ' \
                           'EPA under the agreements ' + EPA_agreements + \
                           ' to RWU, it has not undergone the Agency’s publications review process and therefore, ' \
                           'may not necessarily reflect the views of the Agency and no official endorsement should ' \
                           'be inferred. The viewpoints expressed here do not necessarily represent those of the ' \
                           'Narragansett Bay Estuary Program, RWU, or EPA nor does mention of trade names, ' \
                           'commercial products, or causes constitute endorsement or recommendation for use.'

# Assign the Metadata object's content to a target item
tgt_item_md = md.Metadata(gis_output)
if not tgt_item_md.isReadOnly:
    tgt_item_md.copy(new_md)
    tgt_item_md.save()
else:
    print('\tError: Unable to add metadata')

print('Deleting scratch folder')
arcpy.Delete_management(scratch_folder)
