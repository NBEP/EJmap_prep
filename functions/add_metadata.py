# ---------------------------------------------------------------------------
# add_NBEP_columns
# Last updated: 2022-04-19
# Authors: Mariel Sorlien
#
# Description:
# Arcpy script that adds standard metadata columns (DataSource, SourceYear) to a shapefile
# ---------------------------------------------------------------------------

import arcpy

# Variables
# table_name = input table
# data_source = generally the organization, sometimes a journal citation
# source_year = year of source dataset


def add_metadata_fields(table_name, data_source, source_year):

    len_data_source = len(data_source) + 5 if len(data_source) > 30 else 30
    len_source_year = len(source_year) + 5 if len(source_year) > 30 else 30

    arcpy.management.AddFields(table_name,
                               [
                                   # Field name, field type, field alias, field length, default value
                                   ['DataSource', 'TEXT', 'DataSource', len_data_source],
                                   ['SourceYear', 'TEXT', 'SourceYear', len_source_year]
                               ])
    arcpy.management.CalculateFields(table_name,
                                     "PYTHON3",
                                     [
                                         ['DataSource', '"' + data_source + '"'],
                                         ['SourceYear', '"' + source_year + '"']
                                     ])
