# ---------------------------------------------------------------------------
# ejmap_step1b_NBEP.py
# Authors: Mariel Sorlien
# Last updated: 2023-09-18
# Python 3.7
#
# Description:
# Adds XML metadata. Formatted for NBEP.
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

import arcpy
from arcpy import metadata as md
import os

arcpy.env.overwriteOutput = True

# ------------------------------ STEP 1 -------------------------------------
# Set workspace, projection, initial variables (MANDATORY)

# Set workspace
base_folder = os.getcwd()
scratch_folder = arcpy.env.scratchFolder
gis_folder = base_folder + '/gis_data/int_gisdata/ejmap_intdata.gdb'
csv_folder = base_folder + '/tabular_data/final_data'

# Set default projection
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference('NAD 1983 UTM Zone 19N')

# Set variables
census_year = 2020
NBEP_year = 2023
EPA_agreements = 'CE00A00967'

# Set inputs
gis_input = gis_folder + '/RICTMA_BlockGroups_2020_NBEP2023'
gis_metadata = base_folder + '/metadata_templates/RICTMA_blockgroup_metadata.xml'

# Set outputs
excel_output = csv_folder + '/RICTMA_BlockGroups_2020_NBEP2023.xls'

# ---------------------------- RUN SCRIPT -----------------------------------
# Define additional variables
gis_title = os.path.splitext(os.path.basename(gis_input))[0]

print('Adding column "NBEPYear"')
arcpy.management.AddField(in_table=gis_input,
                          field_name='NBEPYear',
                          field_type='DOUBLE')
arcpy.management.CalculateField(in_table=gis_input,
                                field='NBEPYear',
                                expression=NBEP_year)

print('Generating metadata')
# Create a new Metadata object
new_md = md.Metadata()
# Copy info from template
new_md.importMetadata(gis_metadata)
print('\tTitle')
new_md.title = gis_title
print('\tSummary')
new_md.summary = 'Census block groups for Rhode Island, Massachusetts, and Connecticut as defined by the ' + \
                 str(census_year) + \
                 ' U.S. Census. This data is intended for general planning, graphic display, and GIS analysis.'
print('\tDescription')
# Set description
new_md.description = 'Census block groups for Rhode Island, Massachusetts, and Connecticut as defined by the ' + \
                     str(census_year) + \
                     ' U.S. Census. Census data has been supplemented with town names (RIGIS 2001; MassGIS 2021; ' \
                     'CTDEEP 2005), watersheds (USGS WBD 2023), and NBEP study areas (NBEP 2017). This dataset is ' \
                     'intended for general planning, graphic display, and GIS analysis.'
print('\tConstraints')
# Set constraints
new_md.accessConstraints = 'This dataset is provided "as is". The producer(s) of this dataset, contributors ' \
                           'to this dataset, and the Narragansett Bay Estuary Program (NBEP) do not make any ' \
                           'warranties of any kind for this dataset, and are not liable for any loss or damage ' \
                           'however and whenever caused by any use of this dataset. There are no restrictions or ' \
                           'legal prerequisites for using the data. Once acquired, any modification made to the data ' \
                           'must be noted in the metadata. Please acknowledge both NBEP and the primary producer(s) ' \
                           'of this dataset or any derived products. These data are intended for use as a tool for ' \
                           'reference, display, and general GIS analysis purposes only. It is the responsibility of ' \
                           'the data user to use the data appropriately and consistent with the limitations of ' \
                           'geospatial data in general and these data in particular. The information contained in ' \
                           'these data may be dynamic and could change over time. The data accuracy is checked ' \
                           'against best available sources which may be dated. The data are not better than the ' \
                           'original sources from which they are derived. These data are not designed for use as a ' \
                           'primary regulatory tool in permitting or siting decisions and are not a legally ' \
                           'authoritative source for the location of natural or manmade features. The depicted ' \
                           'boundaries, interpretations, and analysis derived from have not been verified at the ' \
                           'site level them and do not eliminate the need for onsite sampling, testing, and detailed ' \
                           'study of specific sites. This project was funded by agreements by the Environmental ' \
                           'Protection Agency (EPA) to Roger Williams University (RWU) in partnership with the ' \
                           'Narragansett Bay Estuary Program. Although the information in this document has been ' \
                           'funded wholly or in part by EPA under the agreements ' \
                           + EPA_agreements \
                           + ' to RWU, it has not undergone the Agency’s publications review process and therefore, ' \
                           'may not necessarily reflect the views of the Agency and no official endorsement should ' \
                           'be inferred. The viewpoints expressed here do not necessarily represent those of the ' \
                           'Narragansett Bay Estuary Program, RWU, or EPA nor does mention of trade names, ' \
                           'commercial products, or causes constitute endorsement or recommendation for use.'

# Assign the Metadata object's content to a target item
tgt_item_md = md.Metadata(gis_input)
if not tgt_item_md.isReadOnly:
    tgt_item_md.copy(new_md)
    tgt_item_md.save()
else:
    print('\tError: Unable to add metadata')

print('\nExporting data to excel')
# Export shp table to excel
arcpy.conversion.TableToExcel(Input_Table=gis_input,
                              Output_Excel_File=excel_output)

print('\n!!!IMPORTANT!!!')
print('This script updates most metadata fields, but not all. METADATA MUST BE MANUALLY REVIEWED. \nPay particular '
      'attention to following areas: \n\tCITATION (alternate title, date published, edition, other details)'
      '\n\tCONSTRAINTS (use limitations) \n\tEXTENTS (temporal period extent) \n\tLINEAGE (data source, process '
      'step date) \n\tFIELDS (date range)')
