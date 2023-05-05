# ---------------------------------------------------------------------------
# fun_block_groups.py
# Authors: Mariel Sorlien
# Last updated: 2023-05-04
# Python 3.7
#
# Description: Joins additional dataset to block group data, saves file to scratch folder
# ---------------------------------------------------------------------------

import arcpy


def block_group_spatial_join(target_features, join_features, concatenate_fields, output_features):
    gis_temp = arcpy.env.scratchFolder + '/blockgroup_join.shp'

    # Make field map
    fieldmap = arcpy.FieldMappings()
    fieldmap.addTable(target_features)
    fieldmap.addTable(join_features)

    # Update field map to concatenate strings for selected fields
    if concatenate_fields != '':
        for x in concatenate_fields:
            oldfieldmap = fieldmap.findFieldMapIndex(x)
            newfieldmap = fieldmap.getFieldMap(oldfieldmap)
            newfieldmap.mergeRule = 'join'
            newfieldmap.joinDelimiter = '; '

            newfield = newfieldmap.outputField
            newfield.length = 1000
            newfieldmap.outputField = newfield

            fieldmap.replaceFieldMap(oldfieldmap, newfieldmap)

    # Set join type
    join_type = 'LARGEST_OVERLAP'
    if concatenate_fields != '':
        join_type = 'INTERSECT'

    print('Adding spatial join')
    arcpy.analysis.SpatialJoin(
        target_features=target_features,
        join_features=join_features,
        out_feature_class=gis_temp,
        field_mapping=fieldmap,
        match_option=join_type
    )

    print('Saving data')
    arcpy.management.CopyFeatures(
        in_features=gis_temp,
        out_feature_class=output_features
    )
