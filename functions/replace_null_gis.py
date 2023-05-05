# ---------------------------------------------------------------------------
# fun_block_groups.py
# Authors: Mariel Sorlien
# Last updated: 2023-05-05
# Python 3.7
#
# Description: Replace null values
# ---------------------------------------------------------------------------

import arcpy


def replace_null_in_field(in_table, fields, new_text):

    print('Replacing null values with "' + new_text + '"')
    for field in fields:
        print('\tUpdating ' + field)
        with arcpy.da.UpdateCursor(in_table, field) as cursor:
            for row in cursor:
                if row[0] is None or row[0] == '' or row[0] == ' ':
                    row[0] = new_text
                cursor.updateRow(row)
